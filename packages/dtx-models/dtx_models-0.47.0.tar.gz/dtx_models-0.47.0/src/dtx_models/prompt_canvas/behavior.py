import uuid
from datetime import datetime
from typing import List, Literal, Optional, Union
from .base import PromptCanvasBase
from pydantic import BaseModel, Field, HttpUrl, model_validator


# --- Evaluation Criterion Schemas (Unchanged) ---

class PromptBasedEvaluation(BaseModel):
    """
    Defines an evaluation that requires an LLM to assess the outcome.
    The prompt instructs the LLM on how to score or classify the test result.
    """
    criterion_type: Literal["prompt_based"] = "prompt_based"
    prompt_text: Optional[str] = Field(None, description="The raw prompt template text for the evaluation.")
    prompt_template_id: Optional[str] = Field(None, description="The ID of a registered prompt template for evaluation.")

    @model_validator(mode='after')
    def check_prompt_source(self) -> 'PromptBasedEvaluation':
        """Ensures exactly one prompt source is provided."""
        if (self.prompt_text is None) == (self.prompt_template_id is None):
            raise ValueError("For prompt_based_evaluation, exactly one of 'prompt_text' or 'prompt_template_id' must be provided.")
        return self

class TargetResponseEvaluation(BaseModel):
    """
    Defines an evaluation based on the presence or absence of specific text in the model's response.
    """
    criterion_type: Literal["target_response"] = "target_response"
    expected_response: str = Field(..., description="The string or regex pattern to look for in the response.")
    match_type: Literal["exact_match", "contains", "regex"] = Field(
        "contains",
        description="The method to use for matching the expected_response."
    )


# --- Main Behavior Schema (Inherits from PromptCanvasBase) ---

class Behavior(PromptCanvasBase):
    """
    Defines the strategic goal of a test, including its objective, metadata, and evaluation criteria.
    """
    behavior_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="A unique identifier for the behavior."
    )
    name: str = Field(..., description="A short, descriptive name for the behavior (e.g., 'Elicit Harmful Content').")
    display_name: Optional[str] = Field(None, description="A user-friendly display name for the behavior.")
    description: str = Field(..., description="A detailed explanation of the behavior being tested.")
    prompt: Optional[str] = Field(None, description="The prompt text for this behavior.")
    
    evaluation_criterion: Optional[Union[PromptBasedEvaluation, TargetResponseEvaluation]] = Field(
        None,
        discriminator="criterion_type",
        description="The specific method and criteria for evaluating the test's outcome. Can be null."
    )
    
    policies: Optional[List[str]] = Field(
        None,
        description="A list of policy violations this behavior is designed to test."
    )
    tags: Optional[List[str]] = Field(
        None,
        description="A list of keywords for categorization and searching."
    )
    source: Optional[HttpUrl] = Field(
        None,
        description="An optional URL pointing to the origin or reference for this behavior."
    )

# --- Usage Example ---
if __name__ == "__main__":
    # Create a new behavior instance
    behavior_instance = Behavior(
        name="Test Inheritance",
        description="A simple test to show the inherited fields.",
        created_by="system-init"
    )

    # Print the resulting JSON object
    # Notice that `created_at` and `updated_at` are automatically populated.
    print(behavior_instance.model_dump_json(indent=2))
