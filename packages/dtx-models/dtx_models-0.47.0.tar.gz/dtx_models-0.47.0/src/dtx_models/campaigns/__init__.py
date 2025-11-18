"""Pydantic models backing metadata repositories."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Literal

from pydantic import BaseModel, Field

# --- Enums & literal types -------------------------------------------------
CampaignTypeLiteral = Literal["zero_knowledge_red_teaming", "ai_pentesting", "internal_ai_pentesting"]
CampaignStatus = Literal["Draft", "Running", "Completed", "Archived"]
AdvancedParamType = Literal["string", "number", "boolean", "enum", "list[string]"]
ManipulatorType = Literal["Transformation", "Injection", "Attack", "Simulator"]


class BaseRepoModel(BaseModel):
    """Common fields shared by all repository-backed models."""

    name: str = Field(..., description="Unique snake_case name, used as ID")
    title: str = Field(..., description="User-friendly display title")
    description: str = Field(..., description="Detailed description of the item")


class CampaignObjective(BaseRepoModel):
    """High-level campaign objectives (e.g., Sensitive Data Leakage)."""
    
    category: Optional[str] = Field(default=None, description="Category classification for the objective (e.g., Responsible AI, Confidentiality).")
    campaign_types: List[str] = Field(default_factory=list, description="List of campaign type names this objective applies to. Empty means applies to all.")
    framework_reference: str = Field(default="generic", description="Framework reference for this objective. 'generic' means framework-agnostic.")
    target_types: List[str] = Field(default_factory=list, description="List of target type names this objective applies to. Empty means applies to all target types.")


class FrameworkAndControlReference(BaseModel):
    """Framework reference with associated controls."""

    framework: str = Field(..., description="Framework name (e.g., 'generic', 'owasp_llm', 'gdpr')")
    controls: List[str] = Field(default_factory=list, description="List of control identifiers for this framework")


class RunbookObjective(BaseRepoModel):
    """Granular, testable objectives linked to one or more campaign objectives."""

    campaign_objective_names: List[str] = Field(default_factory=list, description="List of campaign objective names this runbook objective maps to")
    plugins: List[str] = Field(default_factory=list, description="List of plugin identifiers (e.g., 'information_hazard:data_leaks:input-leakage')")
    framework_references: List[FrameworkAndControlReference] = Field(default_factory=list, description="List of framework references with associated controls")


class AdvancedParam(BaseModel):
    """Schema definition for an attack library advanced parameter."""

    name: str
    title: str
    type: AdvancedParamType
    description: str


class AttackLibraryItem(BaseRepoModel):
    """Metadata describing how an attack is performed."""

    runbook_objective_names: List[str] = Field(default_factory=list)
    advanced_params: List[AdvancedParam] = Field(default_factory=list)
    recommended_evaluator_names: List[str] = Field(default_factory=list)


class Manipulator(BaseRepoModel):
    """Metadata describing a reusable manipulator."""

    type: ManipulatorType


class Evaluator(BaseRepoModel):
    """Metadata describing an evaluator/scorer."""


class RunbookTemplate(BaseModel):
    """Pre-configured runbook definition."""

    name: str
    title: str
    description: str
    runbook_objective_name: str
    campaign_objective_names: List[str] = Field(default_factory=list)
    attack_library_name: str
    attack_library_params: Dict[str, Any] = Field(default_factory=dict)
    manipulator_names: List[str] = Field(default_factory=list)
    evaluator_name: str


class CampaignTarget(BaseModel):
    """Represents a campaign target asset."""

    target_id: str


class RunbookAttackLibrary(AttackLibraryItem):
    """Denormalized attack library details stored within a runbook."""

    attack_library_params: Dict[str, Any] = Field(default_factory=dict)


class RunbookManipulator(Manipulator):
    """Denormalized manipulator copy stored inside a runbook."""


class RunbookEvaluator(Evaluator):
    """Denormalized evaluator copy stored inside a runbook."""


class AttackRunbook(BaseModel):
    """Configured runbook stored inside a campaign."""

    id: str
    name: str
    runbook_objective: RunbookObjective
    runbook_attack_library: RunbookAttackLibrary
    runbook_manipulators: List[RunbookManipulator] = Field(default_factory=list)
    runbook_evaluator: RunbookEvaluator


class CampaignConfig(BaseModel):
    framework_name: str = ""
    campaign_objective_names: List[str] = Field(default_factory=list)
    runbooks: List[AttackRunbook] = Field(default_factory=list)


class Campaign(BaseModel):
    id: str
    campaign_name: str
    description: str
    campaign_type: CampaignTypeLiteral
    status: CampaignStatus
    targets: List[CampaignTarget] = Field(default_factory=list)
    config: CampaignConfig = Field(default_factory=CampaignConfig)
    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated responses."""

    total_items: int
    items: List[T]
    skip: int
    limit: int
