"""Base classes for wallet pass management."""

import abc
from typing import Optional

from ..config import WalletConfig
from ..schema.core import PassData, PassResponse, PassTemplate
from ..storage import StorageBackend
from ..logging import get_logger

logger = get_logger(__name__)


class BasePass(abc.ABC):
    """Abstract base class for wallet pass implementations."""
    
    def __init__(self, config: WalletConfig, storage: Optional[StorageBackend] = None):
        """Initialize with configuration."""
        self.config = config
        self.storage = storage
    
    @abc.abstractmethod
    def create_pass(self, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Create a new pass."""
        pass
    
    @abc.abstractmethod
    def update_pass(self, pass_id: str, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Update an existing pass."""
        pass
    
    @abc.abstractmethod
    def get_pass(self, pass_id: str) -> PassResponse:
        """Retrieve a pass by ID."""
        pass
    
    @abc.abstractmethod
    def void_pass(self, pass_id: str) -> PassResponse:
        """Mark a pass as void."""
        pass
    
    @abc.abstractmethod
    def generate_pass_file(self, pass_id: str, template: PassTemplate) -> bytes:
        """Generate the physical pass file (pkpass for Apple, JSON for Google)."""
        pass
    
    @abc.abstractmethod
    def send_update_notification(self, pass_id: str) -> bool:
        """Send a push notification for pass updates."""
        pass