from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class ConstraintTier(str, Enum):
    IMMUTABLE = "immutable"      # Core rules, never expire
    VALIDATED = "validated"      # Human-approved, stable
    EXPERIMENTAL = "experimental" # Auto-learned, 30-day trial
    LOGGED = "logged"            # Informational only

class ConstraintScope(BaseModel):
    language: Optional[str] = None
    domain: Optional[str] = "general" # security, performance, etc.
    context: Optional[str] = None

class Constraint(BaseModel):
    id: str
    description: str
    pattern: str
    tier: ConstraintTier = ConstraintTier.EXPERIMENTAL
    scope: ConstraintScope = Field(default_factory=ConstraintScope)
    source: str = "system" # agent name or 'incident_report'
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    active: bool = True
    metadata: Dict = Field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return False

    def matches(self, language: str, domain: str = "general") -> bool:
        if self.scope.language and self.scope.language != language:
            return False
        
        # If we ask for 'general', we want everything for that language
        if domain == "general":
            return True
            
        # If we ask for a specific domain, return 'general' or that specific domain
        if self.scope.domain == "general" or self.scope.domain == domain:
            return True
            
        return False
