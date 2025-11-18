from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .base import (
    BasePromptTemplateParam,
    BasePromptTemplateConversation,
    BasePromptTemplateRepo,
)


class AppPromptParam(BasePromptTemplateParam):
    pass


class AppPrompt(BasePromptTemplateConversation):
    pass

class AppPromptTemplateConfig(BaseModel):
    type: Literal["prompt"] = Field(
        "prompt", description="Type is always set to 'prompt'."
    )
    full_name: str = Field(description="Repo Full Name")
    prompt: Optional[AppPrompt] = Field(
        default=None, description="Template Details"
    )
    params: Optional[List[AppPromptParam]] = Field(
        None,
        description="Optional list of parameters that can be replaced with values.",
    )


# Concrete implementation for App Prompt
class AppPromptTemplate(BasePromptTemplateRepo):
    provider: Literal["prompt"] = Field(
        "prompt", description="Prompt ID, always set to 'prompt'."
    )
    config: AppPromptTemplateConfig

    def get_template(self) -> BasePromptTemplateConversation:
        if not self.config.prompt:
            raise ValueError("Prompt template is not configured.")
        return self.config.prompt

    def get_params(self) -> Optional[List[AppPromptParam]]:
        return self.config.params


class AppPromptTemplates(BaseModel):
    prompts: List[AppPromptTemplate]
