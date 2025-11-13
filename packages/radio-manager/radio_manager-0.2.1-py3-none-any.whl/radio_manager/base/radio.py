"""Abstract base class for all radio devices."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Radio(ABC):
    """Base class for all radio devices."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connected = False
        self.model = config.get('model', 'Unknown')
        self.name = config.get('name', '')

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the radio."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the radio."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current radio status."""
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
