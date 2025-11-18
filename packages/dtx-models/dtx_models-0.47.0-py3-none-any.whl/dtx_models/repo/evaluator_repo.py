"""
Evaluator repository for managing evaluator definitions.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.scorers.evaluators import AnyScorerSchema, create_scorer_schema


class EvaluatorRepository(BaseRepository[AnyScorerSchema]):
    """
    Repository for managing evaluator definitions with lazy loading.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the evaluator repository.
        
        Args:
            data_dir: Optional directory path for evaluator data files
        """
        super().__init__(data_dir)
        self._evaluators_file = os.path.join(self._data_dir, "prompt_canvas", "evaluators.yml")
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for evaluator repository."""
        # Override to use data/ subdirectory instead of repo directory
        return str(Path(__file__).parent / "data")
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> AnyScorerSchema:
        """Load an evaluator from its data dictionary."""
        return create_scorer_schema(data)
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        
        if os.path.exists(self._evaluators_file):
            files.append(self._evaluators_file)
        
        return files
    
    def _load_from_file(self, file_path: str) -> None:
        """Load evaluators from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and 'evaluators' in data:
                evaluators = data['evaluators']
            elif isinstance(data, list):
                evaluators = data
            else:
                evaluators = [data] if data else []
            
            for evaluator_data in evaluators:
                if isinstance(evaluator_data, dict) and 'name' in evaluator_data:
                    name = evaluator_data['name']
                    self._cache[name] = self._load_item(name, evaluator_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load evaluators from {file_path}: {e}")
    
    def get_static_evaluators(self) -> List[AnyScorerSchema]:
        """Get all static evaluators (non-LLM)."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'type') and evaluator.type == 'static']
    
    def get_llm_static_evaluators(self) -> List[AnyScorerSchema]:
        """Get all LLM-static evaluators."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'type') and evaluator.type == 'llm-static']
    
    def get_llm_evaluators(self) -> List[AnyScorerSchema]:
        """Get all LLM evaluators."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'type') and evaluator.type == 'llm']
    
    def get_by_type(self, evaluator_type: str) -> List[AnyScorerSchema]:
        """Get all evaluators of a specific type."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'type') and evaluator.type == evaluator_type]
    
    def get_by_scorer_type(self, scorer_type: str) -> List[AnyScorerSchema]:
        """Get all evaluators that produce a specific scorer type (true_false or float_scale)."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'scorer_type') and evaluator.scorer_type == scorer_type]
    
    def get_by_tag(self, tag: str) -> List[AnyScorerSchema]:
        """Get all evaluators that have a specific tag."""
        if not self._loaded:
            self._load_all()
        
        return [evaluator for evaluator in self._cache.values() 
                if hasattr(evaluator, 'tags') and tag in evaluator.tags]
    
    def search_by_name(self, query: str) -> List[AnyScorerSchema]:
        """Search evaluators by name (case-insensitive partial match)."""
        if not self._loaded:
            self._load_all()
        
        query_lower = query.lower()
        return [evaluator for evaluator in self._cache.values() 
                if query_lower in evaluator.name.lower()]
    
    def search_by_description(self, query: str) -> List[AnyScorerSchema]:
        """Search evaluators by description (case-insensitive partial match)."""
        if not self._loaded:
            self._load_all()
        
        query_lower = query.lower()
        return [evaluator for evaluator in self._cache.values() 
                if query_lower in evaluator.description.lower()]
