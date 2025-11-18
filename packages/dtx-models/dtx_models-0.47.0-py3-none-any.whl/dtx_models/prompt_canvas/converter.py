import json
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .base import PromptCanvasBase

# --- Prompt Data Types ---
PromptDataType = Literal[
    "text",
    "image_path",
    "audio_path",
    "video_path",
    "url",
    "reasoning",
    "error",
    "function_call",
    "tool_call",
    "function_call_output",
]

class ConverterResult:
    """The result of a prompt conversion, containing the converted output and its type."""

    def __init__(self, output_text: str, output_type: PromptDataType):
        self.output_text = output_text
        self.output_type = output_type

    def __str__(self):
        return f"{self.output_type}: {self.output_text}"

# --- 1. Base Class for Common Fields ---
class BaseConverter(PromptCanvasBase):
    name: str = Field(..., description="A unique, machine-readable identifier for the converter.")
    display_name: Optional[str] = Field(None, description="An optional, user-friendly name for display purposes.")
    description: str = Field(..., description="A brief explanation of what the converter does.")

# --- 2. Enhanced Parameter Schema ---
class ConverterParameter(BaseModel):
    """Enhanced parameter schema with validation constraints and metadata."""
    name: str = Field(..., description="Parameter identifier")
    description: str = Field(..., description="Human-readable description of what the parameter does")
    type: Literal["string", "integer", "float", "boolean", "array", "regex"] = Field(..., description="Data type of the parameter")
    required: bool = Field(default=False, description="Whether the parameter is mandatory")
    default: Optional[Any] = Field(default=None, description="Default value if not specified")
    
    # Validation constraints
    min_value: Optional[Union[int, float]] = Field(default=None, description="Minimum value for numeric parameters")
    max_value: Optional[Union[int, float]] = Field(default=None, description="Maximum value for numeric parameters")
    enum: Optional[List[Any]] = Field(default=None, description="Allowed values for the parameter")
    item_type: Optional[Literal["string", "integer", "float", "boolean"]] = Field(default=None, description="Type of array items")
    
    @model_validator(mode='after')
    def validate_parameter(self) -> 'ConverterParameter':
        """Validate parameter constraints."""
        if self.type in ["integer", "float"]:
            if self.min_value is not None and self.max_value is not None:
                if self.min_value > self.max_value:
                    raise ValueError(f"min_value ({self.min_value}) cannot be greater than max_value ({self.max_value})")
        
        if self.type == "array" and self.item_type is None:
            raise ValueError("item_type must be specified for array parameters")
        
        if self.enum is not None and self.default is not None:
            if self.default not in self.enum:
                raise ValueError(f"default value ({self.default}) must be one of the allowed enum values: {self.enum}")
        
        return self

# --- 3. The Three Core Category-Level Schemas ---

class StaticConverter(BaseConverter):
    converter_type: Literal["static"] = "static"
    class_name: str = Field(..., description="The name of the Python class that implements this converter.")
    parameters_schema: List[ConverterParameter] = Field(default_factory=list, description="Schema defining parameter validation and metadata")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Actual parameter values")
    
    @model_validator(mode='after')
    def validate_parameters(self) -> 'StaticConverter':
        """Validate parameters against the schema."""
        if self.parameters_schema:
            self._validate_parameters_against_schema()
        return self
    
    def _validate_parameters_against_schema(self):
        """Validate parameters against the defined schema."""
        schema_dict = {param.name: param for param in self.parameters_schema}
        
        for param_name, param_value in self.parameters.items():
            if param_name not in schema_dict:
                raise ValueError(f"Unknown parameter '{param_name}' not defined in schema")
            
            param_schema = schema_dict[param_name]
            self._validate_parameter_value(param_name, param_value, param_schema)
    
    def _validate_parameter_value(self, param_name: str, value: Any, schema: ConverterParameter):
        """Validate a single parameter value against its schema."""
        # Type validation
        if schema.type == "string" and not isinstance(value, str):
            raise ValueError(f"Parameter '{param_name}' must be a string, got {type(value)}")
        elif schema.type == "integer" and not isinstance(value, int):
            raise ValueError(f"Parameter '{param_name}' must be an integer, got {type(value)}")
        elif schema.type == "float" and not isinstance(value, (int, float)):
            raise ValueError(f"Parameter '{param_name}' must be a float, got {type(value)}")
        elif schema.type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Parameter '{param_name}' must be a boolean, got {type(value)}")
        elif schema.type == "array" and not isinstance(value, list):
            raise ValueError(f"Parameter '{param_name}' must be an array, got {type(value)}")
        elif schema.type == "regex" and not isinstance(value, str):
            raise ValueError(f"Parameter '{param_name}' must be a string (regex pattern), got {type(value)}")
        
        # Regex pattern validation
        if schema.type == "regex" and isinstance(value, str):
            try:
                import re
                re.compile(value)
            except re.error as e:
                raise ValueError(f"Parameter '{param_name}' contains invalid regex pattern: {e}")
        
        # Range validation for numeric types
        if schema.type in ["integer", "float"] and isinstance(value, (int, float)):
            if schema.min_value is not None and value < schema.min_value:
                raise ValueError(f"Parameter '{param_name}' value {value} is below minimum {schema.min_value}")
            if schema.max_value is not None and value > schema.max_value:
                raise ValueError(f"Parameter '{param_name}' value {value} is above maximum {schema.max_value}")
        
        # Enum validation
        if schema.enum is not None and value not in schema.enum:
            raise ValueError(f"Parameter '{param_name}' value {value} is not in allowed values: {schema.enum}")
        
        # Array item type validation
        if schema.type == "array" and schema.item_type:
            for i, item in enumerate(value):
                if schema.item_type == "string" and not isinstance(item, str):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a string, got {type(item)}")
                elif schema.item_type == "integer" and not isinstance(item, int):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be an integer, got {type(item)}")
                elif schema.item_type == "float" and not isinstance(item, (int, float)):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a float, got {type(item)}")
                elif schema.item_type == "boolean" and not isinstance(item, bool):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a boolean, got {type(item)}")
    
    def apply_default_values(self):
        """Apply default values from schema to parameters that are missing."""
        schema_dict = {param.name: param for param in self.parameters_schema}
        
        for param_name, param_schema in schema_dict.items():
            if param_name not in self.parameters and param_schema.default is not None:
                self.parameters[param_name] = param_schema.default

class LLMConverter(BaseConverter):
    converter_type: Literal["llm"] = "llm"
    converter_target: str = Field(
        ...,
        description="The target for execution, in 'provider/model_name' format (e.g., 'google/gemini-1.5-pro').",
        pattern=r"^[^/]+/.+$"
    )
    class_name: Optional[str] = Field(None, description="The class name for an 'inbuilt' LLM converter.")
    template: Optional[str] = Field(None, description="The raw prompt template for a 'custom' converter.")
    prompt_template_id: Optional[str] = Field(None, description="The ID of a registered prompt template.")
    parameters_schema: List[ConverterParameter] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def check_llm_configuration(self) -> 'LLMConverter':
        if self.class_name:
            if self.template:
                raise ValueError("For an inbuilt converter (with 'class_name'), the raw 'template' field must not be set. Use 'prompt_template_id' to override its default template.")
        else:
            if (self.template is None) == (self.prompt_template_id is None):
                raise ValueError("For a custom converter, exactly one of 'template' or 'prompt_template_id' must be provided.")
        
        # Validate parameters against schema
        if self.parameters_schema:
            self._validate_parameters_against_schema()
        return self
    
    def _validate_parameters_against_schema(self):
        """Validate parameters against the defined schema."""
        schema_dict = {param.name: param for param in self.parameters_schema}
        
        for param_name, param_value in self.parameters.items():
            if param_name not in schema_dict:
                raise ValueError(f"Unknown parameter '{param_name}' not defined in schema")
            
            param_schema = schema_dict[param_name]
            self._validate_parameter_value(param_name, param_value, param_schema)
    
    def _validate_parameter_value(self, param_name: str, value: Any, schema: ConverterParameter):
        """Validate a single parameter value against its schema."""
        # Type validation
        if schema.type == "string" and not isinstance(value, str):
            raise ValueError(f"Parameter '{param_name}' must be a string, got {type(value)}")
        elif schema.type == "integer" and not isinstance(value, int):
            raise ValueError(f"Parameter '{param_name}' must be an integer, got {type(value)}")
        elif schema.type == "float" and not isinstance(value, (int, float)):
            raise ValueError(f"Parameter '{param_name}' must be a float, got {type(value)}")
        elif schema.type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Parameter '{param_name}' must be a boolean, got {type(value)}")
        elif schema.type == "array" and not isinstance(value, list):
            raise ValueError(f"Parameter '{param_name}' must be an array, got {type(value)}")
        elif schema.type == "regex" and not isinstance(value, str):
            raise ValueError(f"Parameter '{param_name}' must be a string (regex pattern), got {type(value)}")
        
        # Regex pattern validation
        if schema.type == "regex" and isinstance(value, str):
            try:
                import re
                re.compile(value)
            except re.error as e:
                raise ValueError(f"Parameter '{param_name}' contains invalid regex pattern: {e}")
        
        # Range validation for numeric types
        if schema.type in ["integer", "float"] and isinstance(value, (int, float)):
            if schema.min_value is not None and value < schema.min_value:
                raise ValueError(f"Parameter '{param_name}' value {value} is below minimum {schema.min_value}")
            if schema.max_value is not None and value > schema.max_value:
                raise ValueError(f"Parameter '{param_name}' value {value} is above maximum {schema.max_value}")
        
        # Enum validation
        if schema.enum is not None and value not in schema.enum:
            raise ValueError(f"Parameter '{param_name}' value {value} is not in allowed values: {schema.enum}")
        
        # Array item type validation
        if schema.type == "array" and schema.item_type:
            for i, item in enumerate(value):
                if schema.item_type == "string" and not isinstance(item, str):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a string, got {type(item)}")
                elif schema.item_type == "integer" and not isinstance(item, int):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be an integer, got {type(item)}")
                elif schema.item_type == "float" and not isinstance(item, (int, float)):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a float, got {type(item)}")
                elif schema.item_type == "boolean" and not isinstance(item, bool):
                    raise ValueError(f"Parameter '{param_name}' array item {i} must be a boolean, got {type(item)}")
    
    def apply_default_values(self):
        """Apply default values from schema to parameters that are missing."""
        schema_dict = {param.name: param for param in self.parameters_schema}
        
        for param_name, param_schema in schema_dict.items():
            if param_name not in self.parameters and param_schema.default is not None:
                self.parameters[param_name] = param_schema.default

class DynamicCodeConverter(BaseConverter):
    converter_type: Literal["dynamic_code"] = "dynamic_code"
    requirements: List[str] = Field(default_factory=list)
    code: str = Field(..., description="A string containing a Python script that defines the function: async def convert(prompt: str) -> ConverterReturnType")

# --- 4. Type Aliases ---
ConverterReturnType = Union[str, ConverterResult]

# --- 5. The Final Union Type ---
AnyConverter = Union[StaticConverter, LLMConverter, DynamicCodeConverter]

def create_converter(data: Dict[str, Any]) -> AnyConverter:
    """
    Factory function to create the appropriate converter type based on the data.
    """
    converter_type = data.get("converter_type")
    
    if converter_type == "static":
        return StaticConverter(**data)
    elif converter_type == "llm":
        return LLMConverter(**data)
    elif converter_type == "dynamic_code":
        return DynamicCodeConverter(**data)
    else:
        raise ValueError(f"Unknown converter type: {converter_type}")


def normalize_converter_result(result: ConverterReturnType) -> ConverterResult:
    """
    Normalize a converter result to always return a ConverterResult object.
    
    Args:
        result: Either a string or ConverterResult from a converter
        
    Returns:
        ConverterResult: Normalized result object
    """
    if isinstance(result, ConverterResult):
        return result
    elif isinstance(result, str):
        return ConverterResult(output_text=result, output_type="text")
    else:
        raise TypeError(f"Converter must return str or ConverterResult, got {type(result)}")


# Example usage functions
def create_text_result(text: str) -> ConverterResult:
    """Create a text result."""
    return ConverterResult(output_text=text, output_type="text")


def create_error_result(error_message: str) -> ConverterResult:
    """Create an error result."""
    return ConverterResult(output_text=error_message, output_type="error")


def create_reasoning_result(reasoning: str) -> ConverterResult:
    """Create a reasoning result."""
    return ConverterResult(output_text=reasoning, output_type="reasoning")