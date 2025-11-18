"""
Evaluator schemas and factory functions for the Prompt Canvas system.

This module defines the data structures and validation logic for different types
of scorers/evaluators that can be used in the Prompt Canvas framework.
"""

import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

# --- Base Data Types & Schemas ---

ScoreType = Literal["true_false", "float_scale"]
"""The type of score a scorer can produce."""

class TrueFalseQuestionSchema(BaseModel):
    """Schema for TrueFalseQuestion object."""
    true_description: str = Field(
        ...,
        description="Description of what should be evaluated as 'true'."
    )
    false_description: Optional[str] = Field(
        default="",
        description="Description of what should be evaluated as 'false'. "
                   "If not provided, defaults to anything that doesn't fulfill the true description."
    )
    category: Optional[str] = Field(
        default="",
        description="Optional category for the question."
    )
    metadata: Optional[str] = Field(
        default="",
        description="Optional metadata associated with the question."
    )

class ScorerParameter(BaseModel):
    """
    Schema for defining scorer parameters.
    
    This class defines the structure for individual parameters that can be
    passed to a scorer, including their type, description, and validation rules.
    """
    name: str = Field(
        ..., 
        description="The machine-readable name of the parameter, matching the __init__ argument."
    )
    description: str = Field(
        ..., 
        description="A human-readable description of what the parameter does."
    )
    type: Literal[
        "string", "integer", "float", "boolean", "array", "url", 
        "dict", "path_or_enum", "true_false_question", "scorer_reference"
    ] = Field(
        ..., 
        description="The data type of the parameter."
    )
    required: bool = Field(
        default=False, 
        description="Whether the parameter is mandatory."
    )
    default: Optional[Any] = Field(
        default=None, 
        description="A default value if the parameter is not provided."
    )
    # Enum support for path_or_enum and string types
    enum_options: Optional[List[str]] = Field(
        default=None,
        description="List of valid enum constant names. "
                   "For 'path_or_enum' type: enum values should be resolved by client to file paths. "
                   "For 'string' type: list of valid string values the parameter can accept."
    )
    supported_formats: Optional[List[Literal["url", "file_path", "enum"]]] = Field(
        default=None,
        description="Supported input formats for 'path_or_enum' type parameters."
    )
    # Schema for dict/true_false_question type
    dict_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON schema definition for dict/true_false_question type parameters."
    )
    # For scorer_reference type: expected scorer type
    scorer_schema: Optional[str] = Field(
        default=None,
        description="For scorer_reference type: expected scorer type (e.g., 'float_scale', 'true_false'). "
                   "This helps validate that the referenced scorer is of the correct type."
    )
    example: Optional[Any] = Field(
        default=None,
        description="Example value for the parameter to guide users."
    )
    
    @model_validator(mode='after')
    def validate_parameter_config(self) -> 'ScorerParameter':
        """Validate parameter configuration consistency."""
        if self.type == "path_or_enum":
            # enum_options are optional - client will handle resolution
            pass
        elif self.type == "true_false_question":
            # Validation will happen at runtime when the dict is provided
            pass
        elif self.type == "scorer_reference":
            # scorer_schema is optional but recommended for validation
            pass
        
        return self

class BaseScorerSchema(BaseModel):
    """
    Base schema for all scorer types.
    
    This class defines the common fields that all scorer schemas must have,
    including identification, description, and categorization.
    """
    name: str = Field(
        ..., 
        description="A unique, machine-readable identifier for the scorer."
    )
    display_name: Optional[str] = Field(
        None, 
        description="An optional, user-friendly name."
    )
    description: str = Field(
        ..., 
        description="A brief explanation of what the scorer does."
    )
    scorer_type: ScoreType = Field(
        ..., 
        description="The type of score this scorer will produce."
    )
    tags: List[str] = Field(
        default_factory=list, 
        description="Tags for categorizing and searching."
    )

# --- Scorer Schemas ---

class SimpleStaticScorerSchema(BaseScorerSchema):
    """
    Schema for a static scorer that does NOT require an LLM.
    
    Examples include SubStringScorer, BERTScoreScorer, etc. These scorers
    use pre-built classes that don't need language model inference.
    """
    type: Literal["static"] = Field(
        "static", 
        description="Indicates a pre-built class with no LLM dependency."
    )
    class_name: str = Field(
        ..., 
        description="The fully-qualified, importable name of the Python class."
    )
    parameters: List[str] = Field(
        default_factory=list, 
        description="A list of mandatory parameter names."
    )
    parameters_schema: List[ScorerParameter] = Field(
        default_factory=list, 
        description="A detailed schema for all possible parameters."
    )
    
    @model_validator(mode='after')
    def validate_parameter_consistency(self) -> 'SimpleStaticScorerSchema':
        """Validate that parameters and parameters_schema are consistent."""
        required_params = {p.name for p in self.parameters_schema if p.required}
        declared_params = set(self.parameters)
        
        if required_params != declared_params:
            missing_in_declared = required_params - declared_params
            extra_in_declared = declared_params - required_params
            
            errors = []
            if missing_in_declared:
                errors.append(f"Missing required parameters in 'parameters' list: {missing_in_declared}")
            if extra_in_declared:
                errors.append(f"Extra parameters in 'parameters' list: {extra_in_declared}")
            
            raise ValueError(f"Parameter inconsistency: {'; '.join(errors)}")
        
        return self

class LLMStaticScorerSchema(BaseScorerSchema):
    """
    Schema for a static scorer that REQUIRES an LLM to function.
    
    Examples include SelfAskScaleScorer, SelfAskTrueFalseScorer, etc. These
    scorers use pre-built classes but require language model inference.
    """
    type: Literal["llm-static"] = Field(
        "llm-static", 
        description="Indicates a pre-built class that requires an LLM."
    )
    class_name: str = Field(
        ..., 
        description="The fully-qualified, importable name of the Python class."
    )
    chat_target: str = Field(
        ...,
        description="The language model to use for scoring, in 'provider/model_name' format.",
        pattern=r"^[^/]+/.+$"
    )
    parameters: List[str] = Field(
        default_factory=list, 
        description="A list of other mandatory non-LLM parameter names."
    )
    parameters_schema: List[ScorerParameter] = Field(
        default_factory=list, 
        description="A detailed schema for other possible non-LLM parameters."
    )
    
    @model_validator(mode='after')
    def validate_parameter_consistency(self) -> 'LLMStaticScorerSchema':
        """Validate that parameters and parameters_schema are consistent."""
        required_params = {p.name for p in self.parameters_schema if p.required}
        declared_params = set(self.parameters)
        
        if required_params != declared_params:
            missing_in_declared = required_params - declared_params
            extra_in_declared = declared_params - required_params
            
            errors = []
            if missing_in_declared:
                errors.append(f"Missing required parameters in 'parameters' list: {missing_in_declared}")
            if extra_in_declared:
                errors.append(f"Extra parameters in 'parameters' list: {extra_in_declared}")
            
            raise ValueError(f"Parameter inconsistency: {'; '.join(errors)}")
        
        return self
    
    @staticmethod
    def validate_true_false_question(value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate true_false_question parameter structure.
        This can be called at runtime when instantiating the scorer.
        
        Args:
            value: Dictionary representing a TrueFalseQuestion
            
        Returns:
            Validated question dict
            
        Raises:
            ValueError: If validation fails
        """
        try:
            validated = TrueFalseQuestionSchema(**value)
            return validated.model_dump(exclude_none=True)
        except Exception as e:
            raise ValueError(
                f"Invalid true_false_question structure: {e}. "
                f"Expected format: {{'true_description': str, 'false_description': str (optional), "
                f"'category': str (optional), 'metadata': str (optional)}}"
            )

class LLMScorerSchema(BaseScorerSchema):
    """
    Schema for a scorer that is dynamically defined by an LLM prompt.
    
    These scorers are not pre-built classes but are defined entirely by
    prompts and executed dynamically using language models.
    """
    type: Literal["llm"] = Field(
        "llm", 
        description="Indicates a dynamically defined LLM-based scorer."
    )
    execution_target: str = Field(
        ..., 
        description="Target in 'provider/model_name' format.", 
        pattern=r"^[^/]+/.+$"
    )
    system_prompt: str = Field(
        ..., 
        description="System prompt template for the LLM scorer."
    )

class CompositeScorerSchema(BaseScorerSchema):
    """
    Schema for a composite/wrapper scorer that wraps or combines other scorers.
    
    Examples include FloatScaleThresholdScorer, TrueFalseInverterScorer, etc.
    These scorers take other scorer instances as parameters and modify or combine
    their behavior.
    """
    type: Literal["composite"] = Field(
        "composite", 
        description="Indicates a composite scorer that wraps other scorers."
    )
    class_name: str = Field(
        ..., 
        description="The fully-qualified Python class name for the composite scorer."
    )
    chat_target: Optional[str] = Field(
        None,
        description="Optional chat target in 'provider/model_name' format. "
                   "Most composite scorers don't require this as they delegate to wrapped scorers."
    )
    parameters: List[str] = Field(
        default_factory=list,
        description="List of parameter names that are required for this scorer."
    )
    parameters_schema: List[ScorerParameter] = Field(
        default_factory=list,
        description="Detailed schema for all parameters, including nested scorer references."
    )

# --- Union Type and Factory Function ---

AnyScorerSchema = Union[SimpleStaticScorerSchema, LLMStaticScorerSchema, LLMScorerSchema, CompositeScorerSchema]
"""Union type for all possible scorer schema types."""

def create_scorer_schema(data: Dict[str, Any]) -> AnyScorerSchema:
    """
    Factory function to create the appropriate scorer schema type.
    
    Args:
        data: Dictionary containing scorer configuration data
        
    Returns:
        The appropriate scorer schema instance based on the 'type' field
        
    Raises:
        ValueError: If the scorer type is not recognized
        ValidationError: If the data doesn't match the expected schema
    """
    scorer_def_type = data.get("type")
    
    if scorer_def_type == "static":
        return SimpleStaticScorerSchema(**data)
    elif scorer_def_type == "llm-static":
        return LLMStaticScorerSchema(**data)
    elif scorer_def_type == "llm":
        return LLMScorerSchema(**data)
    elif scorer_def_type == "composite":
        return CompositeScorerSchema(**data)
    else:
        raise ValueError(
            f"Unknown scorer definition type: '{scorer_def_type}'. "
            f"Must be one of: 'static', 'llm-static', 'llm', 'composite'."
        )


def validate_true_false_question_dict(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate true_false_question parameter structure.
    
    This function validates the structure but does not handle enum resolution.
    Enum resolution should be handled by the client implementation.
    
    Args:
        question: TrueFalseQuestion dict structure
        
    Returns:
        Validated question dict
        
    Raises:
        ValueError: If validation fails
    """
    try:
        validated = TrueFalseQuestionSchema(**question)
        return validated.model_dump(exclude_none=True)
    except Exception as e:
        raise ValueError(
            f"Invalid true_false_question structure: {e}. "
            f"Expected format: {{'true_description': str, 'false_description': str (optional), "
            f"'category': str (optional), 'metadata': str (optional)}}"
        )