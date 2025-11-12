"""User data models for BugBountyCrawler."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, EmailStr
import uuid


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"


class UserPreferences(BaseModel):
    """User preferences."""
    
    # UI Preferences
    theme: str = Field(default="light", description="UI theme")
    language: str = Field(default="en", description="Language preference")
    timezone: str = Field(default="UTC", description="Timezone")
    
    # Notification Preferences
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    finding_notifications: bool = Field(default=True, description="Notify on new findings")
    scan_completion_notifications: bool = Field(default=True, description="Notify on scan completion")
    error_notifications: bool = Field(default=True, description="Notify on errors")
    
    # Scan Preferences
    default_scan_config: Dict[str, Any] = Field(default_factory=dict, description="Default scan configuration")
    auto_approve_findings: bool = Field(default=False, description="Auto-approve findings")
    max_concurrent_scans: int = Field(default=3, description="Maximum concurrent scans")
    
    # Security Preferences
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication enabled")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    require_password_change: bool = Field(default=False, description="Require password change")
    
    @validator("theme")
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme."""
        valid_themes = ["light", "dark", "auto"]
        if v not in valid_themes:
            raise ValueError(f"Invalid theme: {v}. Must be one of {valid_themes}")
        return v


class User(BaseModel):
    """User model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="User ID")
    
    # Basic Information
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    
    # Authentication
    password_hash: str = Field(..., description="Hashed password")
    salt: str = Field(..., description="Password salt")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    
    # Status
    is_active: bool = Field(default=True, description="User is active")
    is_verified: bool = Field(default=False, description="Email is verified")
    is_locked: bool = Field(default=False, description="Account is locked")
    
    # Preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="User preferences")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    password_changed_at: Optional[datetime] = Field(None, description="Password change timestamp")
    
    # Security
    failed_login_attempts: int = Field(default=0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    two_factor_secret: Optional[str] = Field(None, description="Two-factor secret")
    recovery_codes: List[str] = Field(default_factory=list, description="Recovery codes")
    
    # Activity
    total_scans: int = Field(default=0, description="Total scans created")
    total_findings: int = Field(default=0, description="Total findings created")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Additional Data
    tags: List[str] = Field(default_factory=list, description="User tags")
    notes: Optional[str] = Field(None, description="User notes")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw user data")
    
    @validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username."""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Username must be no more than 50 characters long")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain alphanumeric characters, underscores, and hyphens")
        return v.lower()
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def is_analyst(self) -> bool:
        """Check if user is analyst or admin."""
        return self.role in [UserRole.ADMIN, UserRole.ANALYST]
    
    def can_create_scans(self) -> bool:
        """Check if user can create scans."""
        return self.role in [UserRole.ADMIN, UserRole.ANALYST]
    
    def can_approve_findings(self) -> bool:
        """Check if user can approve findings."""
        return self.role in [UserRole.ADMIN, UserRole.ANALYST]
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == UserRole.ADMIN
    
    def is_account_locked(self) -> bool:
        """Check if account is locked."""
        if not self.is_locked:
            return False
        
        if self.locked_until and datetime.utcnow() > self.locked_until:
            # Unlock account if lock time has passed
            self.is_locked = False
            self.locked_until = None
            self.failed_login_attempts = 0
            return False
        
        return True
    
    def record_failed_login(self) -> None:
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        self.updated_at = datetime.utcnow()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.is_locked = True
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def record_successful_login(self) -> None:
        """Record a successful login."""
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def change_password(self, new_password_hash: str, new_salt: str) -> None:
        """Change user password."""
        self.password_hash = new_password_hash
        self.salt = new_salt
        self.password_changed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def enable_two_factor(self, secret: str) -> None:
        """Enable two-factor authentication."""
        self.two_factor_secret = secret
        self.preferences.two_factor_enabled = True
        self.updated_at = datetime.utcnow()
    
    def disable_two_factor(self) -> None:
        """Disable two-factor authentication."""
        self.two_factor_secret = None
        self.preferences.two_factor_enabled = False
        self.recovery_codes.clear()
        self.updated_at = datetime.utcnow()
    
    def generate_recovery_codes(self, count: int = 10) -> List[str]:
        """Generate recovery codes for two-factor authentication."""
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        
        self.recovery_codes = codes
        self.updated_at = datetime.utcnow()
        return codes
    
    def verify_recovery_code(self, code: str) -> bool:
        """Verify a recovery code."""
        if code in self.recovery_codes:
            self.recovery_codes.remove(code)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary."""
        return {
            "total_scans": self.total_scans,
            "total_findings": self.total_findings,
            "last_login": self.last_login,
            "last_activity": self.last_activity,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role.value,
        }
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
