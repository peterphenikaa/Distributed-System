"""
Storage Engine - In-memory key-value store with thread safety
"""

import threading
from typing import Tuple, List, Optional


class StorageEngine:
    """
    Thread-safe in-memory storage using dict + RLock.
    
    Supports:
    - PUT: Save key-value pair
    - GET: Retrieve value by key
    - DELETE: Remove key
    - LIST: Get all keys
    """
    
    def __init__(self):
        """Initialize storage with empty dict and RLock."""
        self.storage = {}  # key -> value mapping
        self.lock = threading.RLock()  # Reentrant lock for thread safety
    
    def put(self, key: str, value: str) -> bool:
        """
        Save key-value pair to storage.
        
        Args:
            key: Key to save
            value: Value to save
        
        Returns:
            True if saved successfully
        """
        try:
            with self.lock:
                self.storage[key] = value
            return True
        except Exception as e:
            raise Exception(f"PUT failed: {str(e)}")
    
    def get(self, key: str) -> Tuple[Optional[str], bool]:
        """
        Retrieve value from storage by key.
        
        Args:
            key: Key to retrieve
        
        Returns:
            Tuple of (value, found)
            - value: The stored value (or None if not found)
            - found: True if key exists, False otherwise
        """
        try:
            with self.lock:
                if key in self.storage:
                    return self.storage[key], True
                else:
                    return None, False
        except Exception as e:
            raise Exception(f"GET failed: {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        Delete key from storage (idempotent).
        
        Args:
            key: Key to delete
        
        Returns:
            True if key was found and deleted, False if key didn't exist
        """
        try:
            with self.lock:
                if key in self.storage:
                    del self.storage[key]
                    return True
                else:
                    return False
        except Exception as e:
            raise Exception(f"DELETE failed: {str(e)}")
    
    def list_keys(self) -> List[str]:
        """
        Get list of all keys in storage.
        
        Returns:
            List of all keys
        """
        try:
            with self.lock:
                return list(self.storage.keys())
        except Exception as e:
            raise Exception(f"LISTKEYS failed: {str(e)}")
    
    def size(self) -> int:
        """Get total number of keys in storage."""
        with self.lock:
            return len(self.storage)
    
    def clear(self) -> None:
        """Clear all storage (for testing)."""
        with self.lock:
            self.storage.clear()
