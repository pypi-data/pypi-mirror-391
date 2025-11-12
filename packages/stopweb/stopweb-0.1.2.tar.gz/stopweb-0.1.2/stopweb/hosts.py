"""
Hosts file management for blocking websites
"""

import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


class HostsManager:
    """Manages the system hosts file for website blocking"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.hosts_path = self._get_hosts_path()
        self.backup_path = self._get_backup_path()
        # Marker prefix used to identify entries we manage. We may append metadata after this.
        self.stopweb_marker = "# StopWeb:"
        
    def _get_hosts_path(self) -> Path:
        """Get the path to the system hosts file.

        Honors STOPWEB_HOSTS_PATH env var for testing/override.
        """
        import os
        override = os.environ.get("STOPWEB_HOSTS_PATH")
        if override:
            return Path(override)
        if self.system == "windows":
            return Path("C:/Windows/System32/drivers/etc/hosts")
        else:  # macOS and Linux
            return Path("/etc/hosts")
    
    def _get_backup_path(self) -> Path:
        """Get the path for hosts file backup"""
        return self.hosts_path.with_suffix('.stopweb_backup')
    
    def _requires_sudo(self) -> bool:
        """Check if we need sudo privileges"""
        return self.system != "windows"
    
    def backup_hosts_file(self) -> bool:
        """Create a backup of the hosts file"""
        try:
            if not self.backup_path.exists():
                shutil.copy2(self.hosts_path, self.backup_path)
            return True
        except (PermissionError, FileNotFoundError) as e:
            print(f"❌ Failed to backup hosts file: {e}")
            return False
    
    def read_hosts_file(self) -> List[str]:
        """Read all lines from the hosts file"""
        try:
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except (PermissionError, FileNotFoundError) as e:
            print(f"❌ Failed to read hosts file: {e}")
            return []
    
    def write_hosts_file(self, lines: List[str]) -> bool:
        """Write lines to the hosts file"""
        try:
            # Create backup first
            if not self.backup_hosts_file():
                return False
            
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except PermissionError:
            print(f"❌ Permission denied. Please run with {'administrator privileges' if self.system == 'windows' else 'sudo'}")
            return False
        except Exception as e:
            print(f"❌ Failed to write hosts file: {e}")
            return False
    
    def add_blocked_site(self, domain: str, expires_at: Optional[datetime] = None) -> bool:
        """Block a site by adding it to the hosts file.

        If expires_at is provided, the block is temporary and will be cleaned up by
        cleanup_expired_sites(). If not provided, the block is permanent until removed.
        """
        lines = self.read_hosts_file()
        if not lines:
            return False
        # Remove existing entry for this domain (both www and non-www)
        root_domain = domain.replace('www.', '')
        lines = [line for line in lines if not (
            self.stopweb_marker in line and (
                f"    {root_domain}    " in line or f"    www.{root_domain}    " in line
            )
        )]
        # Build marker (optionally with expiry metadata)
        if expires_at is not None:
            marker = f"{self.stopweb_marker} expires={expires_at.isoformat()}"
        else:
            marker = self.stopweb_marker

        # Add new blocking entries for both root and www versions
        lines.append(f"127.0.0.1    {root_domain}    {marker}\n")
        lines.append(f"127.0.0.1    www.{root_domain}    {marker}\n")
        return self.write_hosts_file(lines)
    
    def remove_blocked_site(self, domain: str) -> bool:
        """Remove a blocked site from the hosts file"""
        lines = self.read_hosts_file()
        if not lines:
            return False
        
        # Remove entries for this domain (both www and non-www)
        original_count = len(lines)
        lines = [line for line in lines if not (
            self.stopweb_marker in line and (
                f"    {domain}    " in line or
                f"    www.{domain}    " in line or
                f"    {domain.replace('www.', '')}    " in line
            )
        )]
        
        if len(lines) < original_count:
            return self.write_hosts_file(lines)
        
        return True  # No entries found to remove
    
    def _parse_expires_from_marker(self, line: str) -> Optional[datetime]:
        """Parse an expires=... ISO timestamp from the marker, if present."""
        if self.stopweb_marker not in line:
            return None
        try:
            comment = line.split(self.stopweb_marker, 1)[1]
            comment = comment.strip()
            # comment may be like: "expires=2025-11-04T13:45:00"
            if comment.startswith("expires="):
                iso_str = comment.split("=", 1)[1].strip()
                # Some editors may have trailing spaces
                iso_str = iso_str.strip()
                return datetime.fromisoformat(iso_str)
        except Exception:
            return None
        return None

    def get_blocked_sites(self) -> List[Tuple[str, Optional[datetime]]]:
        """Get list of currently blocked sites as (domain, expires_at) tuples.

        expires_at is None for permanent blocks.
        """
        lines = self.read_hosts_file()
        blocked_sites: List[Tuple[str, Optional[datetime]]] = []
        for line in lines:
            if self.stopweb_marker in line:
                try:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        domain = parts[1]
                        expires_at = self._parse_expires_from_marker(line)
                        blocked_sites.append((domain, expires_at))
                except (ValueError, IndexError):
                    continue
        return blocked_sites
    
    def cleanup_expired_sites(self) -> int:
        """Remove expired temporary blocks from the hosts file.

        Returns number of entries removed.
        """
        lines = self.read_hosts_file()
        if not lines:
            return 0

        now = datetime.now()
        new_lines: List[str] = []
        removed = 0
        for line in lines:
            if self.stopweb_marker in line:
                expires_at = self._parse_expires_from_marker(line)
                if expires_at is not None and expires_at <= now:
                    # Skip this expired line (remove)
                    removed += 1
                    continue
            new_lines.append(line)

        if removed > 0:
            self.write_hosts_file(new_lines)
        return removed
    
    def remove_all_blocked_sites(self) -> int:
        """Remove all StopWeb blocked sites, return count of removed sites"""
        lines = self.read_hosts_file()
        if not lines:
            return 0
        
        original_count = len(lines)
        lines = [line for line in lines if self.stopweb_marker not in line]
        removed_count = original_count - len(lines)
        
        if removed_count > 0:
            self.write_hosts_file(lines)
        
        return removed_count
    
    def check_permissions(self) -> bool:
        """Check if we have permission to modify hosts file"""
        try:
            # Try to read the hosts file
            with open(self.hosts_path, 'r') as _:
                pass
            
            # Try to write (append mode to avoid damaging the file)
            with open(self.hosts_path, 'a') as _:
                pass
            
            return True
        except PermissionError:
            return False
        except FileNotFoundError:
            return False


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    # Remove protocol if present
    if url.startswith(('http://', 'https://')):
        url = url.split('://', 1)[1]
    
    # Remove path if present
    if '/' in url:
        url = url.split('/', 1)[0]
    
    # Remove port if present
    if ':' in url:
        url = url.split(':', 1)[0]
    
    return url.lower().strip()