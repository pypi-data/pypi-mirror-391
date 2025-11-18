"""
Converter repository for managing converter definitions.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.converter import AnyConverter, StaticConverter, LLMConverter, DynamicCodeConverter


class ConverterRepository(BaseRepository[AnyConverter]):
    """
    Repository for managing converter definitions with lazy loading.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the converter repository.
        
        Args:
            data_dir: Optional directory path for converter data files
        """
        super().__init__(data_dir)
        self._converters_file = os.path.join(self._data_dir, "prompt_canvas", "converters.yml")
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for converter repository."""
        # Override to use data/ subdirectory instead of repo directory
        return str(Path(__file__).parent / "data")
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> AnyConverter:
        """Load a converter from its data dictionary."""
        converter_type = data.get('converter_type', 'static')
        
        if converter_type == 'static':
            return StaticConverter(**data)
        elif converter_type == 'llm':
            return LLMConverter(**data)
        elif converter_type == 'dynamic_code':
            return DynamicCodeConverter(**data)
        else:
            raise ValueError(f"Unknown converter type: {converter_type}")
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        
        if os.path.exists(self._converters_file):
            files.append(self._converters_file)
        
        return files
    
    def _load_from_file(self, file_path: str) -> None:
        """Load converters from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and 'converters' in data:
                converters = data['converters']
            elif isinstance(data, list):
                converters = data
            else:
                converters = [data] if data else []
            
            for converter_data in converters:
                if isinstance(converter_data, dict) and 'name' in converter_data:
                    name = converter_data['name']
                    self._cache[name] = self._load_item(name, converter_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load converters from {file_path}: {e}")
    
    def get_static_converters(self) -> List[StaticConverter]:
        """Get all static converters."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if isinstance(converter, StaticConverter)]
    
    def get_llm_converters(self) -> List[LLMConverter]:
        """Get all LLM converters."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if isinstance(converter, LLMConverter)]
    
    def get_dynamic_code_converters(self) -> List[DynamicCodeConverter]:
        """Get all dynamic code converters."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if isinstance(converter, DynamicCodeConverter)]
    
    def get_by_type(self, converter_type: str) -> List[AnyConverter]:
        """Get all converters of a specific type."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if converter.converter_type == converter_type]
    
    def get_by_class_name(self, class_name: str) -> List[AnyConverter]:
        """Get all converters that use a specific class name."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if hasattr(converter, 'class_name') and converter.class_name == class_name]
    
    def get_by_target(self, target: str) -> List[LLMConverter]:
        """Get all LLM converters that use a specific target."""
        if not self._loaded:
            self._load_all()
        
        return [converter for converter in self._cache.values() 
                if isinstance(converter, LLMConverter) and converter.converter_target == target]
