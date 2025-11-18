from __future__ import annotations
import os
import yaml
from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, Sequence, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Type

from dtx_models.campaigns.runbooks import (
    AITargetType,
    AttackLibraryItem,
    CampaignObjective,
    CampaignType,
    Evaluator,
    Manipulator,
    ManipulatorType,
    PaginatedResponse,
    RunbookObjective,
    RunbookTemplate,
)

from .base_repo import BaseRepository


"""YAML-backed repository implementations with module-level singletons."""

T = TypeVar("T")

@dataclass(frozen=True)
class ListParams:
    """Common list parameters shared by metadata repositories."""

    keyword: Optional[str] = None
    skip: int = 0
    limit: int = 20

    def normalized_keyword(self) -> Optional[str]:
        if self.keyword is None:
            return None
        key = self.keyword.strip().lower()
        return key or None

    def clamp_limit(self, *, min_limit: int = 1, max_limit: int = 100) -> int:
        return max(min_limit, min(self.limit, max_limit))


def keyword_filter(
    items: Iterable[T],
    keyword: Optional[str],
    value_provider: Callable[[T], Sequence[str]],
) -> List[T]:
    """Return only items whose provided values contain the keyword (case-insensitive)."""

    normalized = keyword.strip().lower() if keyword else None
    if not normalized:
        return list(items)

    result: List[T] = []
    for item in items:
        values = value_provider(item)
        if any(normalized in (value or "").lower() for value in values):
            result.append(item)
    return result


def paginate(items: Sequence[T], *, skip: int, limit: int) -> PaginatedResponse[T]:
    """Slice the sequence according to skip/limit and wrap in a PaginatedResponse."""

    safe_skip = max(skip, 0)
    safe_limit = max(limit, 1)
    start = min(safe_skip, len(items))
    end = min(start + safe_limit, len(items))
    sliced = list(items[start:end])
    return PaginatedResponse(
        total_items=len(items),
        items=sliced,
        skip=safe_skip,
        limit=safe_limit,
    )


class MetadataRepository(ABC, Generic[T]):
    """Generic repository contract for metadata collections."""

    @abstractmethod
    def list_items(self, params: ListParams, **filters) -> PaginatedResponse[T]:
        """Return paginated items honoring the requested filters."""


class CampaignObjectiveRepository(MetadataRepository[CampaignObjective], ABC):
    @abstractmethod
    def list_items(self, params: ListParams) -> PaginatedResponse[CampaignObjective]:  # type: ignore[override]
        raise NotImplementedError


class RunbookObjectiveRepository(MetadataRepository[RunbookObjective], ABC):
    @abstractmethod
    def list_items(
        self,
        params: ListParams,
        *,
        campaign_objective_name: Optional[str] = None,
    ) -> PaginatedResponse[RunbookObjective]:
        raise NotImplementedError


class AttackLibraryRepository(MetadataRepository[AttackLibraryItem], ABC):
    @abstractmethod
    def list_items(
        self,
        params: ListParams,
        *,
        runbook_objective_name: Optional[str] = None,
        attack_strategy_name: Optional[str] = None,
    ) -> PaginatedResponse[AttackLibraryItem]:
        raise NotImplementedError


class ManipulatorRepository(MetadataRepository[Manipulator], ABC):
    @abstractmethod
    def list_items(
        self,
        params: ListParams,
        *,
        manipulator_type: Optional[ManipulatorType] = None,
    ) -> PaginatedResponse[Manipulator]:
        raise NotImplementedError


class EvaluatorRepository(MetadataRepository[Evaluator], ABC):
    @abstractmethod
    def list_items(self, params: ListParams) -> PaginatedResponse[Evaluator]:  # type: ignore[override]
        raise NotImplementedError


class RunbookTemplateRepository(MetadataRepository[RunbookTemplate], ABC):
    @abstractmethod
    def list_items(
        self,
        params: ListParams,
        *,
        campaign_objective_name: Optional[str] = None,
    ) -> PaginatedResponse[RunbookTemplate]:
        raise NotImplementedError


class AITargetTypeRepository(MetadataRepository[AITargetType], ABC):
    @abstractmethod
    def list_items(self, params: ListParams) -> PaginatedResponse[AITargetType]:  # type: ignore[override]
        raise NotImplementedError


class CampaignTypeRepository(MetadataRepository[CampaignType], ABC):
    @abstractmethod
    def list_items(self, params: ListParams) -> PaginatedResponse[CampaignType]:  # type: ignore[override]
        raise NotImplementedError


class CampaignYamlRepositoryBase(BaseRepository[T], Generic[T]):
    """Base class for campaign YAML repositories that inherit from BaseRepository."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the repository with campaign data directory."""
        super().__init__(data_dir)
        self._filename = self._get_filename()
        self._model = self._get_model()
    
    def _get_default_data_dir(self) -> str:
        """Get the default data directory for campaign repositories."""
        # Point to data/campaigns/data/ subdirectory
        return str(Path(__file__).parent / "data" / "campaigns" / "data")
    
    @abstractmethod
    def _get_filename(self) -> str:
        """Return the YAML filename for this repository."""
        pass
    
    @abstractmethod
    def _get_model(self) -> Type[T]:
        """Return the Pydantic model class for this repository."""
        pass
    
    def _get_data_files(self) -> List[str]:
        """Get the list of data files to load from."""
        filename = self._get_filename()
        file_path = os.path.join(self._data_dir, filename)
        return [file_path] if os.path.exists(file_path) else []
    
    def _load_item(self, name: str, data: Dict[str, Any]) -> T:
        """Load an item from its data dictionary."""
        return self._model(**data)
    
    def _load_from_file(self, file_path: str) -> None:
        """Load items from a YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, list):
                items = data
            else:
                items = [data] if data else []
            
            for item_data in items:
                if isinstance(item_data, dict) and 'name' in item_data:
                    name = item_data['name']
                    self._cache[name] = self._load_item(name, item_data)
                    
        except Exception as e:
            print(f"Warning: Failed to load data from {file_path}: {e}")
    
    @property
    def items(self) -> List[T]:
        """Get all items (for backward compatibility with existing code)."""
        if not self._loaded:
            self._load_all()
        return list(self._cache.values())

    # --- Convenience helpers -------------------------------------------------
    def _apply_keyword_filter(self, params: ListParams, value_provider: Callable[[T], Sequence[str]]) -> List[T]:
        if not self._loaded:
            self._load_all()
        return keyword_filter(self.items, params.keyword, value_provider)

    def _paginate(self, data: Sequence[T], params: ListParams) -> PaginatedResponse[T]:
        return paginate(list(data), skip=params.skip, limit=params.clamp_limit())


class CampaignObjectiveYamlRepository(CampaignYamlRepositoryBase[CampaignObjective], CampaignObjectiveRepository):
    def _get_filename(self) -> str:
        return "campaign_objectives.yaml"
    
    def _get_model(self) -> Type[CampaignObjective]:
        return CampaignObjective

    def list_items(self, params: ListParams) -> PaginatedResponse[CampaignObjective]:  # type: ignore[override]
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        return self._paginate(filtered, params)


class RunbookObjectiveYamlRepository(CampaignYamlRepositoryBase[RunbookObjective], RunbookObjectiveRepository):
    def _get_filename(self) -> str:
        return "runbook_objectives.yaml"
    
    def _get_model(self) -> Type[RunbookObjective]:
        return RunbookObjective

    def list_items(
        self,
        params: ListParams,
        *,
        campaign_objective_name: Optional[str] = None,
    ) -> PaginatedResponse[RunbookObjective]:
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        if campaign_objective_name:
            filtered = [item for item in filtered if campaign_objective_name in item.campaign_objective_names]
        return self._paginate(filtered, params)


class AttackLibraryYamlRepository(CampaignYamlRepositoryBase[AttackLibraryItem], AttackLibraryRepository):
    def _get_filename(self) -> str:
        return "attack_libraries.yaml"
    
    def _get_model(self) -> Type[AttackLibraryItem]:
        return AttackLibraryItem

    def list_items(
        self,
        params: ListParams,
        *,
        runbook_objective_name: Optional[str] = None,
        attack_strategy_name: Optional[str] = None,
    ) -> PaginatedResponse[AttackLibraryItem]:
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        if runbook_objective_name:
            filtered = [item for item in filtered if runbook_objective_name in item.runbook_objective_names]
        if attack_strategy_name:
            filtered = [
                item for item in filtered
                if item.attack_dataset
                and item.attack_dataset.attack_strategy
                and item.attack_dataset.attack_strategy.name == attack_strategy_name
            ]
        return self._paginate(filtered, params)


class ManipulatorYamlRepository(CampaignYamlRepositoryBase[Manipulator], ManipulatorRepository):
    def _get_filename(self) -> str:
        return "manipulators.yaml"
    
    def _get_model(self) -> Type[Manipulator]:
        return Manipulator

    def list_items(
        self,
        params: ListParams,
        *,
        manipulator_type: Optional[ManipulatorType] = None,
    ) -> PaginatedResponse[Manipulator]:
        filtered = self._apply_keyword_filter(
            params,
            lambda item: (item.name, item.title, item.description, item.type),
        )
        if manipulator_type:
            filtered = [item for item in filtered if item.type == manipulator_type]
        return self._paginate(filtered, params)


class EvaluatorYamlRepository(CampaignYamlRepositoryBase[Evaluator], EvaluatorRepository):
    def _get_filename(self) -> str:
        return "evaluators.yaml"
    
    def _get_model(self) -> Type[Evaluator]:
        return Evaluator

    def list_items(self, params: ListParams) -> PaginatedResponse[Evaluator]:  # type: ignore[override]
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        return self._paginate(filtered, params)


class RunbookTemplateYamlRepository(CampaignYamlRepositoryBase[RunbookTemplate], RunbookTemplateRepository):
    def _get_filename(self) -> str:
        return "runbook_templates.yaml"
    
    def _get_model(self) -> Type[RunbookTemplate]:
        return RunbookTemplate

    def list_items(
        self,
        params: ListParams,
        *,
        campaign_objective_name: Optional[str] = None,
    ) -> PaginatedResponse[RunbookTemplate]:
        filtered = self._apply_keyword_filter(
            params,
            lambda item: (item.name, item.title, item.description, item.runbook_objective_name),
        )
        if campaign_objective_name:
            filtered = [item for item in filtered if campaign_objective_name in item.campaign_objective_names]
        return self._paginate(filtered, params)


class AITargetTypeYamlRepository(CampaignYamlRepositoryBase[AITargetType], AITargetTypeRepository):
    def _get_filename(self) -> str:
        return "targets_types.yaml"
    
    def _get_model(self) -> Type[AITargetType]:
        return AITargetType

    def list_items(self, params: ListParams) -> PaginatedResponse[AITargetType]:  # type: ignore[override]
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        return self._paginate(filtered, params)


class CampaignTypeYamlRepository(CampaignYamlRepositoryBase[CampaignType], CampaignTypeRepository):
    def _get_filename(self) -> str:
        return "campaign_types.yaml"
    
    def _get_model(self) -> Type[CampaignType]:
        return CampaignType

    def list_items(self, params: ListParams) -> PaginatedResponse[CampaignType]:  # type: ignore[override]
        filtered = self._apply_keyword_filter(params, lambda item: (item.name, item.title, item.description))
        return self._paginate(filtered, params)


# --- Dependency helpers ----------------------------------------------------
_campaign_objective_repo = CampaignObjectiveYamlRepository()
_runbook_objective_repo = RunbookObjectiveYamlRepository()
_attack_library_repo = AttackLibraryYamlRepository()
_manipulator_repo = ManipulatorYamlRepository()
_evaluator_repo = EvaluatorYamlRepository()
_runbook_template_repo = RunbookTemplateYamlRepository()
_ai_target_type_repo = AITargetTypeYamlRepository()
_campaign_type_repo = CampaignTypeYamlRepository()


def get_campaign_objective_repository() -> CampaignObjectiveRepository:
    return _campaign_objective_repo


def get_runbook_objective_repository() -> RunbookObjectiveRepository:
    return _runbook_objective_repo


def get_attack_library_repository() -> AttackLibraryRepository:
    return _attack_library_repo


def get_manipulator_repository() -> ManipulatorRepository:
    return _manipulator_repo


def get_evaluator_repository() -> EvaluatorRepository:
    return _evaluator_repo


def get_runbook_template_repository() -> RunbookTemplateRepository:
    return _runbook_template_repo


def get_ai_target_type_repository() -> AITargetTypeRepository:
    return _ai_target_type_repo


def get_campaign_type_repository() -> CampaignTypeRepository:
    return _campaign_type_repo
