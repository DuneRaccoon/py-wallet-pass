"""Tests for storage backends."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from wallet_pass.storage import FileSystemStorage, MemoryStorage


def test_memory_storage():
    """Test the in-memory storage backend."""
    storage = MemoryStorage()
    
    # Test storing and retrieving pass data
    provider = "test"
    pass_id = "test-123"
    pass_data = {"id": pass_id, "value": "test-value"}
    
    storage.store_pass(provider, pass_id, pass_data)
    retrieved_data = storage.retrieve_pass(provider, pass_id)
    
    assert retrieved_data == pass_data
    
    # Test listing passes
    assert storage.list_passes(provider) == [pass_id]
    
    # Test deleting a pass
    assert storage.delete_pass(provider, pass_id) is True
    assert storage.list_passes(provider) == []
    
    # Test retrieving a non-existent pass
    with pytest.raises(KeyError):
        storage.retrieve_pass(provider, pass_id)
    
    # Test deleting a non-existent pass
    assert storage.delete_pass(provider, pass_id) is False


def test_filesystem_storage():
    """Test the filesystem storage backend."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = FileSystemStorage(temp_dir)
        
        # Test storing and retrieving pass data
        provider = "test"
        pass_id = "test-123"
        pass_data = {"id": pass_id, "value": "test-value"}
        
        storage.store_pass(provider, pass_id, pass_data)
        
        # Check that the file was created
        pass_path = Path(temp_dir) / provider / "passes" / f"{pass_id}.json"
        assert pass_path.exists()
        
        # Check the file content
        with open(pass_path, 'r') as f:
            stored_data = json.load(f)
            assert stored_data == pass_data
        
        # Test retrieving the pass
        retrieved_data = storage.retrieve_pass(provider, pass_id)
        assert retrieved_data == pass_data
        
        # Test listing passes
        assert storage.list_passes(provider) == [pass_id]
        
        # Test deleting a pass
        assert storage.delete_pass(provider, pass_id) is True
        assert not pass_path.exists()
        assert storage.list_passes(provider) == []
        
        # Test retrieving a non-existent pass
        with pytest.raises(FileNotFoundError):
            storage.retrieve_pass(provider, pass_id)
        
        # Test deleting a non-existent pass
        assert storage.delete_pass(provider, pass_id) is False