"""Storage backends for wallet passes."""

import abc
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class StorageBackend(abc.ABC):
    """Abstract base class for storage backends."""
    
    @abc.abstractmethod
    def store_pass(self, provider: str, pass_id: str, pass_data: Dict[str, Any]) -> None:
        """Store pass data for a specific provider."""
        pass
    
    @abc.abstractmethod
    def retrieve_pass(self, provider: str, pass_id: str) -> Dict[str, Any]:
        """Retrieve pass data for a specific provider."""
        pass
    
    @abc.abstractmethod
    def delete_pass(self, provider: str, pass_id: str) -> bool:
        """Delete pass data for a specific provider."""
        pass
    
    @abc.abstractmethod
    def list_passes(self, provider: str) -> List[str]:
        """List all pass IDs for a specific provider."""
        pass


class FileSystemStorage(StorageBackend):
    """File system based storage for passes."""
    
    def __init__(self, storage_path: Union[str, Path]):
        """Initialize with storage path."""
        self.storage_path = Path(storage_path)
    
    def store_pass(self, provider: str, pass_id: str, pass_data: Dict[str, Any]) -> None:
        """Store pass data in the file system."""
        # Create provider directory if it doesn't exist
        provider_dir = self.storage_path / provider / "passes"
        os.makedirs(provider_dir, exist_ok=True)
        
        # Store the pass data
        pass_path = provider_dir / f"{pass_id}.json"
        with open(pass_path, 'w') as f:
            json.dump(pass_data, f, indent=2)
        
        logger.debug(f"Stored {provider} pass {pass_id} to {pass_path}")
    
    def retrieve_pass(self, provider: str, pass_id: str) -> Dict[str, Any]:
        """Retrieve pass data from the file system."""
        pass_path = self.storage_path / provider / "passes" / f"{pass_id}.json"
        
        if not pass_path.exists():
            raise FileNotFoundError(f"Pass not found: {pass_id}")
        
        with open(pass_path, 'r') as f:
            pass_data = json.load(f)
        
        logger.debug(f"Retrieved {provider} pass {pass_id} from {pass_path}")
        
        return pass_data
    
    def delete_pass(self, provider: str, pass_id: str) -> bool:
        """Delete pass data from the file system."""
        pass_path = self.storage_path / provider / "passes" / f"{pass_id}.json"
        
        if not pass_path.exists():
            logger.warning(f"Pass not found for deletion: {pass_id}")
            return False
        
        os.remove(pass_path)
        logger.debug(f"Deleted {provider} pass {pass_id} from {pass_path}")
        
        return True
    
    def list_passes(self, provider: str) -> List[str]:
        """List all pass IDs stored in the file system."""
        provider_dir = self.storage_path / provider / "passes"
        
        if not provider_dir.exists():
            return []
        
        pass_ids = []
        for file_path in provider_dir.glob("*.json"):
            pass_id = file_path.stem
            pass_ids.append(pass_id)
        
        return pass_ids


class MemoryStorage(StorageBackend):
    """In-memory storage for passes. Useful for testing."""
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self.passes = {}
    
    def store_pass(self, provider: str, pass_id: str, pass_data: Dict[str, Any]) -> None:
        """Store pass data in memory."""
        if provider not in self.passes:
            self.passes[provider] = {}
        
        self.passes[provider][pass_id] = pass_data
        logger.debug(f"Stored {provider} pass {pass_id} in memory")
    
    def retrieve_pass(self, provider: str, pass_id: str) -> Dict[str, Any]:
        """Retrieve pass data from memory."""
        if provider not in self.passes or pass_id not in self.passes[provider]:
            raise KeyError(f"Pass not found: {provider}/{pass_id}")
        
        logger.debug(f"Retrieved {provider} pass {pass_id} from memory")
        return self.passes[provider][pass_id]
    
    def delete_pass(self, provider: str, pass_id: str) -> bool:
        """Delete pass data from memory."""
        if provider not in self.passes or pass_id not in self.passes[provider]:
            logger.warning(f"Pass not found for deletion: {provider}/{pass_id}")
            return False
        
        del self.passes[provider][pass_id]
        logger.debug(f"Deleted {provider} pass {pass_id} from memory")
        return True
    
    def list_passes(self, provider: str) -> List[str]:
        """List all pass IDs stored in memory."""
        if provider not in self.passes:
            return []
        
        return list(self.passes[provider].keys())


# Factory function to create a storage backend
def create_storage_backend(storage_type: str, **kwargs) -> StorageBackend:
    """
    Create a storage backend instance.
    
    Args:
        storage_type: Type of storage ('filesystem', 'memory', or custom)
        **kwargs: Additional arguments for the storage backend
    
    Returns:
        A StorageBackend instance
    """
    if storage_type == 'filesystem':
        if 'storage_path' not in kwargs:
            raise ValueError("storage_path is required for filesystem storage")
        
        return FileSystemStorage(kwargs['storage_path'])
    
    elif storage_type == 'memory':
        return MemoryStorage()
    
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
