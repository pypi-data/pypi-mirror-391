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
@click.argument('websites', nargs=-1)
@click.pass_context
def main(ctx, duration: Optional[str], list_sites: bool, remove: Optional[str], 
         clear: bool, cleanup: bool, audit: bool, watch: bool, interval: int, websites: tuple):
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