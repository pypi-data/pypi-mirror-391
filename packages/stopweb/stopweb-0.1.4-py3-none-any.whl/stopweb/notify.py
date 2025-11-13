"""
Notification and audit helpers for StopWeb.

- Detect manual changes in hosts file (removals or modifications of StopWeb lines)
- Send email notifications using SMTP if configured; otherwise write to outbox
"""

from __future__ import annotations

import socket
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, List, Tuple

from .config import StopWebConfig


def _filter_stopweb_lines(lines: List[str], marker: str) -> List[str]:
    return [ln.rstrip("\n") for ln in lines if marker in ln]


def _domain_from_line(line: str) -> str:
    # Expect format: "127.0.0.1    domain    # StopWeb: ..."
    try:
        parts = line.split()
        return parts[1]
    except Exception:
        return ""


def compute_changes(prev_lines: List[str], curr_lines: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """Compute manual changes between two snapshots of StopWeb-managed lines.

    Returns dict with keys:
      - removed: list of (domain, old_line)
      - modified: list of (domain, new_line)
    Additions are intentionally ignored.
    """
    prev_by_domain: Dict[str, str] = { _domain_from_line(line): line for line in prev_lines if _domain_from_line(line) }
    curr_by_domain: Dict[str, str] = { _domain_from_line(line): line for line in curr_lines if _domain_from_line(line) }

    removed: List[Tuple[str, str]] = []
    modified: List[Tuple[str, str]] = []

    for dom, old_line in prev_by_domain.items():
        if dom not in curr_by_domain:
            removed.append((dom, old_line))
        else:
            new_line = curr_by_domain[dom]
            if new_line != old_line:
                modified.append((dom, new_line))

    return { 'removed': removed, 'modified': modified }


class NotificationManager:
    def __init__(self, config: StopWebConfig):
        self.config = config
        self.outbox_dir: Path = self.config._get_config_dir() / "outbox"
        self.outbox_dir.mkdir(parents=True, exist_ok=True)

    def check_and_notify(self, hosts_manager) -> Dict[str, int]:
        """Compare current hosts StopWeb lines with last snapshot and notify if manual changes.

        Does not update the snapshot; callers should update snapshot at the end of their operation.
        Returns counts for reporting.
        """
        marker = hosts_manager.stopweb_marker
        prev_lines = self.config.get_hosts_snapshot()
        curr_lines = _filter_stopweb_lines(hosts_manager.read_hosts_file(), marker)
        diffs = compute_changes(prev_lines, curr_lines)

        removed_cnt = len(diffs['removed'])
        modified_cnt = len(diffs['modified'])

        notifications = self.config.get_notifications()
        if notifications.get('enabled', True) and (removed_cnt or modified_cnt):
            try:
                self._send_email_report(diffs)
            except Exception:
                # As a fallback, write to outbox file
                self._write_outbox(diffs)
        return { 'removed': removed_cnt, 'modified': modified_cnt }

    def _compose_subject(self, removed_cnt: int, modified_cnt: int) -> str:
        host = socket.gethostname()
        return f"StopWeb alert on {host}: {removed_cnt} removed, {modified_cnt} modified"

    def _format_diff_text(self, diffs: Dict[str, List[Tuple[str, str]]]) -> str:
        lines: List[str] = []
        lines.append(f"Time: {datetime.now().isoformat()}")
        lines.append("")
        if diffs['removed']:
            lines.append("Removed entries:")
            for dom, old in diffs['removed']:
                lines.append(f"  - {dom}\n    old: {old}")
            lines.append("")
        if diffs['modified']:
            lines.append("Modified entries:")
            for dom, new in diffs['modified']:
                lines.append(f"  - {dom}\n    new: {new}")
            lines.append("")
        return "\n".join(lines).strip() or "(no changes)"

    def _send_email_report(self, diffs: Dict[str, List[Tuple[str, str]]]):
        notifications = self.config.get_notifications()
        email_to = notifications.get('email_to')
        smtp = notifications.get('smtp', {})
        subject = self._compose_subject(len(diffs['removed']), len(diffs['modified']))
        body = self._format_diff_text(diffs)

        # If SMTP not configured, fallback to outbox
        if not smtp.get('host'):
            self._write_outbox(diffs)
            return

        # Support both single email string or list of emails
        if isinstance(email_to, str):
            recipients = [email_to]
        elif isinstance(email_to, list):
            recipients = email_to
        else:
            recipients = []

        if not recipients:
            self._write_outbox(diffs)
            return

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp.get('user') or f"stopweb@{socket.gethostname()}"
        msg['To'] = ', '.join(recipients)
        msg.set_content(body)

        import smtplib
        host = smtp.get('host')
        port = int(smtp.get('port', 587))
        use_tls = bool(smtp.get('use_tls', True))
        user = smtp.get('user')
        password = smtp.get('password')

        if use_tls:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)

    def _write_outbox(self, diffs: Dict[str, List[Tuple[str, str]]]):
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        subject = self._compose_subject(len(diffs['removed']), len(diffs['modified']))
        body = self._format_diff_text(diffs)
        path = self.outbox_dir / f"{ts}-notification.txt"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(subject + "\n\n" + body + "\n")


def update_snapshot_from_hosts(config: StopWebConfig, hosts_manager) -> None:
    """Utility to persist the current StopWeb-managed lines as the latest snapshot."""
    marker = hosts_manager.stopweb_marker
    curr_lines = _filter_stopweb_lines(hosts_manager.read_hosts_file(), marker)
    config.save_hosts_snapshot(curr_lines)
