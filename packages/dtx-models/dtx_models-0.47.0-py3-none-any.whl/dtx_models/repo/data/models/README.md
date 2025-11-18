# Model Configuration Files

This directory contains model configuration files for various AI providers. These YAML files define the available models and their configurations for different providers.

## File Structure

### Provider Model Files
- `anthropic_models.yml` - Anthropic Claude models
- `azure_models.yml` - Azure OpenAI models  
- `bedrock_claude_models.yml` - AWS Bedrock Claude models
- `cerebras_models.yml` - Cerebras models
- `gemini_models.yml` - Google Gemini models
- `hf_models.yml` - Hugging Face models
- `mistral_models.yml` - Mistral models
- `openai_models.yml` - OpenAI models

### LiteLLM Model Files
- `litellm_models_ag.yml` - LiteLLM models (AG category)
- `litellm_models_lr.yml` - LiteLLM models (LR category)
- `litellm_models_sz.yml` - LiteLLM models (SZ category)

## Usage

These files are automatically loaded by the model repository system when using:

```python
from dtx_models.repo.models_repo import ModelRegistry, AnthropicModelsRepo, OpenAIModelsRepo

# Load all models
registry = ModelRegistry()
all_models = registry.list_all_models()

# Load specific provider models
anthropic_repo = AnthropicModelsRepo()
anthropic_models = anthropic_repo.list_models()

# Search models
results = registry.search_by_keyword("claude")
```

## File Format

Model files use YAML format with provider-specific structures:

### Standard Provider Format
```yaml
provider_name:
  - model: "model-name"
    # ... provider-specific configuration
```

### LiteLLM Format
```yaml
litellm:
  - model: "provider/model-name"
    # ... litellm-specific configuration
```

## Notes

- These files are included in the package distribution
- Model configurations are loaded automatically by the repository system
- Each provider has its own configuration schema
- LiteLLM files are merged from multiple files for comprehensive coverage
