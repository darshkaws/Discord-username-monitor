"""
Discord Username Monitor - Account Data Model
Represents a Discord account with credentials
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    """Discord account data model"""
    
    email: str
    token: str
    password: Optional[str] = None
    username: Optional[str] = None
    format: str = "unknown"
    line_num: Optional[int] = None
    
    def __post_init__(self):
        """Validate account data after initialization"""
        if not self.token:
            raise ValueError("Token is required")
        
        if not self.email:
            raise ValueError("Email is required")
        
        # Clean token (remove quotes if present)
        self.token = self.token.strip().strip('"\'')
        
        # Validate token format (basic check)
        if len(self.token) < 50:
            raise ValueError("Token appears to be invalid (too short)")
        
        if not ('.' in self.token or self.token.startswith(('mfa.', 'NTK', 'MTK', 'ODk'))):
            raise ValueError("Token format appears invalid")
    
    @property
    def display_email(self):
        """Get display-friendly email"""
        return self.email
    
    @property
    def masked_token(self):
        """Get masked token for display"""
        if len(self.token) > 20:
            return f"{self.token[:10]}...{self.token[-10:]}"
        return f"{self.token[:5]}..."
    
    @property
    def has_password(self):
        """Check if account has password"""
        return self.password is not None and len(self.password.strip()) > 0
    
    @property
    def can_claim(self):
        """Check if account can be used for claiming (has password)"""
        return self.has_password
    
    def to_credentials_string(self):
        """Convert to credentials string format"""
        return f"{self.email}:{self.password or 'N/A'}:{self.token}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'token': self.token,
            'format': self.format,
            'line_num': self.line_num,
            'has_password': self.has_password,
            'can_claim': self.can_claim
        }
    
    def __str__(self):
        """String representation"""
        return f"Account(email={self.email}, format={self.format}, can_claim={self.can_claim})"
    
    def __repr__(self):
        """Debug representation"""
        return f"Account(email='{self.email}', token='{self.masked_token}', format='{self.format}')"