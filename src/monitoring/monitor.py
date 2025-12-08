"""Monitor configuration and data models."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Monitor:
    """Represents a monitoring configuration."""
    name: str
    url: str
    steps: List[Dict[str, Any]]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = True
    schedule: str = "*/5 * * * *"  # Default: every 5 minutes
    alert_emails: List[str] = field(default_factory=list)
    slack_webhook_url: Optional[str] = None
    alerts_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert monitor to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'steps': self.steps,
            'enabled': self.enabled,
            'schedule': self.schedule,
            'alert_emails': self.alert_emails,
            'slack_webhook_url': self.slack_webhook_url,
            'alerts_enabled': self.alerts_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Monitor':
        """Create monitor from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            url=data['url'],
            steps=data['steps'],
            enabled=data.get('enabled', True),
            schedule=data.get('schedule', '*/5 * * * *'),
            alert_emails=data.get('alert_emails', []),
            slack_webhook_url=data.get('slack_webhook_url'),
            alerts_enabled=data.get('alerts_enabled', True),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )


@dataclass
class TestRun:
    """Represents a test run result."""
    monitor_id: str
    status: str  # 'success', 'failed', 'error'
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert test run to dictionary."""
        return {
            'id': self.id,
            'monitor_id': self.monitor_id,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'screenshot_path': self.screenshot_path,
            'step_results': self.step_results
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestRun':
        """Create test run from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            monitor_id=data['monitor_id'],
            status=data['status'],
            started_at=datetime.fromisoformat(data['started_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            duration_ms=data.get('duration_ms', 0),
            error_message=data.get('error_message'),
            screenshot_path=data.get('screenshot_path'),
            step_results=data.get('step_results', [])
        )
