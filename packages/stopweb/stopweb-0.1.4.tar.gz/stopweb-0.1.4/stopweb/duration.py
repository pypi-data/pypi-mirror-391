"""
Duration parsing and time management utilities
"""

import re
from datetime import datetime, timedelta
from typing import Optional


class DurationParser:
    """Parse human-readable duration strings"""
    
    def __init__(self):
        # Duration patterns with flexible matching
        self.patterns = [
            # Hours: 2h, 12hours, 1 hour
            (r'(\d+)\s*h(?:ours?)?', 'hours'),
            # Days: 1d, 7days, 1 day  
            (r'(\d+)\s*d(?:ays?)?', 'days'),
            # Weeks: 1w, 2weeks, 1 week
            (r'(\d+)\s*w(?:eeks?)?', 'weeks'),
            # Minutes: 30m, 45mins, 30 minutes
            (r'(\d+)\s*m(?:ins?|inutes?)?', 'minutes'),
        ]
    
    def parse_duration(self, duration_str: str) -> Optional[timedelta]:
        """
        Parse duration string into timedelta
        
        Args:
            duration_str: String like '2h', '1d', '3days', '1week'
            
        Returns:
            timedelta object or None if parsing fails
        """
        if not duration_str:
            return None
        
        duration_str = duration_str.lower().strip()
        
        for pattern, unit in self.patterns:
            match = re.match(pattern, duration_str)
            if match:
                value = int(match.group(1))
                
                if unit == 'minutes':
                    return timedelta(minutes=value)
                elif unit == 'hours':
                    return timedelta(hours=value)
                elif unit == 'days':
                    return timedelta(days=value)
                elif unit == 'weeks':
                    return timedelta(weeks=value)
        
        return None
    
    def get_default_duration(self) -> timedelta:
        """Deprecated: default duration is no longer used (blocks are permanent by default).

        Kept for backward compatibility; returns 1 day but callers should not rely on this.
        """
        return timedelta(days=1)
    
    def format_duration(self, delta: timedelta) -> str:
        """Format timedelta into human-readable string"""
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"
        
        minutes = total_seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        
        days = hours // 24
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''}"
        
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    
    def format_expires_at(self, expires_at: datetime) -> str:
        """Format expiration datetime for display"""
        now = datetime.now()
        
        if expires_at <= now:
            return "Expired"
        
        delta = expires_at - now
        time_left = self.format_duration(delta)
        
        # Also show the actual time
        expires_str = expires_at.strftime("%Y-%m-%d %H:%M")
        
        return f"in {time_left} ({expires_str})"


class TimeManager:
    """Manage time-based operations for website blocking"""
    
    def __init__(self):
        self.parser = DurationParser()
    
    def calculate_expires_at(self, duration_str: Optional[str] = None) -> Optional[datetime]:
        """
        Calculate expiration time from duration string
        
        Args:
            duration_str: Duration string like '2h', '1d', or None for default
            
        Returns:
            datetime when the block should expire, or None if no expiry (permanent)
        """
        if not duration_str:
            return None

        delta = self.parser.parse_duration(duration_str)
        if not delta:
            raise ValueError(f"Invalid duration format: {duration_str}")

        return datetime.now() + delta
    
    def is_expired(self, expires_at: datetime) -> bool:
        """Check if a block has expired"""
        return datetime.now() >= expires_at
    
    def time_until_expiry(self, expires_at: datetime) -> timedelta:
        """Get time remaining until expiry"""
        now = datetime.now()
        if expires_at <= now:
            return timedelta(0)
        return expires_at - now
    
    def format_time_remaining(self, expires_at: datetime) -> str:
        """Format time remaining in human-readable form"""
        return self.parser.format_expires_at(expires_at)


def validate_duration_format(duration_str: str) -> bool:
    """Validate if duration string is in correct format"""
    parser = DurationParser()
    return parser.parse_duration(duration_str) is not None


def get_supported_duration_formats() -> str:
    """Get help text for supported duration formats"""
    return """
Supported duration formats:
  h, hours    - Hours (e.g., 2h, 12hours)
  d, days     - Days (e.g., 1d, 7days)  
  w, weeks    - Weeks (e.g., 1w, 2weeks)
  m, minutes  - Minutes (e.g., 30m, 45minutes)

Examples:
  stopweb --duration 2h facebook.com
  stopweb --duration 1d youtube.com
  stopweb --duration 1w reddit.com
"""