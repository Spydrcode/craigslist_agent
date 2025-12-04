"""
Real-time Agent Progress Tracking
Provides observable status for agent pipeline execution.
"""
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentProgress:
    """Tracks progress of a single agent."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.PENDING
        self.progress = 0.0  # 0.0 to 1.0
        self.current_item = 0
        self.total_items = 0
        self.message = ""
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.emoji = "⏳"

    def start(self, total_items: int = 0, message: str = ""):
        """Mark agent as started."""
        self.status = AgentStatus.RUNNING
        self.start_time = time.time()
        self.total_items = total_items
        self.message = message or f"Starting {self.name}..."
        self.emoji = "🔄"

    def update(self, current: int = None, message: str = None):
        """Update progress."""
        if current is not None:
            self.current_item = current
            if self.total_items > 0:
                self.progress = current / self.total_items
        if message:
            self.message = message

    def complete(self, result=None, message: str = None):
        """Mark agent as completed."""
        self.status = AgentStatus.COMPLETED
        self.end_time = time.time()
        self.progress = 1.0
        self.result = result
        self.message = message or f"{self.name} completed"
        self.emoji = "✅"

    def fail(self, error: str):
        """Mark agent as failed."""
        self.status = AgentStatus.FAILED
        self.end_time = time.time()
        self.error = error
        self.message = f"Failed: {error}"
        self.emoji = "❌"

    def skip(self, reason: str):
        """Mark agent as skipped."""
        self.status = AgentStatus.SKIPPED
        self.message = reason
        self.emoji = "⏭️"

    @property
    def elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return None
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'progress': self.progress,
            'current_item': self.current_item,
            'total_items': self.total_items,
            'message': self.message,
            'emoji': self.emoji,
            'elapsed_time': self.elapsed_time,
            'error': self.error
        }


class PipelineProgress:
    """Tracks progress of entire agent pipeline."""

    def __init__(self):
        self.agents: List[AgentProgress] = []
        self.callbacks: List[Callable] = []
        self.start_time = None
        self.end_time = None

    def add_agent(self, name: str, description: str) -> AgentProgress:
        """Add agent to pipeline."""
        agent = AgentProgress(name, description)
        self.agents.append(agent)
        return agent

    def get_agent(self, name: str) -> Optional[AgentProgress]:
        """Get agent by name."""
        return next((a for a in self.agents if a.name == name), None)

    def on_update(self, callback: Callable):
        """Register callback for updates."""
        self.callbacks.append(callback)

    def notify(self):
        """Notify all callbacks of update."""
        for callback in self.callbacks:
            try:
                callback(self)
            except Exception as e:
                print(f"Callback error: {e}")

    def start(self):
        """Start pipeline."""
        self.start_time = time.time()
        self.notify()

    def complete(self):
        """Complete pipeline."""
        self.end_time = time.time()
        self.notify()

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress (0.0 to 1.0)."""
        if not self.agents:
            return 0.0
        return sum(a.progress for a in self.agents) / len(self.agents)

    @property
    def completed_agents(self) -> int:
        """Count completed agents."""
        return sum(1 for a in self.agents if a.status == AgentStatus.COMPLETED)

    @property
    def total_agents(self) -> int:
        """Total number of agents."""
        return len(self.agents)

    @property
    def elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return None
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def estimated_time_remaining(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if not self.start_time or self.overall_progress == 0:
            return None
        elapsed = self.elapsed_time
        if not elapsed:
            return None
        total_estimated = elapsed / self.overall_progress
        return total_estimated - elapsed

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'agents': [a.to_dict() for a in self.agents],
            'overall_progress': self.overall_progress,
            'completed_agents': self.completed_agents,
            'total_agents': self.total_agents,
            'elapsed_time': self.elapsed_time,
            'estimated_time_remaining': self.estimated_time_remaining,
            'start_time': self.start_time,
            'end_time': self.end_time
        }


# Global progress tracker for current operation
_current_progress: Optional[PipelineProgress] = None


def get_current_progress() -> Optional[PipelineProgress]:
    """Get current pipeline progress."""
    return _current_progress


def set_current_progress(progress: PipelineProgress):
    """Set current pipeline progress."""
    global _current_progress
    _current_progress = progress


def clear_current_progress():
    """Clear current pipeline progress."""
    global _current_progress
    _current_progress = None
