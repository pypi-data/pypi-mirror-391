"""
Prompt Converter Workflow Pydantic Models

This module defines the Pydantic classes for prompt converter workflows.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from ..base import PromptCanvasBase
from ..converter import AnyConverter, ConverterResult, StaticConverter, LLMConverter, DynamicCodeConverter
from ..behavior import Behavior
from ..prompt_templates.converter_prompts import ConverterPromptTemplate


class ConverterSpec(BaseModel):
    """
    A Pydantic model for specifying a converter by name with optional metadata.
    
    This class allows users to specify a converter by name and optionally provide
    a title and description for better documentation and identification.
    """
    
    name: str = Field(
        ...,
        description="The name/identifier of the converter to use",
        min_length=1,
        max_length=100
    )
    
    title: Optional[str] = Field(
        None,
        description="Optional human-readable title for the converter",
        max_length=200
    )
    
    description: Optional[str] = Field(
        None,
        description="Optional description of what this converter does",
        max_length=1000
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "zalgo_converter",
                    "title": "Zalgo Text Converter",
                    "description": "Converts text into cursed Zalgo text using combining Unicode marks"
                },
                {
                    "name": "zero_width_converter"
                }
            ]
        }
    )


class PromptConverterWorkflow(PromptCanvasBase):
    """
    A workflow that chains multiple prompt converters together to create
    sophisticated prompt processing pipelines.
    """
    
    workflow_type: str = Field(default="prompt_converter", description="The type of workflow")
    name: str = Field(..., description="A unique, machine-readable identifier for the workflow")
    display_name: Optional[str] = Field(None, description="An optional, user-friendly name for display purposes")
    description: Optional[str] = Field(None, description="A brief explanation of what the workflow does")
    version: str = Field(default="1.0", description="The version of the workflow")
    
    # Workflow components
    # Note: This field accepts both converter names (strings) and AnyConverter objects
    # Example: converters=["preprocessor", DynamicCodeConverter(...), "llm_processor"]
    converters: List[Union[str, ConverterSpec, AnyConverter]] = Field(..., description="The ordered list of converters in the workflow pipeline (can be converter names or converter objects)")
    definitions: List[Union[ConverterPromptTemplate, Behavior]] = Field(
        default_factory=list,
        description="Local definitions (templates, behaviors) used within this workflow"
    )
    
    # Workflow configuration
    stop_on_error: bool = Field(default=True, description="Whether to stop processing if a converter fails")
    max_retries: int = Field(default=0, description="Maximum number of retries for failed converters")
    timeout_seconds: Optional[int] = Field(None, description="Timeout for the entire workflow execution")
    
    @model_validator(mode='before')
    @classmethod
    def validate_converters(cls, values):
        """Validate that converters are strings, AnyConverter objects, or ConverterSpec objects."""
        if isinstance(values, dict) and 'converters' in values:
            converters = values['converters']
            if not isinstance(converters, list):
                raise ValueError("Converters must be a list")
            
            validated_converters = []
            for converter in converters:
                if isinstance(converter, str):
                    # String converter name - keep as is
                    validated_converters.append(converter)
                elif isinstance(converter, (StaticConverter, LLMConverter, DynamicCodeConverter)):
                    # AnyConverter object - keep as is
                    validated_converters.append(converter)
                elif isinstance(converter, ConverterSpec):
                    # ConverterSpec object - keep as is
                    validated_converters.append(converter)
                elif isinstance(converter, dict):
                    # Dictionary from serialization - let Pydantic handle it
                    validated_converters.append(converter)
                else:
                    raise ValueError(f"Converter must be a string, AnyConverter object, or ConverterSpec object, got {type(converter)}")
            
            values['converters'] = validated_converters
        
        return values
    
    
    


class PromptConverterWorkflowResult(BaseModel):
    """The result of executing a prompt converter workflow."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    final_output: ConverterResult = Field(..., description="The final output from the workflow")
    success: bool = Field(..., description="Whether the workflow executed successfully")
    error_message: Optional[str] = Field(None, description="Error message if the workflow failed")
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"PromptConverterWorkflowResult({status}): {self.final_output}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary for serialization."""
        return {
            "success": self.success,
            "final_output": {
                "output_text": self.final_output.output_text,
                "output_type": self.final_output.output_type
            },
            "error_message": self.error_message
        }