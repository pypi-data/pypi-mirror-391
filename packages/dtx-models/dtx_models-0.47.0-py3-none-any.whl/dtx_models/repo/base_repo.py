"""
Base repository class for managing collections of objects with lazy loading.
"""

import os
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository class that provides common functionality for managing collections of objects.
    Supports lazy loading, listing, and retrieval by name.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            data_dir: Optional directory path for data files. If None, uses default location.
        """
        self._cache: Dict[str, T] = {}
        self._loaded = False
        self._data_dir = data_dir or self._get_default_data_dir()
        
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for this repository."""
        # Default to the repo directory
        return str(Path(__file__).parent)
    
    @abstractmethod
    def _load_item(self, name: str, data: Dict[str, Any]) -> T:
        """
        Load a single item from its data dictionary.
        
        Args:
            name: The name/identifier of the item
            data: The data dictionary for the item
            
        Returns:
            The loaded item
        """
        pass
    
    @abstractmethod
    def _get_data_files(self) -> List[str]:
        """
        Get the list of data files to load from.
        
        Returns:
            List of file paths to load data from
        """
        pass
    
    def _load_all(self) -> None:
        """Load all items from data files."""
        if self._loaded:
            return
            
        for data_file in self._get_data_files():
            if os.path.exists(data_file):
                self._load_from_file(data_file)
        
        self._loaded = True
    
    def _load_from_file(self, file_path: str) -> None:
        """Load items from a YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if isinstance(data, dict) and 'items' in data:
                # Handle structured format with 'items' key
                items = data['items']
            elif isinstance(data, list):
                # Handle direct list format
                items = data
            else:
                # Handle single item format
                items = [data] if data else []
            
            for item_data in items:
                if isinstance(item_data, dict) and 'name' in item_data:
                    name = item_data['name']
                    self._cache[name] = self._load_item(name, item_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load data from {file_path}: {e}")
    
    def get(self, name: str) -> Optional[T]:
        """
        Get an item by name.
        
        Args:
            name: The name of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        if not self._loaded:
            self._load_all()
        
        return self._cache.get(name)
    
    def list_all(self) -> List[T]:
        """
        List all items in the repository.
        
        Returns:
            List of all items
        """
        if not self._loaded:
            self._load_all()
        
        return list(self._cache.values())
    
    def list_names(self) -> List[str]:
        """
        List all item names in the repository.
        
        Returns:
            List of all item names
        """
        if not self._loaded:
            self._load_all()
        
        return list(self._cache.keys())
    
    def exists(self, name: str) -> bool:
        """
        Check if an item exists by name.
        
        Args:
            name: The name of the item to check
            
        Returns:
            True if the item exists, False otherwise
        """
        if not self._loaded:
            self._load_all()
        
        return name in self._cache
    
    def count(self) -> int:
        """
        Get the total number of items in the repository.
        
        Returns:
            Number of items
        """
        if not self._loaded:
            self._load_all()
        
        return len(self._cache)
    
    def clear_cache(self) -> None:
        """Clear the internal cache and force reload on next access."""
        self._cache.clear()
        self._loaded = False
    
    def reload(self) -> None:
        """Reload all data from files."""
        self.clear_cache()
        self._load_all()
