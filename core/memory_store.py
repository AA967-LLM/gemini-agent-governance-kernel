import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.constraints import Constraint, ConstraintTier

class MemoryStore:
    """
    Persistent Institutional Memory for the Council.
    Manages the Constraint Library and Incident Database.
    """
    def __init__(self, storage_dir: str = ".gemini/memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.constraints_path = self.storage_dir / "constraints.json"
        self.incidents_path = self.storage_dir / "incidents.json"
        
        self.constraints: List[Constraint] = self._load_constraints()
        self.incidents: List[Dict] = self._load_incidents()

    def _load_constraints(self) -> List[Constraint]:
        if not self.constraints_path.exists():
            return []
        try:
            with open(self.constraints_path, 'r') as f:
                data = json.load(f)
                return [Constraint(**c) for c in data]
        except Exception:
            return []

    def _load_incidents(self) -> List[Dict]:
        if not self.incidents_path.exists():
            return []
        try:
            with open(self.incidents_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def save(self):
        """Persist memory to disk."""
        with open(self.constraints_path, 'w') as f:
            json.dump([c.model_dump(mode='json') for c in self.constraints], f, indent=2)
        with open(self.incidents_path, 'w') as f:
            json.dump(self.incidents, f, indent=2)

    def add_constraint(self, constraint: Constraint):
        # Prevent poisoning: Detect overly broad patterns
        if len(constraint.pattern) < 3:
            constraint.active = False
            constraint.metadata["warning"] = "Overly broad pattern detected"
        
        # Set expiry for experimental
        if constraint.tier == ConstraintTier.EXPERIMENTAL and not constraint.expires_at:
            constraint.expires_at = datetime.now() + timedelta(days=30)
            
        self.constraints.append(constraint)
        self.save()

    def get_active_constraints(self, language: str, domain: str = "general") -> List[Constraint]:
        active = []
        now = datetime.now()
        for c in self.constraints:
            if not c.active: continue
            if c.is_expired(): continue
            if c.matches(language, domain):
                active.append(c)
        return active

    def record_incident(self, incident: Dict):
        incident["timestamp"] = datetime.now().isoformat()
        self.incidents.append(incident)
        self.save()
