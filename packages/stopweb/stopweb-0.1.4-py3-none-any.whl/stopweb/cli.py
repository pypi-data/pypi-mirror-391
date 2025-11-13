"""
Command-line interface for StopWeb
"""

import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .hosts import HostsManager, get_domain_from_url
from .config import StopWebConfig
from .notify import NotificationManager, update_snapshot_from_hosts
from typing import cast
from .duration import TimeManager, get_supported_duration_formats


console = Console()


@click.group(invoke_without_command=True)
@click.option('--duration', '-d', help='Optional block duration (e.g., 2h, 1d, 1w). Default: permanent')
@click.option('--list', '-l', 'list_sites', is_flag=True, help='List blocked sites')
@click.option('--remove', '-r', help='Remove blocked site')
@click.option('--clear', is_flag=True, help='Remove all blocked sites')
@click.option('--cleanup', is_flag=True, help='Remove expired blocks')
@click.option('--audit', is_flag=True, help='Run a one-time audit of manual hosts changes (removed/modified StopWeb entries)')
@click.option('--watch', is_flag=True, help='Continuously watch for manual changes and notify')
@click.option('--interval', type=int, default=30, show_default=True, help='Polling interval (seconds) for --watch')
@click.option('--config-email', is_flag=True, help='Configure email notifications')
@click.option('--install-service', is_flag=True, help='Install auto-start monitoring service')
@click.option('--uninstall-service', is_flag=True, help='Uninstall auto-start monitoring service')
@click.argument('websites', nargs=-1)
@click.pass_context
def main(ctx, duration: Optional[str], list_sites: bool, remove: Optional[str], 
         clear: bool, cleanup: bool, audit: bool, watch: bool, interval: int,
         config_email: bool, install_service: bool, uninstall_service: bool, websites: tuple):
    """
        StopWeb - Block websites to stay focused
    
    Examples:
            stopweb facebook.com youtube.com         # Block permanently (default)
            stopweb -d 2h reddit.com                 # Block for 2 hours
      stopweb --list                           # List blocked sites
      stopweb --remove facebook.com            # Unblock a site
      stopweb --clear                          # Remove all blocks
    """
    
    hosts_manager = HostsManager()
    config = StopWebConfig()
    notifier = NotificationManager(config)
    
    # Check permissions only for operations that modify hosts file
    requires_write = cleanup or clear or bool(remove) or bool(websites)
    if requires_write and not hosts_manager.check_permissions():
        console.print("❌ [red]Permission denied![/red]")
        if hosts_manager._requires_sudo():
            console.print("💡 [yellow]Please run with sudo privileges:[/yellow]")
            console.print(f"   [cyan]sudo {' '.join(sys.argv)}[/cyan]")
        else:
            console.print("💡 [yellow]Please run as administrator[/yellow]")
        sys.exit(1)
    
    # Before doing anything, detect any manual changes since last run and notify
    try:
        notifier.check_and_notify(hosts_manager)
    except Exception:
        # Non-fatal: continue CLI even if notification fails
        pass

    # Handle different operations
    if config_email:
        handle_config_email(config)
        return

    if install_service:
        handle_install_service(interval)
        return

    if uninstall_service:
        handle_uninstall_service()
        return

    if audit:
        run_audit(notifier, hosts_manager, config)
        return

    if watch:
        run_watch(notifier, hosts_manager, config, interval)
        return
    if cleanup:
        handle_cleanup(hosts_manager)
        # update snapshot after changes
        update_snapshot_from_hosts(config, hosts_manager)
        return
    
    if clear:
        handle_clear(hosts_manager)
        update_snapshot_from_hosts(config, hosts_manager)
        return
    
    if remove:
        handle_remove(hosts_manager, remove)
        update_snapshot_from_hosts(config, hosts_manager)
        return
    
    if list_sites:
        handle_list(hosts_manager)
        # keep snapshot in sync even on read-only operations
        update_snapshot_from_hosts(config, hosts_manager)
        return
    
    if websites:
        handle_block(hosts_manager, websites, duration)
        update_snapshot_from_hosts(config, hosts_manager)
        return
    
    # No arguments provided, show help
    if ctx.invoked_subcommand is None:
        show_welcome()
        # sync snapshot on idle run
        try:
            update_snapshot_from_hosts(config, hosts_manager)
        except Exception:
            pass
        ctx.get_help()


def handle_block(hosts_manager: HostsManager, websites: tuple, duration: Optional[str]):
    """Handle blocking websites.

    Default is permanent; if duration is provided, create a temporary block.
    """
    time_mgr = TimeManager()
    success_count = 0
    failed_sites = []
    # Precompute expires_at if a single duration applies to all
    expires_at: Optional[datetime] = None
    if duration:
        try:
            expires_at = time_mgr.calculate_expires_at(duration)
        except ValueError:
            console.print(f"❌ [red]Invalid duration:[/red] {duration}")
            console.print(get_supported_duration_formats())
            return
    for website in websites:
        domain = get_domain_from_url(website)
        if hosts_manager.add_blocked_site(domain, expires_at=expires_at):
            success_count += 1
            if expires_at is None:
                console.print(f"✅ [green]Blocked[/green] {domain} [dim](permanent)[/dim]")
            else:
                left = time_mgr.format_time_remaining(expires_at)
                console.print(f"✅ [green]Blocked[/green] {domain} [dim](expires {left})[/dim]")
        else:
            failed_sites.append(domain)
            console.print(f"❌ [red]Failed to block[/red] {domain}")
    if success_count > 0:
        console.print(f"\n🎯 [bold green]Successfully blocked {success_count} site(s)[/bold green]")
        console.print("\n💡 [dim]Note: You may need to clear your browser cache or restart your browser for immediate effect.[/dim]")
    if failed_sites:
        console.print(f"\n⚠️  [yellow]Failed to block:[/yellow] {', '.join(failed_sites)}")


def handle_list(hosts_manager: HostsManager):
    """Handle listing blocked sites (permanent and temporary)"""
    blocked_sites = hosts_manager.get_blocked_sites()
    if not blocked_sites:
        console.print("📭 [yellow]No sites are currently blocked[/yellow]")
        return
    table = Table(title="🚫 Blocked Websites")
    table.add_column("Website", style="cyan", no_wrap=True)
    table.add_column("Expires", style="magenta")
    tm = TimeManager()
    for domain, expires_at in blocked_sites:
        if expires_at is None:
            exp_str = "Permanent"
        else:
            exp_str = tm.format_time_remaining(expires_at)
        table.add_row(domain, exp_str)
    console.print(table)
    console.print(f"\n📊 [bold]{len(blocked_sites)} blocked site(s)[/bold]")


def handle_remove(hosts_manager: HostsManager, domain: str):
    """Handle removing a blocked site"""
    domain = get_domain_from_url(domain)
    
    if hosts_manager.remove_blocked_site(domain):
        console.print(f"✅ [green]Unblocked[/green] {domain}")
        console.print("💡 [dim]You may need to clear your browser cache for immediate effect.[/dim]")
    else:
        console.print(f"❌ [red]Failed to unblock[/red] {domain}")


def handle_clear(hosts_manager: HostsManager):
    """Handle clearing all blocked sites"""
    removed_count = hosts_manager.remove_all_blocked_sites()
    
    if removed_count > 0:
        console.print(f"✅ [green]Removed {removed_count} blocked site(s)[/green]")
        console.print("💡 [dim]You may need to clear your browser cache for immediate effect.[/dim]")
    else:
        console.print("📭 [yellow]No blocked sites found[/yellow]")


def handle_cleanup(hosts_manager: HostsManager):
    """Handle cleaning up expired temporary blocks"""
    removed_count = hosts_manager.cleanup_expired_sites()
    
    if removed_count > 0:
        console.print(f"🧹 [green]Cleaned up {removed_count} expired block(s)[/green]")
    else:
        console.print("✨ [yellow]No expired blocks found[/yellow]")


def show_welcome():
    """Show welcome message"""
    welcome_text = Text("StopWeb", style="bold blue")
    subtitle = Text("Block websites temporarily to stay focused", style="dim")
    
    panel = Panel.fit(
        f"{welcome_text}\n{subtitle}",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()


def run_audit(notifier: NotificationManager, hosts_manager: HostsManager, config: StopWebConfig):
    """Perform a single audit and display counts."""
    counts = notifier.check_and_notify(hosts_manager)
    console.print(f"🔍 Audit: removed={counts['removed']}, modified={counts['modified']}")
    update_snapshot_from_hosts(config, hosts_manager)


def run_watch(notifier: NotificationManager, hosts_manager: HostsManager, config: StopWebConfig, interval: int):
    """Continuously watch hosts file for manual changes."""
    import time
    console.print(f"👀 Watching for manual changes every {interval}s. Press Ctrl+C to stop.")
    try:
        while True:
            counts = notifier.check_and_notify(hosts_manager)
            if counts['removed'] or counts['modified']:
                console.print(f"🔔 Change detected: removed={counts['removed']}, modified={counts['modified']}")
                # update baseline so we don't re-notify the same change
                update_snapshot_from_hosts(config, hosts_manager)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("👋 Watch stopped.")


def handle_config_email(config: StopWebConfig):
    """Interactive email configuration."""
    console.print(Panel("📧 Email Notification Configuration", style="bold blue"))
    
    # Get current settings
    notifications = config.get_notifications()
    current_email = notifications.get('email_to', [])
    if isinstance(current_email, str):
        current_email = [current_email]
    
    smtp = notifications.get('smtp', {})
    
    console.print(f"\n[dim]Current recipients: {', '.join(current_email) if current_email else 'None'}[/dim]")
    console.print(f"[dim]Current SMTP host: {smtp.get('host', 'Not configured')}[/dim]\n")
    
    # Email recipients
    emails_input = click.prompt("📮 Email recipients (comma-separated)", 
                                default=', '.join(current_email) if current_email else '')
    recipients = [e.strip() for e in emails_input.split(',') if e.strip()]
    
    # SMTP settings
    console.print("\n[bold]SMTP Settings:[/bold]")
    console.print("[dim]Common providers:[/dim]")
    console.print("  Gmail: smtp.gmail.com")
    console.print("  Outlook/O365: smtp.office365.com")
    console.print("  Yahoo: smtp.mail.yahoo.com\n")
    
    smtp_host = click.prompt("🌐 SMTP host", default=smtp.get('host', 'smtp.gmail.com'))
    smtp_port = click.prompt("🔌 SMTP port", default=smtp.get('port', 587), type=int)
    smtp_user = click.prompt("👤 SMTP username/email", default=smtp.get('user', recipients[0] if recipients else ''))
    smtp_password = click.prompt("🔑 SMTP password (app-specific password for Gmail)", 
                                 default=smtp.get('password', ''), hide_input=True)
    use_tls = click.confirm("🔒 Use TLS?", default=smtp.get('use_tls', True))
    
    # Save configuration
    config_data = config.load_config()
    if 'settings' not in config_data:
        config_data['settings'] = {}
    if 'notifications' not in config_data['settings']:
        config_data['settings']['notifications'] = {}
    
    config_data['settings']['notifications']['enabled'] = True
    config_data['settings']['notifications']['email_to'] = recipients
    config_data['settings']['notifications']['smtp'] = {
        'host': smtp_host,
        'port': smtp_port,
        'user': smtp_user,
        'password': smtp_password,
        'use_tls': use_tls
    }
    
    config.save_config(config_data)
    
    console.print("\n✅ [green]Email configuration saved![/green]")
    console.print(f"📧 Recipients: {', '.join(recipients)}")
    console.print(f"🌐 SMTP: {smtp_user}@{smtp_host}:{smtp_port}")
    
    # Test email
    if click.confirm("\n📤 Send test email?", default=True):
        try:
            import smtplib
            from email.message import EmailMessage
            import socket
            
            msg = EmailMessage()
            msg['Subject'] = f"StopWeb Test - {socket.gethostname()}"
            msg['From'] = smtp_user
            msg['To'] = ', '.join(recipients)
            msg.set_content("Test email from StopWeb.\n\nIf you received this, email notifications are configured correctly!")
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            console.print("✅ [green]Test email sent successfully![/green]")
        except Exception as e:
            console.print(f"❌ [red]Failed to send test email: {e}[/red]")


def handle_install_service(interval: int):
    """Install auto-start monitoring service."""
    import platform
    import shutil
    import os
    import subprocess
    
    system = platform.system().lower()
    stopweb_path = shutil.which('stopweb') or sys.argv[0]
    
    console.print(Panel("🚀 Install Auto-Start Monitoring Service", style="bold blue"))
    
    if system == 'darwin':  # macOS
        plist_path = '/Library/LaunchDaemons/com.stopweb.watch.plist'
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stopweb.watch</string>
    <key>ProgramArguments</key>
    <array>
        <string>{stopweb_path}</string>
        <string>--watch</string>
        <string>--interval</string>
        <string>{interval}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/stopweb-watch.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/stopweb-watch.log</string>
</dict>
</plist>'''
        
        console.print(f"\n📝 Creating launchd service at: {plist_path}")
        console.print(f"📍 StopWeb path: {stopweb_path}")
        console.print(f"⏱️  Interval: {interval} seconds")
        
        try:
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            os.system(f'launchctl load {plist_path}')
            console.print(f"\n✅ [green]Service installed successfully![/green]")
            console.print(f"📋 Service will start on boot and monitor hosts every {interval}s")
            console.print(f"📄 Log file: /tmp/stopweb-watch.log")
            console.print(f"\n[dim]To uninstall: stopweb --uninstall-service[/dim]")
        except PermissionError:
            console.print("\n❌ [red]Permission denied. Please run with sudo:[/red]")
            console.print(f"   [cyan]sudo stopweb --install-service[/cyan]")
        except Exception as e:
            console.print(f"\n❌ [red]Installation failed: {e}[/red]")
    
    elif system == 'windows':
        console.print("\n📝 Creating Windows Task Scheduler task...")
        console.print(f"📍 StopWeb path: {stopweb_path}")
        console.print(f"⏱️  Interval: {interval} seconds")
        
        ps_script = f'''
$action = New-ScheduledTaskAction -Execute "{stopweb_path}" -Argument "--watch --interval {interval}"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "StopWeb Monitor" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Monitor hosts file for unauthorized changes" `
    -Force
'''
        
        try:
            import subprocess
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                    capture_output=True, text=True, check=True)
            console.print(f"\n✅ [green]Service installed successfully![/green]")
            console.print(f"📋 Task 'StopWeb Monitor' will start on boot")
            console.print(f"\n[dim]To uninstall: stopweb --uninstall-service[/dim]")
        except subprocess.CalledProcessError as e:
            console.print(f"\n❌ [red]Installation failed: {e.stderr}[/red]")
            console.print("\n💡 [yellow]Please run as Administrator[/yellow]")
        except Exception as e:
            console.print(f"\n❌ [red]Installation failed: {e}[/red]")
    
    else:  # Linux
        service_content = f'''[Unit]
Description=StopWeb Monitor
After=network.target

[Service]
Type=simple
ExecStart={stopweb_path} --watch --interval {interval}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
        
        service_path = '/etc/systemd/system/stopweb-monitor.service'
        console.print(f"\n📝 Creating systemd service at: {service_path}")
        console.print(f"📍 StopWeb path: {stopweb_path}")
        console.print(f"⏱️  Interval: {interval} seconds")
        
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            os.system('systemctl daemon-reload')
            os.system('systemctl enable stopweb-monitor')
            os.system('systemctl start stopweb-monitor')
            
            console.print(f"\n✅ [green]Service installed successfully![/green]")
            console.print(f"📋 Service will start on boot and monitor hosts every {interval}s")
            console.print(f"\n[dim]To uninstall: stopweb --uninstall-service[/dim]")
        except PermissionError:
            console.print("\n❌ [red]Permission denied. Please run with sudo:[/red]")
            console.print(f"   [cyan]sudo stopweb --install-service[/cyan]")
        except Exception as e:
            console.print(f"\n❌ [red]Installation failed: {e}[/red]")


def handle_uninstall_service():
    """Uninstall auto-start monitoring service."""
    import platform
    import os
    import subprocess
    
    system = platform.system().lower()
    
    console.print(Panel("🗑️  Uninstall Auto-Start Monitoring Service", style="bold yellow"))
    
    if system == 'darwin':  # macOS
        plist_path = '/Library/LaunchDaemons/com.stopweb.watch.plist'
        try:
            os.system(f'launchctl unload {plist_path}')
            if os.path.exists(plist_path):
                os.remove(plist_path)
            console.print("✅ [green]Service uninstalled successfully![/green]")
        except PermissionError:
            console.print("❌ [red]Permission denied. Please run with sudo:[/red]")
            console.print("   [cyan]sudo stopweb --uninstall-service[/cyan]")
        except Exception as e:
            console.print(f"❌ [red]Uninstallation failed: {e}[/red]")
    
    elif system == 'windows':
        try:
            import subprocess
            subprocess.run(['powershell', '-Command', 
                            'Unregister-ScheduledTask -TaskName "StopWeb Monitor" -Confirm:$false'],
                           check=True)
            console.print("✅ [green]Service uninstalled successfully![/green]")
        except subprocess.CalledProcessError:
            console.print("❌ [red]Uninstallation failed. Please run as Administrator[/red]")
        except Exception as e:
            console.print(f"❌ [red]Uninstallation failed: {e}[/red]")
    
    else:  # Linux
        try:
            os.system('systemctl stop stopweb-monitor')
            os.system('systemctl disable stopweb-monitor')
            service_path = '/etc/systemd/system/stopweb-monitor.service'
            if os.path.exists(service_path):
                os.remove(service_path)
            os.system('systemctl daemon-reload')
            console.print("✅ [green]Service uninstalled successfully![/green]")
        except PermissionError:
            console.print("❌ [red]Permission denied. Please run with sudo:[/red]")
            console.print("   [cyan]sudo stopweb --uninstall-service[/cyan]")
        except Exception as e:
            console.print(f"❌ [red]Uninstallation failed: {e}[/red]")


@click.command()
def version():
    """Show version information"""
    from . import __version__
    console.print(f"StopWeb version {__version__}")


# Add version command to main group
main = cast(click.Group, main)  # satisfy type checker
main.add_command(version)  # type: ignore[attr-defined]


if __name__ == '__main__':
    main()  # type: ignore[arg-type]