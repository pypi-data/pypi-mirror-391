"""
Attack Recipes Repository

This module provides a repository for managing attack recipe definitions with lazy loading.
Attack recipes combine attack strategies with seed prompts/behaviors into complete configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_repo import BaseRepository
from ..prompt_canvas.workflows.attack_recipes import AttackRecipe, create_attack_recipe_schema


class AttackRecipesRepository(BaseRepository[AttackRecipe]):
    """
    Repository for managing attack recipe definitions with lazy loading.
    
    Attack recipes are complete, ready-to-execute configurations that combine:
    - Attack strategies with their configurations
    - Seed prompts or behaviors
    - Execution parameters
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the attack recipes repository.
        
        Args:
            data_dir: Optional directory path for attack recipe data files
        """
        super().__init__(data_dir)
        self._attack_recipes_file = os.path.join(self._data_dir, "prompt_canvas", "attack_recipes.yml")

    def _get_default_data_dir(self) -> str:
        """Get the default data directory for attack recipes repository."""
        return str(Path(__file__).parent / "data")

    def _load_item(self, name: str, data: Dict[str, Any]) -> AttackRecipe:
        """Load an attack recipe from its data dictionary."""
        try:
            return create_attack_recipe_schema(data)
        except Exception as e:
            raise ValueError(f"Failed to load attack recipe '{name}': {e}")

    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        files = []
        if os.path.exists(self._attack_recipes_file):
            files.append(self._attack_recipes_file)
        return files

    # --- Filtering and Search Methods ---

    def get_by_attack_strategy(self, strategy_name: str) -> List[AttackRecipe]:
        """Get attack recipes by their attack strategy."""
        self._load_all()
        return [r for r in self._cache.values() if r.attack_strategy.name == strategy_name]

    def get_by_tag(self, tag: str) -> List[AttackRecipe]:
        """Get attack recipes by a specific tag."""
        self._load_all()
        return [r for r in self._cache.values() if r.tags and tag in r.tags]

    def get_by_author(self, author: str) -> List[AttackRecipe]:
        """Get attack recipes by author."""
        self._load_all()
        return [r for r in self._cache.values() if r.author and author.lower() in r.author.lower()]

    def search_by_keyword(self, keyword: str) -> List[AttackRecipe]:
        """Search for attack recipes by keyword in name, description, or tags."""
        self._load_all()
        keyword_lower = keyword.lower()
        return [
            r
            for r in self._cache.values()
            if keyword_lower in r.name.lower()
            or (r.description and keyword_lower in r.description.lower())
            or (r.tags and any(keyword_lower in t.lower() for t in r.tags))
        ]

    def get_with_seed_prompts(self) -> List[AttackRecipe]:
        """Get attack recipes that have seed prompts."""
        self._load_all()
        return [r for r in self._cache.values() if r.seed_prompts]

    def get_with_behaviors(self) -> List[AttackRecipe]:
        """Get attack recipes that have behaviors."""
        self._load_all()
        return [r for r in self._cache.values() if r.behaviors]

    def get_by_complexity(self, complexity: str) -> List[AttackRecipe]:
        """
        Get attack recipes by complexity level.
        
        Args:
            complexity: One of 'simple', 'medium', 'complex'
        """
        self._load_all()
        
        def get_recipe_complexity(recipe: AttackRecipe) -> str:
            """Determine recipe complexity based on its components."""
            score = 0
            
            # Base complexity from attack strategy
            if recipe.attack_strategy.name in ['crescendo-attack', 'red-teaming-attack', 'tap-attack']:
                score += 3
            elif recipe.attack_strategy.name in ['skeleton-key-attack', 'flip-attack']:
                score += 1
            else:
                score += 2
            
            # Add complexity for seed prompts
            if recipe.seed_prompts:
                if isinstance(recipe.seed_prompts, list):
                    score += len(recipe.seed_prompts)
                else:
                    score += 1
            
            # Add complexity for behaviors
            if recipe.behaviors:
                if isinstance(recipe.behaviors, list):
                    score += len(recipe.behaviors)
                else:
                    score += 1
            
            # Add complexity for execution config
            if recipe.execution_config:
                if recipe.execution_config.timeout_seconds and recipe.execution_config.timeout_seconds > 300:
                    score += 1
                if recipe.execution_config.retry_attempts and recipe.execution_config.retry_attempts > 2:
                    score += 1
            
            if score <= 2:
                return 'simple'
            elif score <= 5:
                return 'medium'
            else:
                return 'complex'
        
        return [r for r in self._cache.values() if get_recipe_complexity(r) == complexity]

    # --- Recipe Analysis Methods ---

    def get_recipe_components(self, name: str) -> Dict[str, Any]:
        """
        Get detailed component information for a recipe.
        
        Args:
            name: Name of the recipe
            
        Returns:
            Dictionary with component details
        """
        recipe = self.get(name)
        if not recipe:
            return {}
        
        components = {
            'attack_strategy': recipe.attack_strategy.name,
            'seed_prompts': [],
            'behaviors': [],
            'execution_config': {}
        }
        
        # Analyze seed prompts
        if recipe.seed_prompts:
            if isinstance(recipe.seed_prompts, list):
                for prompt in recipe.seed_prompts:
                    if isinstance(prompt, str):
                        components['seed_prompts'].append({'content': prompt})
                    else:
                        components['seed_prompts'].append({
                            'name': prompt.name,
                            'content': prompt.content,
                            'description': prompt.description,
                            'category': prompt.category
                        })
            else:
                components['seed_prompts'].append({'content': recipe.seed_prompts})
        
        # Analyze behaviors
        if recipe.behaviors:
            if isinstance(recipe.behaviors, list):
                for behavior in recipe.behaviors:
                    components['behaviors'].append({
                        'name': behavior.name,
                        'description': behavior.description,
                        'parameters': behavior.parameters,
                        'category': behavior.category
                    })
            else:
                components['behaviors'].append({
                    'name': recipe.behaviors.name,
                    'description': recipe.behaviors.description,
                    'parameters': recipe.behaviors.parameters,
                    'category': recipe.behaviors.category
                })
        
        # Analyze execution config
        if recipe.execution_config:
            components['execution_config'] = {
                'timeout_seconds': recipe.execution_config.timeout_seconds,
                'retry_attempts': recipe.execution_config.retry_attempts
            }
        
        return components

    def validate_recipe_config(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Validate a recipe configuration against its schema.
        
        Args:
            name: Name of the recipe
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        recipe = self.get(name)
        if not recipe:
            return False
        
        try:
            # Create a temporary recipe with the provided config
            recipe_data = recipe.model_dump()
            recipe_data.update(config)
            AttackRecipe(**recipe_data)
            return True
        except Exception:
            return False

    def get_recipe_dependencies(self, name: str) -> Dict[str, List[str]]:
        """
        Get dependencies for a recipe (attack strategies, etc.).
        
        Args:
            name: Name of the recipe
            
        Returns:
            Dictionary with dependency lists
        """
        recipe = self.get(name)
        if not recipe:
            return {}
        
        dependencies = {
            'attack_strategies': [recipe.attack_strategy.name],
            'converters': [],
            'scorers': [],
            'targets': []
        }
        
        # Extract dependencies from attack strategy config
        strategy_config = recipe.attack_strategy.config
        
        # Get converter dependencies
        if 'attack_converter_config' in strategy_config:
            converters = strategy_config['attack_converter_config'].get('converters', [])
            for converter in converters:
                dependencies['converters'].append(converter['name'])
        
        # Get scorer dependencies
        if 'scoring_config' in strategy_config:
            scorer = strategy_config['scoring_config'].get('scorer', {})
            if scorer:
                dependencies['scorers'].append(scorer['name'])
        
        # Get target dependencies
        if 'objective_target' in strategy_config:
            target = strategy_config['objective_target']
            dependencies['targets'].append(target['name'])
        
        return dependencies

    def get_recipe_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about attack recipes."""
        self._load_all()
        
        if not self._cache:
            return {'total': 0}
        
        stats = {
            'total': len(self._cache),
            'by_attack_strategy': {},
            'by_complexity': {'simple': 0, 'medium': 0, 'complex': 0},
            'by_author': {},
            'with_seed_prompts': 0,
            'with_behaviors': 0,
            'avg_components': 0
        }
        
        total_components = 0
        
        for recipe in self._cache.values():
            # Count by attack strategy
            strategy = recipe.attack_strategy.name
            stats['by_attack_strategy'][strategy] = stats['by_attack_strategy'].get(strategy, 0) + 1
            
            # Count by complexity
            complexity = self._get_recipe_complexity(recipe)
            stats['by_complexity'][complexity] += 1
            
            # Count by author
            if recipe.author:
                author = recipe.author
                stats['by_author'][author] = stats['by_author'].get(author, 0) + 1
            
            # Count seed prompts and behaviors
            if recipe.seed_prompts:
                stats['with_seed_prompts'] += 1
            
            if recipe.behaviors:
                stats['with_behaviors'] += 1
            
            # Count components
            component_count = 1  # attack strategy
            if recipe.seed_prompts:
                if isinstance(recipe.seed_prompts, list):
                    component_count += len(recipe.seed_prompts)
                else:
                    component_count += 1
            if recipe.behaviors:
                if isinstance(recipe.behaviors, list):
                    component_count += len(recipe.behaviors)
                else:
                    component_count += 1
            
            total_components += component_count
        
        if self._cache:
            stats['avg_components'] = total_components / len(self._cache)
        
        return stats

    def _get_recipe_complexity(self, recipe: AttackRecipe) -> str:
        """Helper method to determine recipe complexity."""
        score = 0
        
        # Base complexity from attack strategy
        if recipe.attack_strategy.name in ['crescendo-attack', 'red-teaming-attack', 'tap-attack']:
            score += 3
        elif recipe.attack_strategy.name in ['skeleton-key-attack', 'flip-attack']:
            score += 1
        else:
            score += 2
        
        # Add complexity for seed prompts
        if recipe.seed_prompts:
            if isinstance(recipe.seed_prompts, list):
                score += len(recipe.seed_prompts)
            else:
                score += 1
        
        # Add complexity for behaviors
        if recipe.behaviors:
            if isinstance(recipe.behaviors, list):
                score += len(recipe.behaviors)
            else:
                score += 1
        
        # Add complexity for execution config
        if recipe.execution_config:
            if recipe.execution_config.timeout_seconds and recipe.execution_config.timeout_seconds > 300:
                score += 1
            if recipe.execution_config.retry_attempts and recipe.execution_config.retry_attempts > 2:
                score += 1
        
        if score <= 2:
            return 'simple'
        elif score <= 5:
            return 'medium'
        else:
            return 'complex'
