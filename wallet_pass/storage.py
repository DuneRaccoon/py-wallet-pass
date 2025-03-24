"""Storage backends for wallet passes."""

import abc
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logging import get_logger, with_context

logger = get_logger(__name__)


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
        
        context = with_context(provider=provider, pass_id=pass_id, path=str(pass_path))
        logger.bind(**context).debug("✅ Stored pass data to filesystem")
    
    def retrieve_pass(self, provider: str, pass_id: str) -> Dict[str, Any]:
        """Retrieve pass data from the file system."""
        pass_path = self.storage_path / provider / "passes" / f"{pass_id}.json"
        
        if not pass_path.exists():
            context = with_context(provider=provider, pass_id=pass_id, path=str(pass_path))
            logger.bind(**context).error("❌ Pass file not found")
            raise FileNotFoundError(f"Pass not found: {pass_id}")
        
        with open(pass_path, 'r') as f:
            pass_data = json.load(f)
        
        context = with_context(provider=provider, pass_id=pass_id, path=str(pass_path))
        logger.bind(**context).debug("✅ Retrieved pass data from filesystem")
        
        return pass_data
    
    def delete_pass(self, provider: str, pass_id: str) -> bool:
        """Delete pass data from the file system."""
        pass_path = self.storage_path / provider / "passes" / f"{pass_id}.json"
        context = with_context(provider=provider, pass_id=pass_id, path=str(pass_path))
        
        if not pass_path.exists():
            logger.bind(**context).warning("⚠️ Pass not found for deletion")
            return False
        
        os.remove(pass_path)
        logger.bind(**context).info("🗑️ Deleted pass from filesystem")
        
        return True
    
    def list_passes(self, provider: str) -> List[str]:
        """List all pass IDs stored in the file system."""
        provider_dir = self.storage_path / provider / "passes"
        context = with_context(provider=provider, directory=str(provider_dir))
        
        if not provider_dir.exists():
            logger.bind(**context).debug("ℹ️ Provider directory does not exist")
            return []
        
        pass_ids = []
        for file_path in provider_dir.glob("*.json"):
            pass_id = file_path.stem
            pass_ids.append(pass_id)
        
        logger.bind(**context).debug(f"📃 Found {len(pass_ids)} passes")
        
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
        context = with_context(provider=provider, pass_id=pass_id)
        logger.bind(**context).debug("✅ Stored pass data in memory")
    
    def retrieve_pass(self, provider: str, pass_id: str) -> Dict[str, Any]:
        """Retrieve pass data from memory."""
        context = with_context(provider=provider, pass_id=pass_id)
        
        if provider not in self.passes or pass_id not in self.passes[provider]:
            logger.bind(**context).error("❌ Pass not found in memory storage")
            raise KeyError(f"Pass not found: {provider}/{pass_id}")
        
        logger.bind(**context).debug("✅ Retrieved pass data from memory")
        return self.passes[provider][pass_id]
    
    def delete_pass(self, provider: str, pass_id: str) -> bool:
        """Delete pass data from memory."""
        context = with_context(provider=provider, pass_id=pass_id)
        
        if provider not in self.passes or pass_id not in self.passes[provider]:
            logger.bind(**context).warning("⚠️ Pass not found for deletion in memory")
            return False
        
        del self.passes[provider][pass_id]
        logger.bind(**context).info("🗑️ Deleted pass from memory")
        return True
    
    def list_passes(self, provider: str) -> List[str]:
        """List all pass IDs stored in memory."""
        context = with_context(provider=provider)
        
        if provider not in self.passes:
            logger.bind(**context).debug("ℹ️ No passes found for provider in memory")
            return []
        
        pass_ids = list(self.passes[provider].keys())
        logger.bind(**context).debug(f"📃 Found {len(pass_ids)} passes in memory")
        return pass_ids


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
