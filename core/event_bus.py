from typing import Callable, Dict, List, Any, Optional
import asyncio
from datetime import datetime
import hashlib

class EventType:
    DELIBERATION_START = "deliberation_start"
    AGENT_VOTE = "agent_vote"
    CONSENSUS_REACHED = "consensus_reached"
    DELIBERATION_END = "deliberation_end"
    ERROR = "error"
    
    # New Events for Phase 4a
    TOKEN_STATUS = "token_status"
    LOOP_DETECTED = "loop_detected"
    AGENT_ACTION = "agent_action" # Generic action logging

class Event:
    def __init__(self, type: str, data: Dict[str, Any]):
        self.type = type
        self.data = data
        self.timestamp = datetime.now().isoformat()

class LoopDetector:
    """
    Tracks agent actions to detect identical repetitions.
    Rule: 3 identical actions without state change = STUCK.
    """
    def __init__(self):
        self.history = []
        self.max_history = 10
        self.threshold = 3

    def check(self, agent: str, action: str, target: str) -> Optional[Dict]:
        """
        Returns loop details if detected, else None.
        """
        # Create a signature of the action
        sig = hashlib.md5(f"{agent}:{action}:{target}".encode()).hexdigest()
        self.history.append(sig)
        
        # Keep history short
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # Check for immediate repetition at the end of the list
        if len(self.history) >= self.threshold:
            recent = self.history[-self.threshold:]
            if all(s == sig for s in recent):
                return {
                    "agent": agent,
                    "action": action,
                    "target": target,
                    "count": self.threshold
                }
        return None

class EventBus:
    """
    Zero-Cost Event Bus with integrated Loop Detection.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {}
            cls._instance.loop_detector = LoopDetector()
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Dict[str, Any]):
        # Loop Detection Logic
        if event_type == EventType.AGENT_ACTION:
            agent = data.get("agent", "unknown")
            action = data.get("action", "unknown")
            target = data.get("target", "unknown")
            
            loop = self.loop_detector.check(agent, action, target)
            if loop:
                # Auto-publish loop event
                self.publish(EventType.LOOP_DETECTED, loop)

        # Standard Dispatch
        if event_type not in self.subscribers:
            return

        event = Event(event_type, data)
        for callback in self.subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(event))
                else:
                    callback(event)
            except Exception as e:
                print(f"[EventBus Error] {e}")