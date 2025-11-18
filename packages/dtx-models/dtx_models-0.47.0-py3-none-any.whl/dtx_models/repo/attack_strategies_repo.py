"""
Attack strategies repository for managing attack strategy definitions.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.attack_strategies.jailbreaks import AttackStrategy


class AttackStrategiesRepository(BaseRepository[AttackStrategy]):
    """
    Repository for managing attack strategy definitions with lazy loading.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the attack strategies repository.
        
        Args:
            data_dir: Optional directory path for attack strategy data files
        """
        super().__init__(data_dir)
        self._attack_strategies_file = os.path.join(self._data_dir, "prompt_canvas", "attack_strategies.yml")
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for attack strategies repository."""
        # Override to use data/ subdirectory instead of repo directory
        return str(Path(__file__).parent / "data")
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> AttackStrategy:
        """Load an attack strategy from its data dictionary."""
        try:
            return AttackStrategy(**data)
        except Exception as e:
            raise ValueError(f"Failed to load attack strategy '{name}': {e}")
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        
        if os.path.exists(self._attack_strategies_file):
            files.append(self._attack_strategies_file)
        
        return files
    
    def _load_from_file(self, file_path: str) -> None:
        """Load attack strategies from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if isinstance(data, list):
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
            print(f"Warning: Failed to load attack strategies from {file_path}: {e}")
    
    def get_by_strategy_type(self, strategy_type: str) -> List[AttackStrategy]:
        """
        Get all attack strategies of a specific type.
        
        Args:
            strategy_type: The type of attack strategy to filter by
            
        Returns:
            List of attack strategies matching the type
        """
        if not self._loaded:
            self._load_all()
        
        return [
            strategy for strategy in self._cache.values()
            if strategy.strategy_type == strategy_type
        ]
    
    def get_by_tag(self, tag: str) -> List[AttackStrategy]:
        """
        Get all attack strategies that have a specific tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            List of attack strategies containing the tag
        """
        if not self._loaded:
            self._load_all()
        
        return [
            strategy for strategy in self._cache.values()
            if hasattr(strategy, 'tags') and tag in strategy.tags
        ]
    
    def search_by_keyword(self, keyword: str) -> List[AttackStrategy]:
        """
        Search attack strategies by keyword in name, description, or tags.
        
        Args:
            keyword: The keyword to search for
            
        Returns:
            List of attack strategies matching the keyword
        """
        if not self._loaded:
            self._load_all()
        
        keyword_lower = keyword.lower()
        matches = []
        
        for strategy in self._cache.values():
            # Search in name
            if keyword_lower in strategy.name.lower():
                matches.append(strategy)
                continue
            
            # Search in description
            if strategy.description and keyword_lower in strategy.description.lower():
                matches.append(strategy)
                continue
            
            # Search in tags
            if hasattr(strategy, 'tags') and strategy.tags:
                if any(keyword_lower in tag.lower() for tag in strategy.tags):
                    matches.append(strategy)
                    continue
        
        return matches
    
    def get_required_parameters(self, name: str) -> List[str]:
        """
        Get the required parameters for a specific attack strategy.
        
        Args:
            name: The name of the attack strategy
            
        Returns:
            List of required parameter names
        """
        strategy = self.get(name)
        if strategy is None:
            return []
        
        return strategy.parameters
    
    def get_parameter_schema(self, name: str) -> List[Dict[str, Any]]:
        """
        Get the parameter schema for a specific attack strategy.
        
        Args:
            name: The name of the attack strategy
            
        Returns:
            List of parameter schema dictionaries
        """
        strategy = self.get(name)
        if strategy is None:
            return []
        
        return [param.model_dump() for param in strategy.parameters_schema]
    
    def validate_strategy_config(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against an attack strategy's schema.
        
        Args:
            name: The name of the attack strategy
            config: The configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        strategy = self.get(name)
        if strategy is None:
            return False
        
        # Check if all required parameters are present
        required_params = set(strategy.parameters)
        config_params = set(config.keys())
        
        if not required_params.issubset(config_params):
            return False
        
        # Additional validation could be added here
        # For now, we'll just check parameter presence
        return True
