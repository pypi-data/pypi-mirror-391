"""
Behavior repository for managing behavior definitions from various sources.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.behavior import Behavior


class BehaviorRepository(BaseRepository[Behavior]):
    """
    Repository for managing behavior definitions from harmbench, advbench, and other sources.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the behavior repository.
        
        Args:
            data_dir: Optional directory path for behavior data files
        """
        super().__init__(data_dir)
        self._harmbench_file = os.path.join(self._data_dir, "prompt_canvas", "harmbench_behaviors.yml")
        self._advbench_file = os.path.join(self._data_dir, "prompt_canvas", "advbench_behaviors.yml")
        self._behaviors_file = os.path.join(self._data_dir, "prompt_canvas", "behaviors.yml")
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for behavior repository."""
        # Override to use data/ subdirectory instead of repo directory
        return str(Path(__file__).parent / "data")
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> Behavior:
        """Load a behavior from its data dictionary."""
        return Behavior(**data)
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        
        # Add YAML behavior files
        if os.path.exists(self._behaviors_file):
            files.append(self._behaviors_file)
        if os.path.exists(self._harmbench_file):
            files.append(self._harmbench_file)
        if os.path.exists(self._advbench_file):
            files.append(self._advbench_file)
        
        return files
    
    def _load_from_file(self, file_path: str) -> None:
        """Load behaviors from YAML files."""
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            self._load_from_yaml(file_path)
    
    def _load_from_yaml(self, file_path: str) -> None:
        """Load behaviors from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and 'behaviors' in data:
                behaviors = data['behaviors']
            elif isinstance(data, list):
                behaviors = data
            else:
                behaviors = [data] if data else []
            
            for behavior_data in behaviors:
                if isinstance(behavior_data, dict) and 'name' in behavior_data:
                    name = behavior_data['name']
                    self._cache[name] = Behavior(**behavior_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load behaviors from {file_path}: {e}")
    
    
    
    def get_by_policy(self, policy: str) -> List[Behavior]:
        """Get all behaviors that have a specific policy."""
        if not self._loaded:
            self._load_all()
        
        return [behavior for behavior in self._cache.values() 
                if policy in behavior.policies]
    
    def get_by_tag(self, tag: str) -> List[Behavior]:
        """Get all behaviors that have a specific tag."""
        if not self._loaded:
            self._load_all()
        
        return [behavior for behavior in self._cache.values() 
                if tag in behavior.tags]
