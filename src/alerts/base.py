"""Base alert handler interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AlertHandler(ABC):
    """Base class for alert handlers."""

    @abstractmethod
    def send_alert(self, monitor_name: str, test_run: Dict[str, Any]) -> bool:
        """
        Send an alert for a failed test run.

        Args:
            monitor_name: Name of the monitor that failed
            test_run: Test run result dictionary

        Returns:
            True if alert was sent successfully, False otherwise
        """
        pass

    def should_send_alert(self, test_run: Dict[str, Any]) -> bool:
        """
        Determine if an alert should be sent for this test run.

        Args:
            test_run: Test run result dictionary

        Returns:
            True if alert should be sent
        """
        # Send alerts only for failures and errors
        return test_run.get('status') in ['failed', 'error']
