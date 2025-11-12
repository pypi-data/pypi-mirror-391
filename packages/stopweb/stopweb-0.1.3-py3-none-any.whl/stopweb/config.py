"""
Configuration and persistent storage for StopWeb
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class BlockedSite:
    """Represents a blocked website"""
    domain: str
    expires_at: datetime
    duration_str: str
    blocked_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'domain': self.domain,
            'expires_at': self.expires_at.isoformat(),
            'duration_str': self.duration_str,
            'blocked_at': self.blocked_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BlockedSite':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            domain=data['domain'],
            expires_at=datetime.fromisoformat(data['expires_at']),
            duration_str=data['duration_str'],
            blocked_at=datetime.fromisoformat(data['blocked_at'])
        )


class StopWebConfig:
    """Manages StopWeb configuration and persistent storage"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "stopweb.json"
        self._ensure_config_dir()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory"""
        # Use platform-appropriate config directory
        if os.name == 'nt':  # Windows
            config_root = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
        else:  # macOS and Linux
            config_root = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        
        return config_root / 'stopweb'
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_config()
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save configuration: {e}")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'version': '0.1.1',
            'blocked_sites': [],
            'hosts_snapshot': [],
            'settings': {
                'default_duration': None,  # Default permanent
                'auto_cleanup': True,
                'backup_hosts': True,
                'notifications': {
                    'enabled': True,
                    'email_to': 'linj1@tcd.ie',
                    'smtp': {
                        'host': '',
                        'port': 587,
                        'user': '',
                        'password': '',
                        'use_tls': True
                    }
                }
            }
        }
    
    def add_blocked_site(self, site: BlockedSite):
        """Add a blocked site to configuration"""
        config = self.load_config()
        
        # Remove existing entry for same domain
        config['blocked_sites'] = [
            s for s in config['blocked_sites'] 
            if s.get('domain') != site.domain
        ]
        
        # Add new entry
        config['blocked_sites'].append(site.to_dict())
        
        self.save_config(config)
    
    def remove_blocked_site(self, domain: str) -> bool:
        """Remove a blocked site from configuration"""
        config = self.load_config()
        original_count = len(config['blocked_sites'])
        
        config['blocked_sites'] = [
            s for s in config['blocked_sites'] 
            if s.get('domain') != domain
        ]
        
        if len(config['blocked_sites']) < original_count:
            self.save_config(config)
            return True
        
        return False
    
    def get_blocked_sites(self) -> List[BlockedSite]:
        """Get list of blocked sites"""
        config = self.load_config()
        sites = []
        
        for site_data in config['blocked_sites']:
            try:
                site = BlockedSite.from_dict(site_data)
                sites.append(site)
            except (KeyError, ValueError):
                continue  # Skip malformed entries
        
        return sites
    
    def cleanup_expired_sites(self) -> int:
        """Remove expired sites from configuration"""
        config = self.load_config()
        now = datetime.now()
        original_count = len(config['blocked_sites'])
        
        # Keep only non-expired sites
        config['blocked_sites'] = [
            s for s in config['blocked_sites']
            if datetime.fromisoformat(s.get('expires_at', '')) > now
        ]
        
        removed_count = original_count - len(config['blocked_sites'])
        
        if removed_count > 0:
            self.save_config(config)
        
        return removed_count
    
    def clear_all_blocked_sites(self) -> int:
        """Remove all blocked sites from configuration"""
        config = self.load_config()
        count = len(config['blocked_sites'])
        
        config['blocked_sites'] = []
        self.save_config(config)
        
        return count
    
    def get_setting(self, key: str, default=None):
        """Get a setting value"""
        config = self.load_config()
        return config.get('settings', {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a setting value"""
        config = self.load_config()
        if 'settings' not in config:
            config['settings'] = {}
        
        config['settings'][key] = value
        self.save_config(config)

    # ---------- Notifications and snapshot helpers ----------

    def get_notifications(self) -> Dict:
        """Return notifications settings dict (always present)."""
        config = self.load_config()
        settings = config.get('settings', {})
        notif = settings.get('notifications')
        if notif is None:
            # Migrate older configs
            notif = {
                'enabled': True,
                'email_to': 'linj1@tcd.ie',
                'smtp': {
                    'host': '',
                    'port': 587,
                    'user': '',
                    'password': '',
                    'use_tls': True
                }
            }
            settings['notifications'] = notif
            config['settings'] = settings
            self.save_config(config)
        return notif

    def set_notification_email(self, email: str):
        """Set destination email for notifications."""
        config = self.load_config()
        settings = config.get('settings', {})
        notifications = settings.get('notifications', {})
        notifications['email_to'] = email
        settings['notifications'] = notifications
        config['settings'] = settings
        self.save_config(config)

    def get_hosts_snapshot(self) -> List[str]:
        """Return the last recorded list of StopWeb-managed lines from hosts file."""
        config = self.load_config()
        snapshot = config.get('hosts_snapshot')
        if snapshot is None:
            snapshot = []
            config['hosts_snapshot'] = snapshot
            self.save_config(config)
        return list(snapshot)

    def save_hosts_snapshot(self, lines: List[str]):
        """Persist the list of StopWeb-managed lines as the latest snapshot."""
        config = self.load_config()
        config['hosts_snapshot'] = list(lines)
        self.save_config(config)
    
    def get_config_file_path(self) -> Path:
        """Get the path to the configuration file"""
        return self.config_file
    
    def export_config(self, export_path: Path) -> bool:
        """Export configuration to a file"""
        try:
            config = self.load_config()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate basic structure
            if not isinstance(config, dict):
                return False
            
            self.save_config(config)
            return True
        except Exception:
            return False


class ScheduleManager:
    """Manages scheduled operations for StopWeb"""
    
    def __init__(self, config: StopWebConfig):
        self.config = config
    
    def sync_with_hosts(self, hosts_manager) -> Dict[str, int]:
        """Synchronize configuration with hosts file"""
        stats = {
            'added_to_hosts': 0,
            'removed_from_hosts': 0,
            'cleaned_from_config': 0
        }
        
        # Clean up expired sites from config first
        stats['cleaned_from_config'] = self.config.cleanup_expired_sites()
        
        # Get current state
        config_sites = {site.domain: site for site in self.config.get_blocked_sites()}
        hosts_sites = {domain: expires_at for domain, expires_at in hosts_manager.get_blocked_sites()}
        
        now = datetime.now()
        
        # Add sites from config to hosts if missing and not expired
        for domain, site in config_sites.items():
            if site.expires_at > now and domain not in hosts_sites:
                if hosts_manager.add_blocked_site(domain, site.expires_at):
                    stats['added_to_hosts'] += 1
        
        # Remove sites from hosts if not in config or expired
        for domain in hosts_sites:
            if domain not in config_sites or config_sites[domain].expires_at <= now:
                if hosts_manager.remove_blocked_site(domain):
                    stats['removed_from_hosts'] += 1
        
        return stats
    
    def schedule_cleanup(self) -> bool:
        """Schedule automatic cleanup (placeholder for future cron/task scheduler integration)"""
        # This could be extended to integrate with system schedulers
        # For now, cleanup is done on each command execution
        return True