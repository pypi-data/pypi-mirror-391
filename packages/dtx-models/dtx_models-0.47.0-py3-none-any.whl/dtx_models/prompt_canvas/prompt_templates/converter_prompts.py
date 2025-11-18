import re
from typing import List, Literal, Optional

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    model_validator,
)

from ..base import PromptCanvasBase

class ConverterPromptTemplate(PromptCanvasBase):
    """
    A schema for defining prompt templates used by prompt converters.
    """

    # --- Core Identifying Fields ---
    name: str = Field(
        ...,
        description="A unique, machine-readable identifier for the template (e.g., 'noise_converter').",
    )
    display_name: Optional[str] = Field(
        None,
        description="An optional, user-friendly name for display purposes (e.g., 'Noise Injector').",
    )
    type: Literal["prompt_converter"] = Field(
        "prompt_converter",
        description="The fixed type for this template schema, used as a discriminator.",
    )
    description: str = Field(
        ...,
        description="A detailed explanation of the template's purpose and strategy.",
    )

    # --- Metadata Fields ---
    authors: List[str] = Field(
        ...,
        description="A list of the original authors of the prompt.",
    )
    groups: Optional[List[str]] = Field(
        None,
        description="Optional list of associated groups, institutions, or affiliations.",
    )
    source: Optional[HttpUrl] = Field(
        None,
        description="An optional URL to the source of the prompt.",
    )

    # --- Template Definition Fields ---
    parameters: List[str] = Field(
        default_factory=list,
        description="The names of the parameters the template expects, e.g., ['prompt', 'tone'].",
    )
    data_type: Literal["text"] = Field(
        "text",
        description="The data type this prompt operates on.",
    )
    value: str = Field(
        ...,
        description="The core prompt template string, with parameters in {{...}} format.",
    )

    @model_validator(mode='after')
    def check_parameters_match_template_value(self) -> 'PromptConverterPromptTemplate':
        """
        Validates that the parameters defined in the `parameters` list
        match the variables used in the `value` template string.
        """
        if not self.value:
            return self

        # Find all occurrences of {{parameter_name}} in the template value
        # Using a simple regex to capture the variable names inside the braces
        variables_in_template = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", self.value))
        
        # Convert the declared parameters list to a set for easy comparison
        declared_parameters = set(self.parameters)

        if variables_in_template != declared_parameters:
            raise ValueError(
                "The parameters declared in the 'parameters' field do not perfectly match the variables "
                f"used in the 'value' template. Declared: {sorted(list(declared_parameters))}, "
                f"Used: {sorted(list(variables_in_template))}"
            )
        
        return self


class ConverterPromptTemplates(BaseModel):
    templates: List[ConverterPromptTemplate]