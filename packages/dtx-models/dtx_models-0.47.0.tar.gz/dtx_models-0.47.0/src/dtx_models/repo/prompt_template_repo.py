"""
Prompt template repository for managing converter prompt templates.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.prompt_templates.converter_prompts import ConverterPromptTemplate


class PromptTemplateRepository(BaseRepository[ConverterPromptTemplate]):
    """
    Repository for managing converter prompt templates with lazy loading.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the prompt template repository.
        
        Args:
            data_dir: Optional directory path for template data files
        """
        super().__init__(data_dir)
        self._templates_file = os.path.join(self._data_dir, "prompt_canvas", "prompt_templates.yml")
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for prompt template repository."""
        # Override to use data/ subdirectory instead of repo directory
        return str(Path(__file__).parent / "data")
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> ConverterPromptTemplate:
        """Load a prompt template from its data dictionary."""
        return ConverterPromptTemplate(**data)
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        
        if os.path.exists(self._templates_file):
            files.append(self._templates_file)
        
        return files
    
    def _load_from_file(self, file_path: str) -> None:
        """Load prompt templates from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and 'templates' in data:
                templates = data['templates']
            elif isinstance(data, list):
                templates = data
            else:
                templates = [data] if data else []
            
            for template_data in templates:
                if isinstance(template_data, dict) and 'name' in template_data:
                    name = template_data['name']
                    self._cache[name] = ConverterPromptTemplate(**template_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load prompt templates from {file_path}: {e}")
    
    def get_by_type(self, template_type: str) -> List[ConverterPromptTemplate]:
        """Get all templates of a specific type."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if template.type == template_type]
    
    def get_by_author(self, author: str) -> List[ConverterPromptTemplate]:
        """Get all templates by a specific author."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if author in template.authors]
    
    def get_by_group(self, group: str) -> List[ConverterPromptTemplate]:
        """Get all templates in a specific group."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if group in template.groups]
    
    def get_by_source(self, source: str) -> List[ConverterPromptTemplate]:
        """Get all templates from a specific source."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if template.source == source]
    
    def search_by_parameter(self, parameter: str) -> List[ConverterPromptTemplate]:
        """Get all templates that use a specific parameter."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if parameter in template.parameters]
    
    def get_templates_with_parameter_count(self, count: int) -> List[ConverterPromptTemplate]:
        """Get all templates with a specific number of parameters."""
        if not self._loaded:
            self._load_all()
        
        return [template for template in self._cache.values() 
                if len(template.parameters) == count]
