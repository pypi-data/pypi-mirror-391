"""
Attack strategy schemas and parameter definitions for the Prompt Canvas system.

This module defines the data structures and validation logic for attack strategies
that can be used in the Prompt Canvas framework for adversarial testing.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

# Import provider configs for flexible objective_target
from dtx_models.providers.openai import OpenaiProviderConfig
from dtx_models.providers.anthropic import AnthropicProviderConfig
from dtx_models.providers.azure_openAI import AzureProviderConfig
from dtx_models.providers.mistral import MistralProviderConfig
from dtx_models.providers.gemini import GeminiProviderConfig
from dtx_models.providers.litellm import LitellmProviderConfig
from dtx_models.providers.hf import HuggingFaceProviderConfig
from dtx_models.providers.groq import GroqProviderConfig

# Union type for all supported provider configs
ProviderConfig = Union[
    OpenaiProviderConfig,
    AnthropicProviderConfig,
    AzureProviderConfig,
    MistralProviderConfig,
    GeminiProviderConfig,
    LitellmProviderConfig,
    HuggingFaceProviderConfig,
    GroqProviderConfig,
]

# Union type for adversarial provider configs (OpenAI and Groq)
AdversarialProviderConfig = Union[
    OpenaiProviderConfig,
    GroqProviderConfig,
]


"""
# ---
# Attack Strategy Blueprint: Crescendo Attack
#
# This file defines a reusable blueprint for the Crescendo attack strategy.
# It includes default values and examples for each parameter.
# ---

- name: "crescendo-attack-blueprint"
  display_name: "Crescendo Attack Blueprint"
  description: "A blueprint for a multi-turn attack that uses an adversarial LLM and converters to escalate prompts."
  version: "1.1"

  # --- Blueprint Information ---
  strategy_type: "crescendo"
  class_name: "pyrit.executor.attack.CrescendoAttack"

  # --- Blueprint: Parameter Contract ---
  # CHANGED: 'attack_scoring_config' is no longer listed as mandatory.
  parameters:
    - objective_target
    - attack_adversarial_config
    - attack_converter_config

  parameters_schema:
    - name: "objective_target"
      description: "A reference to the primary LLM target for the attack objective. Target name can be a custom name or in the format 'provider/model' (e.g., 'openai/gpt-4', 'azure/gpt-4o')."
      type: "target_reference"
      required: true
      example:
        name: "my-production-gpt4o-target"

    - name: "attack_scoring_config"
      description: "The scoring configuration, which includes a reference to the objective scorer."
      type: "scoring_config"
      # CHANGED: This is now optional.
      required: false
      # CHANGED: Added a default value.
      default:
        objective_scorer:
          name: "default-refusal-scorer"
      example:
        objective_scorer:
          name: "my-custom-jailbreak-scorer"
          parameters:
            substring: "pwned"

    - name: "attack_adversarial_config"
      description: "The adversarial configuration, which includes a reference to the adversarial target. Target name can be a custom name or in the format 'provider/model' (e.g., 'openai/gpt-4', 'azure/gpt-4o')."
      type: "adversarial_config"
      required: true
      example:
        target:
          name: "default-azure-openai-gpt4-adversarial-target"
        system_prompt_uri: "https://.../my_custom_adversarial_prompt.yaml"

    - name: "attack_converter_config"
      description: "A reference to the prompt converter configuration to be used."
      type: "converter_config_reference"
      required: true
      example:
        name: "my-zalgo-plus-emoji-converters"
        
    - name: "max_turns"
      description: "The maximum number of turns in the conversation."
      type: "integer"
      required: false
      default: 5
      example: 10
      
    - name: "max_backtracks"
      description: "The maximum number of times the strategy can backtrack if it fails."
      type: "integer"
      required: false
      default: 5
      example: 3
"""


# --- Reference and Config Schemas (Unchanged) ---

class TargetReference(BaseModel):
    """Reference to a target component in the system."""
    name: str = Field(..., description="The unique name of the target component to be used. Can be a custom name or in the format 'provider/model' (e.g., 'openai/gpt-4', 'azure/gpt-4o').")
    description: Optional[str] = Field(None, description="An optional description for this reference.")


class TargetPlaceholder(BaseModel):
    """Placeholder for an objective target that is required but may not be created during the definition stage."""
    placeholder: bool = Field(default=True, description="Indicates this is a placeholder target.")
    description: Optional[str] = Field(None, description="An optional description for this placeholder.")
    required: bool = Field(default=True, description="Whether this target is required for the attack strategy.")
    
    def to_target_reference(self, target_name: str, target_description: Optional[str] = None) -> TargetReference:
        """Convert this placeholder to a TargetReference when the actual target is available."""
        return TargetReference(
            name=target_name,
            description=target_description or self.description
        )


class AdversarialTargetReference(BaseModel):
    """Reference to an adversarial target component in the system."""
    name: str = Field(..., description="The unique name of the adversarial target component to be used. Can be a custom name or in the format 'provider/model' (e.g., 'openai/gpt-4', 'azure/gpt-4o').")
    description: Optional[str] = Field(None, description="An optional description for this adversarial target reference.")


class AdversarialTargetPlaceholder(BaseModel):
    """Placeholder for an adversarial target that is required but may not be created during the definition stage."""
    placeholder: bool = Field(default=True, description="Indicates this is a placeholder adversarial target.")
    description: Optional[str] = Field(None, description="An optional description for this adversarial target placeholder.")
    required: bool = Field(default=True, description="Whether this adversarial target is required for the attack strategy.")
    
    def to_adversarial_target_reference(self, target_name: str, target_description: Optional[str] = None) -> AdversarialTargetReference:
        """Convert this placeholder to an AdversarialTargetReference when the actual target is available."""
        return AdversarialTargetReference(
            name=target_name,
            description=target_description or self.description
        )

class ScorerReference(BaseModel):
    """Reference to a scorer component with optional parameter overrides."""
    name: str = Field(..., description="The unique name of the scorer component to be used.")
    description: Optional[str] = Field(None, description="An optional description for this reference.")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional dictionary of parameter values to override the scorer's defaults."
    )

class ConverterConfigReference(BaseModel):
    """Reference to a converter configuration with optional parameter overrides."""
    name: str = Field(..., description="The unique name of the converter configuration to be used.")
    description: Optional[str] = Field(None, description="An optional description for this reference.")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional dictionary of parameter values to override the converter config's defaults."
    )

class ScoringConfigSchema(BaseModel):
    """Configuration schema for scoring components matching PyRIT's AttackScoringConfig."""
    objective_scorer: Optional[ScorerReference] = Field(
        None, 
        description="Reference to the objective scorer to be used. Must be a true/false scorer if provided."
    )
    refusal_scorer: Optional[ScorerReference] = Field(
        None,
        description="Reference to the refusal scorer for detecting refusals or non-compliance. Must be a true/false scorer if provided."
    )
    auxiliary_scorers: List[ScorerReference] = Field(
        default_factory=list,
        description="List of additional scorers for auxiliary metrics or custom evaluations. Can include any scorer type (Likert, float_scale, true/false, etc.)."
    )
    use_score_as_feedback: bool = Field(
        default=True,
        description="Whether to use scoring results as feedback for iterative attacks."
    )
    successful_objective_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Threshold for considering an objective successful [0.0 to 1.0]. A value of 1.0 means the objective must be fully achieved, while 0.0 means any score is acceptable. Only applies to float_scale scorers."
    )
    
    @model_validator(mode='after')
    def validate_threshold(self) -> 'ScoringConfigSchema':
        """Validate that successful_objective_threshold is within valid range."""
        if not 0.0 <= self.successful_objective_threshold <= 1.0:
            raise ValueError(
                f"successful_objective_threshold must be between 0.0 and 1.0, "
                f"got {self.successful_objective_threshold}"
            )
        return self

class AdversarialConfigSchema(BaseModel):
    """Configuration schema for adversarial attack components."""
    target: Union[str, AdversarialTargetReference, AdversarialProviderConfig, AdversarialTargetPlaceholder] = Field(..., description="Reference to the adversarial target to be used. Can be a string (e.g., 'openai/gpt-4'), AdversarialTargetReference, AdversarialProviderConfig (OpenAI or Groq), or AdversarialTargetPlaceholder.")
    system_prompt_uri: Optional[str] = Field(None, description="Optional URI to a custom system prompt for the adversarial target.")


# --- UPDATED Attack Strategy Parameter Definition ---

class AttackStrategyParameter(BaseModel):
    """Schema for defining attack strategy parameters with validation and documentation."""
    name: str = Field(..., description="The parameter name, matching the __init__ argument.")
    description: str = Field(..., description="A description of what the parameter does.")
    type: Literal[
        "string", "integer", "float", "boolean", "dict", "array", "target_reference", "scoring_config", "adversarial_config", "converter_config_reference"
    ] = Field(..., description="The data type or reference type of the parameter.")
    required: bool = Field(..., description="Whether the parameter is mandatory.")
    default: Optional[Any] = Field(None, description="The default value for this parameter, if it's not required.")
    example: Optional[Any] = Field(None, description="An example of a valid value for this parameter.")
    
    @model_validator(mode='after')
    def validate_parameter_consistency(self) -> 'AttackStrategyParameter':
        """Validate parameter consistency between required flag and default value."""
        if self.required and self.default is not None:
            raise ValueError(f"Parameter '{self.name}' cannot be both required and have a default value")
        
        # Allow optional parameters without defaults (they can be None)
        return self


# --- Generic Attack Strategy Schema (Unchanged) ---

class AttackStrategy(BaseModel):
    """
    A generic schema to define a blueprint for any attack strategy.
    
    This class defines the structure for attack strategy blueprints, including
    metadata, parameter definitions, and validation rules.
    """
    name: str = Field(..., description="A unique name for this attack strategy blueprint.")
    display_name: Optional[str] = Field(None, description="A user-friendly display name for the strategy.")
    description: Optional[str] = Field(None, description="A detailed explanation of this attack strategy.")
    version: str = Field(default="1.0", description="The version of the strategy blueprint.")
    strategy_type: str = Field(..., description="The unique type of the strategy (e.g., 'crescendo').")
    class_name: str = Field(..., description="The fully-qualified Python class for this strategy.")
    tags: Optional[List[str]] = Field(None, description="Optional tags for categorizing the strategy.")
    
    # Complex structured parameters as direct fields
    objective_target: Optional[Union[str, TargetReference, ProviderConfig, TargetPlaceholder]] = Field(None, description="A reference to the primary LLM target for the attack objective. Can be a string (e.g., 'openai/gpt-4'), TargetReference, ProviderConfig, or TargetPlaceholder.")
    attack_adversarial_config: Optional[AdversarialConfigSchema] = Field(None, description="The adversarial configuration for the attack.")
    attack_scoring_config: Optional[ScoringConfigSchema] = Field(None, description="The scoring configuration for the attack.")
    attack_converter_config: Optional[ConverterConfigReference] = Field(None, description="The converter configuration for the attack.")
    
    # Simple parameters
    parameters: List[str] = Field(default=[], description="A list of simple parameter names for this strategy.")
    parameters_schema: List[AttackStrategyParameter] = Field(
        default=[],
        description="The detailed schema for simple parameters, including their default values."
    )
    
    @model_validator(mode='after')
    def validate_parameters_consistency(self) -> 'AttackStrategy':
        """Validate that all required parameters have corresponding schema definitions."""
        schema_names = {param.name for param in self.parameters_schema}
        missing_schemas = set(self.parameters) - schema_names
        
        if missing_schemas:
            raise ValueError(f"Required parameters {missing_schemas} are missing from parameters_schema")
        
        return self