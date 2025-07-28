"""
Discord Username Monitor - Username Data Model
Represents a username being monitored
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Username:
    """Username data model for monitoring"""
    
    name: str
    length: int
    status: str = "unknown"  # unknown, available, taken, checking
    last_checked: Optional[datetime] = None
    check_count: int = 0
    found_at: Optional[datetime] = None
    claimed_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate username after initialization"""
        if not self.name:
            raise ValueError("Username name is required")
        
        # Clean username
        self.name = self.name.strip().lower()
        
        # Validate length
        if len(self.name) < 2 or len(self.name) > 32:
            raise ValueError(f"Invalid username length: {len(self.name)}")
        
        # Validate characters
        if not self._is_valid_username(self.name):
            raise ValueError(f"Invalid username characters: {self.name}")
        
        # Set length
        self.length = len(self.name)
    
    def _is_valid_username(self, username):
        """Check if username contains valid Discord characters"""
        import re
        # Discord allows letters, numbers, periods, underscores
        # Cannot start/end with periods, no consecutive periods
        if username.startswith('.') or username.endswith('.'):
            return False
        if '..' in username:
            return False
        return re.match(r'^[a-zA-Z0-9._]+$', username) is not None
    
    @property
    def rarity(self):
        """Get username rarity based on length"""
        if self.length <= 3:
            return "ultra_rare"
        elif self.length == 4:
            return "rare"
        elif self.length == 5:
            return "uncommon"
        else:
            return "common"
    
    @property
    def rarity_text(self):
        """Get human-readable rarity text"""
        rarity_map = {
            "ultra_rare": "Ultra Rare",
            "rare": "Rare",
            "uncommon": "Uncommon",
            "common": "Common"
        }
        return rarity_map.get(self.rarity, "Unknown")
    
    def mark_available(self):
        """Mark username as available"""
        self.status = "available"
        self.found_at = datetime.now()
    
    def mark_taken(self):
        """Mark username as taken"""
        self.status = "taken"
        self.last_checked = datetime.now()
    
    def mark_checking(self):
        """Mark username as being checked"""
        self.status = "checking"
        self.check_count += 1
    
    def mark_claimed(self, account_email):
        """Mark username as claimed"""
        self.status = "claimed"
        self.claimed_by = account_email
        self.found_at = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'length': self.length,
            'status': self.status,
            'rarity': self.rarity,
            'check_count': self.check_count,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'found_at': self.found_at.isoformat() if self.found_at else None,
            'claimed_by': self.claimed_by
        }
    
    def __str__(self):
        """String representation"""
        return f"Username(name={self.name}, status={self.status}, rarity={self.rarity})"
    
    def __repr__(self):
        """Debug representation"""
        return f"Username(name='{self.name}', length={self.length}, status='{self.status}')"