"""
Repository factory for managing all repositories with lazy loading.
"""

from typing import Optional

from .base_repo import BaseRepository
from .behavior_repo import BehaviorRepository
from .converter_repo import ConverterRepository
from .evaluator_repo import EvaluatorRepository
from .prompt_template_repo import PromptTemplateRepository
from .converter_prompt_template_repo import ConverterPromptTemplateRepository
from .attack_strategies_repo import AttackStrategiesRepository
from .attack_recipes_repo import AttackRecipesRepository
from .campaigns_repo import (
    CampaignObjectiveRepository,
    RunbookObjectiveRepository,
    AttackLibraryRepository,
    ManipulatorRepository,
    EvaluatorRepository as CampaignEvaluatorRepository,
    RunbookTemplateRepository,
    AITargetTypeRepository,
    CampaignTypeRepository,
    get_campaign_objective_repository,
    get_runbook_objective_repository,
    get_attack_library_repository,
    get_manipulator_repository,
    get_evaluator_repository as get_campaign_evaluator_repository,
    get_runbook_template_repository,
    get_ai_target_type_repository,
    get_campaign_type_repository,
)


class RepositoryFactory:
    """
    Factory class for managing all repositories with lazy initialization.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the repository factory.
        
        Args:
            data_dir: Optional base directory for all repositories
        """
        self._data_dir = data_dir
        # Prompt Canvas repositories
        self._behavior_repo: Optional[BehaviorRepository] = None
        self._converter_repo: Optional[ConverterRepository] = None
        self._evaluator_repo: Optional[EvaluatorRepository] = None
        self._template_repo: Optional[PromptTemplateRepository] = None
        self._converter_template_repo: Optional[ConverterPromptTemplateRepository] = None
        self._attack_strategies_repo: Optional[AttackStrategiesRepository] = None
        self._attack_recipes_repo: Optional[AttackRecipesRepository] = None
        # Campaign repositories
        self._campaign_objective_repo: Optional[CampaignObjectiveRepository] = None
        self._runbook_objective_repo: Optional[RunbookObjectiveRepository] = None
        self._attack_library_repo: Optional[AttackLibraryRepository] = None
        self._manipulator_repo: Optional[ManipulatorRepository] = None
        self._campaign_evaluator_repo: Optional[CampaignEvaluatorRepository] = None
        self._runbook_template_repo: Optional[RunbookTemplateRepository] = None
        self._ai_target_type_repo: Optional[AITargetTypeRepository] = None
        self._campaign_type_repo: Optional[CampaignTypeRepository] = None
    
    # Prompt Canvas repositories
    @property
    def behaviors(self) -> BehaviorRepository:
        """Get the behavior repository (prompt canvas, lazy loaded)."""
        if self._behavior_repo is None:
            self._behavior_repo = BehaviorRepository(self._data_dir)
        return self._behavior_repo
    
    @property
    def converters(self) -> ConverterRepository:
        """Get the converter repository (prompt canvas, lazy loaded)."""
        if self._converter_repo is None:
            self._converter_repo = ConverterRepository(self._data_dir)
        return self._converter_repo
    
    @property
    def evaluators(self) -> EvaluatorRepository:
        """Get the evaluator repository (prompt canvas, lazy loaded)."""
        if self._evaluator_repo is None:
            self._evaluator_repo = EvaluatorRepository(self._data_dir)
        return self._evaluator_repo
    
    @property
    def templates(self) -> PromptTemplateRepository:
        """Get the prompt template repository (prompt canvas, lazy loaded)."""
        if self._template_repo is None:
            self._template_repo = PromptTemplateRepository(self._data_dir)
        return self._template_repo
    
    @property
    def converter_templates(self) -> ConverterPromptTemplateRepository:
        """Get the converter prompt template repository (prompt canvas, lazy loaded)."""
        if self._converter_template_repo is None:
            self._converter_template_repo = ConverterPromptTemplateRepository(self._data_dir)
        return self._converter_template_repo
    
    @property
    def attack_strategies(self) -> AttackStrategiesRepository:
        """Get the attack strategies repository (prompt canvas, lazy loaded)."""
        if self._attack_strategies_repo is None:
            self._attack_strategies_repo = AttackStrategiesRepository(self._data_dir)
        return self._attack_strategies_repo
    
    @property
    def attack_recipes(self) -> AttackRecipesRepository:
        """Get the attack recipes repository (prompt canvas, lazy loaded)."""
        if self._attack_recipes_repo is None:
            self._attack_recipes_repo = AttackRecipesRepository(self._data_dir)
        return self._attack_recipes_repo
    
    # Campaign repositories
    
    @property
    def campaign_objectives(self) -> CampaignObjectiveRepository:
        """Get the campaign objective repository (lazy loaded)."""
        if self._campaign_objective_repo is None:
            self._campaign_objective_repo = get_campaign_objective_repository()
        return self._campaign_objective_repo
    
    @property
    def runbook_objectives(self) -> RunbookObjectiveRepository:
        """Get the runbook objective repository (lazy loaded)."""
        if self._runbook_objective_repo is None:
            self._runbook_objective_repo = get_runbook_objective_repository()
        return self._runbook_objective_repo
    
    @property
    def attack_libraries(self) -> AttackLibraryRepository:
        """Get the attack library repository (lazy loaded)."""
        if self._attack_library_repo is None:
            self._attack_library_repo = get_attack_library_repository()
        return self._attack_library_repo
    
    @property
    def manipulators(self) -> ManipulatorRepository:
        """Get the manipulator repository (lazy loaded)."""
        if self._manipulator_repo is None:
            self._manipulator_repo = get_manipulator_repository()
        return self._manipulator_repo
    
    @property
    def campaign_evaluators(self) -> CampaignEvaluatorRepository:
        """Get the campaign evaluator repository (lazy loaded)."""
        if self._campaign_evaluator_repo is None:
            self._campaign_evaluator_repo = get_campaign_evaluator_repository()
        return self._campaign_evaluator_repo
    
    @property
    def runbook_templates(self) -> RunbookTemplateRepository:
        """Get the runbook template repository (lazy loaded)."""
        if self._runbook_template_repo is None:
            self._runbook_template_repo = get_runbook_template_repository()
        return self._runbook_template_repo
    
    @property
    def ai_target_types(self) -> AITargetTypeRepository:
        """Get the AI target type repository (lazy loaded)."""
        if self._ai_target_type_repo is None:
            self._ai_target_type_repo = get_ai_target_type_repository()
        return self._ai_target_type_repo
    
    @property
    def campaign_types(self) -> CampaignTypeRepository:
        """Get the campaign type repository (lazy loaded)."""
        if self._campaign_type_repo is None:
            self._campaign_type_repo = get_campaign_type_repository()
        return self._campaign_type_repo
    
    def reload_all(self) -> None:
        """Reload all repositories."""
        # Prompt Canvas repositories
        if self._behavior_repo:
            self._behavior_repo.reload()
        if self._converter_repo:
            self._converter_repo.reload()
        if self._evaluator_repo:
            self._evaluator_repo.reload()
        if self._template_repo:
            self._template_repo.reload()
        if self._converter_template_repo:
            self._converter_template_repo.reload()
        if self._attack_strategies_repo:
            self._attack_strategies_repo.reload()
        if self._attack_recipes_repo:
            self._attack_recipes_repo.reload()
        # Campaign repositories don't have reload() method, they use lazy loading
    
    def clear_all_caches(self) -> None:
        """Clear all repository caches."""
        # Prompt Canvas repositories
        if self._behavior_repo:
            self._behavior_repo.clear_cache()
        if self._converter_repo:
            self._converter_repo.clear_cache()
        if self._evaluator_repo:
            self._evaluator_repo.clear_cache()
        if self._template_repo:
            self._template_repo.clear_cache()
        if self._converter_template_repo:
            self._converter_template_repo.clear_cache()
        if self._attack_strategies_repo:
            self._attack_strategies_repo.clear_cache()
        if self._attack_recipes_repo:
            self._attack_recipes_repo.clear_cache()
        # Campaign repositories use internal caching, reset by reinitializing
        if self._campaign_objective_repo:
            self._campaign_objective_repo = None
        if self._runbook_objective_repo:
            self._runbook_objective_repo = None
        if self._attack_library_repo:
            self._attack_library_repo = None
        if self._manipulator_repo:
            self._manipulator_repo = None
        if self._campaign_evaluator_repo:
            self._campaign_evaluator_repo = None
        if self._runbook_template_repo:
            self._runbook_template_repo = None
        if self._ai_target_type_repo:
            self._ai_target_type_repo = None
        if self._campaign_type_repo:
            self._campaign_type_repo = None
    
    def get_stats(self) -> dict:
        """Get statistics for all repositories."""
        stats = {}
        
        # Prompt Canvas repository stats
        if self._behavior_repo:
            stats['behaviors'] = {
                'total': self._behavior_repo.count(),
                'harmbench': len(self._behavior_repo.get_by_tag('harmbench')),
                'advbench': len(self._behavior_repo.get_by_tag('advbench'))
            }
        
        if self._converter_repo:
            stats['converters'] = {
                'total': self._converter_repo.count(),
                'static': len(self._converter_repo.get_static_converters()),
                'llm': len(self._converter_repo.get_llm_converters()),
                'dynamic_code': len(self._converter_repo.get_dynamic_code_converters())
            }
        
        if self._evaluator_repo:
            stats['evaluators'] = {
                'total': self._evaluator_repo.count(),
                'static': len(self._evaluator_repo.get_static_evaluators()),
                'llm-static': len(self._evaluator_repo.get_llm_static_evaluators()),
                'llm': len(self._evaluator_repo.get_llm_evaluators()),
                'true_false': len(self._evaluator_repo.get_by_scorer_type('true_false')),
                'float_scale': len(self._evaluator_repo.get_by_scorer_type('float_scale'))
            }
        
        if self._template_repo:
            stats['templates'] = {
                'total': self._template_repo.count()
            }
        
        if self._converter_template_repo:
            stats['converter_templates'] = {
                'total': self._converter_template_repo.count()
            }
        
        if self._attack_strategies_repo:
            stats['attack_strategies'] = {
                'total': len(self._attack_strategies_repo.list_all()),
                'crescendo': len(self._attack_strategies_repo.get_by_strategy_type('crescendo')),
                'red_teaming': len(self._attack_strategies_repo.get_by_strategy_type('red_teaming')),
                'skeleton_key': len(self._attack_strategies_repo.get_by_strategy_type('skeleton_key')),
                'tap': len(self._attack_strategies_repo.get_by_strategy_type('tap')),
                'role_play': len(self._attack_strategies_repo.get_by_strategy_type('role_play'))
            }
        
        if self._attack_recipes_repo:
            recipe_stats = self._attack_recipes_repo.get_recipe_statistics()
            stats['attack_recipes'] = recipe_stats
        
        # Campaign repository stats
        from dtx_models.repo.campaigns_repo import ListParams
        params = ListParams(limit=1000)
        
        if self._campaign_objective_repo:
            result = self._campaign_objective_repo.list_items(params)
            stats['campaign_objectives'] = {'total': result.total_items}
        
        if self._runbook_objective_repo:
            result = self._runbook_objective_repo.list_items(params)
            stats['runbook_objectives'] = {'total': result.total_items}
        
        if self._attack_library_repo:
            result = self._attack_library_repo.list_items(params)
            stats['attack_libraries'] = {'total': result.total_items}
        
        if self._manipulator_repo:
            result = self._manipulator_repo.list_items(params)
            stats['manipulators'] = {'total': result.total_items}
        
        if self._campaign_evaluator_repo:
            result = self._campaign_evaluator_repo.list_items(params)
            stats['campaign_evaluators'] = {'total': result.total_items}
        
        if self._runbook_template_repo:
            result = self._runbook_template_repo.list_items(params)
            stats['runbook_templates'] = {'total': result.total_items}
        
        if self._ai_target_type_repo:
            result = self._ai_target_type_repo.list_items(params)
            stats['ai_target_types'] = {'total': result.total_items}
        
        if self._campaign_type_repo:
            result = self._campaign_type_repo.list_items(params)
            stats['campaign_types'] = {'total': result.total_items}
        
        return stats


# Global factory instance
_repo_factory: Optional[RepositoryFactory] = None


def get_repo_factory(data_dir: Optional[str] = None) -> RepositoryFactory:
    """
    Get the global repository factory instance.
    
    Args:
        data_dir: Optional data directory (only used on first call)
        
    Returns:
        The global repository factory instance
    """
    global _repo_factory
    
    if _repo_factory is None:
        _repo_factory = RepositoryFactory(data_dir)
    
    return _repo_factory


def get_behaviors(data_dir: Optional[str] = None) -> BehaviorRepository:
    """Get the behavior repository."""
    return get_repo_factory(data_dir).behaviors


def get_converters(data_dir: Optional[str] = None) -> ConverterRepository:
    """Get the converter repository."""
    return get_repo_factory(data_dir).converters


def get_prompt_templates(data_dir: Optional[str] = None) -> PromptTemplateRepository:
    """Get the prompt template repository."""
    return get_repo_factory(data_dir).templates


def get_evaluators(data_dir: Optional[str] = None) -> EvaluatorRepository:
    """Get the evaluator repository."""
    return get_repo_factory(data_dir).evaluators


def get_converter_prompt_templates(data_dir: Optional[str] = None) -> ConverterPromptTemplateRepository:
    """Get the converter prompt template repository."""
    return get_repo_factory(data_dir).converter_templates


def get_attack_strategies(data_dir: Optional[str] = None) -> AttackStrategiesRepository:
    """Get the attack strategies repository."""
    return get_repo_factory(data_dir).attack_strategies


def get_attack_recipes(data_dir: Optional[str] = None) -> AttackRecipesRepository:
    """Get the attack recipes repository."""
    return get_repo_factory(data_dir).attack_recipes


def get_campaign_objectives(data_dir: Optional[str] = None) -> CampaignObjectiveRepository:
    """Get the campaign objective repository."""
    return get_repo_factory(data_dir).campaign_objectives


def get_runbook_objectives(data_dir: Optional[str] = None) -> RunbookObjectiveRepository:
    """Get the runbook objective repository."""
    return get_repo_factory(data_dir).runbook_objectives


def get_attack_libraries(data_dir: Optional[str] = None) -> AttackLibraryRepository:
    """Get the attack library repository."""
    return get_repo_factory(data_dir).attack_libraries


def get_manipulators(data_dir: Optional[str] = None) -> ManipulatorRepository:
    """Get the manipulator repository."""
    return get_repo_factory(data_dir).manipulators


def get_campaign_evaluators(data_dir: Optional[str] = None) -> CampaignEvaluatorRepository:
    """Get the campaign evaluator repository."""
    return get_repo_factory(data_dir).campaign_evaluators


def get_runbook_templates(data_dir: Optional[str] = None) -> RunbookTemplateRepository:
    """Get the runbook template repository."""
    return get_repo_factory(data_dir).runbook_templates


def get_ai_target_types(data_dir: Optional[str] = None) -> AITargetTypeRepository:
    """Get the AI target type repository."""
    return get_repo_factory(data_dir).ai_target_types


def get_campaign_types(data_dir: Optional[str] = None) -> CampaignTypeRepository:
    """Get the campaign type repository."""
    return get_repo_factory(data_dir).campaign_types
