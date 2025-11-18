"""Model Registry - Maps model names to providers."""

# Copyright 2025-present aiiware.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Model → Provider mapping
# This registry enables auto-detection of provider from model name
MODEL_PROVIDER_MAP = {
    # OpenAI models
    "gpt-5": "openai",
    "gpt-5.1": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4.1-mini": "openai",
    "gpt-4-turbo": "openai",
    "gpt-4-turbo-preview": "openai",
    "gpt-4": "openai",
    "gpt-3.5-turbo": "openai",
    "gpt-3.5-turbo-16k": "openai",

    # Anthropic models
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    "claude-sonnet-4.5": "anthropic",
    "claude-haiku-4.5": "anthropic",
    "claude-opus-4": "anthropic",

    # Google Gemini models
    "gemini-1.5-pro": "gemini",
    "gemini-1.5-flash": "gemini",
    "gemini-pro": "gemini",
    "gemini-pro-vision": "gemini",

    # Moonshot models
    "kimi-k2-0905-preview": "moonshot",
    "kimi-k2-turbo-preview": "moonshot",
    "kimi-k2-thinking": "moonshot",
    "kimi-k2-thinking-turbo": "moonshot",

    # DeepSeek models
    "deepseek-chat": "deepseek",
    "deepseek-coder": "deepseek",
}


def detect_provider_from_model(model: str) -> str:
    """
    Auto-detect provider from model name.

    Args:
        model: Model name (e.g., 'kimi-k2-thinking', 'gpt-4.1-mini')

    Returns:
        Provider name (e.g., 'moonshot', 'openai')

    Raises:
        ValueError: If model is not recognized

    Example:
        >>> detect_provider_from_model("kimi-k2-thinking")
        'moonshot'
        >>> detect_provider_from_model("gpt-4.1-mini")
        'openai'
        >>> detect_provider_from_model("invalid-model")
        Traceback (most recent call last):
            ...
        ValueError: Model 'invalid-model' not recognized...
    """
    # Try exact match first
    provider = MODEL_PROVIDER_MAP.get(model)
    if provider:
        return provider

    # Try prefix matching for flexible model names
    # Example: "gpt-4-turbo-2024-04-09" matches "gpt-4-turbo"
    for model_name, provider_name in MODEL_PROVIDER_MAP.items():
        if model.startswith(model_name):
            return provider_name

    # Model not found - provide helpful error
    available_models = sorted(MODEL_PROVIDER_MAP.keys())
    raise ValueError(
        f"Model '{model}' not recognized. "
        f"Available models: {', '.join(available_models)}"
    )


def get_available_models() -> dict[str, list[str]]:
    """
    Get all available models grouped by provider.

    Returns:
        Dictionary mapping provider → list of models

    Example:
        >>> models = get_available_models()
        >>> 'openai' in models
        True
        >>> 'gpt-4.1-mini' in models['openai']
        True
        >>> 'kimi-k2-thinking' in models['moonshot']
        True
    """
    result: dict[str, list[str]] = {}

    for model, provider in MODEL_PROVIDER_MAP.items():
        if provider not in result:
            result[provider] = []
        result[provider].append(model)

    # Sort models within each provider for better readability
    for provider in result:
        result[provider].sort()

    return result


def validate_model_provider_match(model: str, provider: str) -> bool:
    """
    Validate that a model belongs to the specified provider.

    Args:
        model: Model name
        provider: Provider name

    Returns:
        True if model belongs to provider, False otherwise

    Example:
        >>> validate_model_provider_match("gpt-4.1-mini", "openai")
        True
        >>> validate_model_provider_match("gpt-4.1-mini", "anthropic")
        False
    """
    try:
        detected_provider = detect_provider_from_model(model)
        return detected_provider == provider
    except ValueError:
        # Model not recognized
        return False


def get_models_for_provider(provider: str) -> list[str]:
    """
    Get all models available for a specific provider.

    Args:
        provider: Provider name (openai, anthropic, gemini, moonshot, deepseek)

    Returns:
        List of model names for that provider

    Example:
        >>> models = get_models_for_provider("openai")
        >>> "gpt-4.1-mini" in models
        True
        >>> models = get_models_for_provider("moonshot")
        >>> "kimi-k2-thinking" in models
        True
    """
    all_models = get_available_models()
    return all_models.get(provider, [])


# v0.8.0: Model metadata with display names, cost tiers, and descriptions
MODEL_METADATA = {
    "openai": {
        "display_name": "OpenAI",
        "api_key_env_var": "OPENAI_API_KEY",
        "models": {
            "gpt-5": {
                "display_name": "GPT-5",
                "cost_tier": "premium",
                "description": "Best for coding and agentic tasks"
            },
            "gpt-5.1": {
                "display_name": "GPT-5.1",
                "cost_tier": "premium",
                "description": "Flagship model with improved reasoning and speed"
            },
            "gpt-4o": {
                "display_name": "GPT-4o",
                "cost_tier": "premium",
                "description": "Most capable GPT-4 model with vision capabilities"
            },
            "gpt-4o-mini": {
                "display_name": "GPT-4o Mini",
                "cost_tier": "cheap",
                "description": "Affordable GPT-4 model for most tasks"
            },
            "gpt-4.1-mini": {
                "display_name": "GPT-4.1 Mini",
                "cost_tier": "cheap",
                "description": "Latest mini model with improved performance"
            },
            "gpt-4-turbo": {
                "display_name": "GPT-4 Turbo",
                "cost_tier": "premium",
                "description": "High-performance GPT-4 with extended context"
            },
            "gpt-4-turbo-preview": {
                "display_name": "GPT-4 Turbo Preview",
                "cost_tier": "premium",
                "description": "Preview version of GPT-4 Turbo"
            },
            "gpt-4": {
                "display_name": "GPT-4",
                "cost_tier": "expensive",
                "description": "Original GPT-4 model"
            },
            "gpt-3.5-turbo": {
                "display_name": "GPT-3.5 Turbo",
                "cost_tier": "cheap",
                "description": "Fast and cost-effective for simple tasks"
            },
            "gpt-3.5-turbo-16k": {
                "display_name": "GPT-3.5 Turbo 16K",
                "cost_tier": "cheap",
                "description": "GPT-3.5 with extended context window"
            }
        }
    },
    "anthropic": {
        "display_name": "Anthropic",
        "api_key_env_var": "ANTHROPIC_API_KEY",
        "models": {
            "claude-3-opus-20240229": {
                "display_name": "Claude 3 Opus",
                "cost_tier": "expensive",
                "description": "Most capable Claude 3 model for complex tasks"
            },
            "claude-3-sonnet-20240229": {
                "display_name": "Claude 3 Sonnet",
                "cost_tier": "standard",
                "description": "Balanced Claude 3 model for most use cases"
            },
            "claude-3-haiku-20240307": {
                "display_name": "Claude 3 Haiku",
                "cost_tier": "cheap",
                "description": "Fast and cost-effective Claude 3 model"
            },
            "claude-sonnet-4.5": {
                "display_name": "Claude Sonnet 4.5",
                "cost_tier": "premium",
                "description": "Latest Claude model with extended context"
            },
            "claude-haiku-4.5": {
                "display_name": "Claude Haiku 4.5",
                "cost_tier": "cheap",
                "description": "Latest fast and affordable Claude model"
            },
            "claude-opus-4": {
                "display_name": "Claude Opus 4",
                "cost_tier": "expensive",
                "description": "Most advanced Claude model"
            }
        }
    },
    "gemini": {
        "display_name": "Google Gemini",
        "api_key_env_var": "GEMINI_API_KEY",
        "models": {
            "gemini-1.5-pro": {
                "display_name": "Gemini 1.5 Pro",
                "cost_tier": "premium",
                "description": "Google's most capable multimodal model"
            },
            "gemini-1.5-flash": {
                "display_name": "Gemini 1.5 Flash",
                "cost_tier": "cheap",
                "description": "Fast and cost-effective Gemini model"
            },
            "gemini-pro": {
                "display_name": "Gemini Pro",
                "cost_tier": "standard",
                "description": "Balanced Gemini model for general tasks"
            },
            "gemini-pro-vision": {
                "display_name": "Gemini Pro Vision",
                "cost_tier": "standard",
                "description": "Gemini Pro with vision capabilities"
            }
        }
    },
    "moonshot": {
        "display_name": "Moonshot AI",
        "api_key_env_var": "MOONSHOT_API_KEY",
        "models": {
            "kimi-k2-0905-preview": {
                "display_name": "Kimi K2 Preview",
                "cost_tier": "standard",
                "description": "Preview version of Kimi K2 model"
            },
            "kimi-k2-turbo-preview": {
                "display_name": "Kimi K2 Turbo Preview",
                "cost_tier": "cheap",
                "description": "Fast preview version of Kimi K2"
            },
            "kimi-k2-thinking": {
                "display_name": "Kimi K2 Thinking",
                "cost_tier": "premium",
                "description": "Advanced reasoning model with chain-of-thought"
            },
            "kimi-k2-thinking-turbo": {
                "display_name": "Kimi K2 Thinking Turbo",
                "cost_tier": "standard",
                "description": "Fast reasoning model with chain-of-thought"
            }
        }
    },
    "deepseek": {
        "display_name": "DeepSeek",
        "api_key_env_var": "DEEPSEEK_API_KEY",
        "models": {
            "deepseek-chat": {
                "display_name": "DeepSeek Chat",
                "cost_tier": "cheap",
                "description": "Ultra cost-effective for general tasks"
            },
            "deepseek-coder": {
                "display_name": "DeepSeek Coder",
                "cost_tier": "cheap",
                "description": "Specialized for code generation and understanding"
            }
        }
    }
}


def get_model_metadata(provider: str, model: str) -> dict:
    """
    Get metadata for a specific model.

    Args:
        provider: Provider name
        model: Model name

    Returns:
        Dictionary with display_name, cost_tier, description

    Example:
        >>> meta = get_model_metadata("openai", "gpt-4.1-mini")
        >>> meta["display_name"]
        'GPT-4.1 Mini'
        >>> meta["cost_tier"]
        'cheap'
    """
    provider_meta = MODEL_METADATA.get(provider, {})
    return provider_meta.get("models", {}).get(model, {
        "display_name": model,
        "cost_tier": "standard",
        "description": "Model description not available"
    })


def get_provider_metadata(provider: str) -> dict:
    """
    Get metadata for a specific provider.

    Args:
        provider: Provider name

    Returns:
        Dictionary with display_name, api_key_env_var

    Example:
        >>> meta = get_provider_metadata("openai")
        >>> meta["display_name"]
        'OpenAI'
        >>> meta["api_key_env_var"]
        'OPENAI_API_KEY'
    """
    return MODEL_METADATA.get(provider, {
        "display_name": provider.title(),
        "api_key_env_var": f"{provider.upper()}_API_KEY"
    })
