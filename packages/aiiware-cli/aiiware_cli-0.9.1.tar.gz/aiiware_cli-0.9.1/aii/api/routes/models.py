"""Models endpoint - List available models and providers."""

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


from fastapi import APIRouter, HTTPException, Depends
import os

from aii.api.models import ModelsResponse, ProviderInfo, ModelInfo, FlatModelInfo
from aii.api.middleware import verify_api_key, check_rate_limit, get_server_instance
from aii.data.providers.model_registry import (
    get_available_models,
    get_model_metadata,
    get_provider_metadata,
    MODEL_METADATA
)

router = APIRouter()


@router.get("/api/models", response_model=ModelsResponse)
async def list_models(
    api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    List all available models and their configuration status.

    Returns information about:
    - All registered models across all providers
    - Which models are available (API key configured)
    - The default model currently in use
    - Custom user-configured models

    Response:
    ```json
    {
      "default_model": "deepseek-chat",
      "default_provider": "deepseek",
      "total_models": 26,
      "available_models": 8,
      "providers": [
        {
          "name": "openai",
          "display_name": "OpenAI",
          "configured": true,
          "api_key_env_var": "OPENAI_API_KEY",
          "models": [...]
        }
      ],
      "flat_models": [...]
    }
    ```
    """
    server = get_server_instance()

    if not server:
        raise HTTPException(status_code=500, detail="Server not initialized")

    # Get default model from config
    default_model = server.config.get("llm.model", "deepseek-chat")
    default_provider = server.config.get("llm.provider", "deepseek")

    # Get all models from registry
    all_models = get_available_models()

    providers_info = []
    flat_models = []
    total_models = 0
    available_models = 0

    for provider_name, models in all_models.items():
        # Get provider metadata
        provider_meta = get_provider_metadata(provider_name)
        api_key_env_var = provider_meta.get("api_key_env_var")

        # Check if provider is configured (API key exists)
        configured = _is_provider_configured(provider_name, api_key_env_var)

        # Build model info list
        model_infos = []
        for model_name in models:
            meta = get_model_metadata(provider_name, model_name)
            is_default = (model_name == default_model)

            model_info = ModelInfo(
                name=model_name,
                display_name=meta.get("display_name", model_name),
                available=configured,
                is_default=is_default,
                is_custom=False,  # TODO: Detect custom models from config
                cost_tier=meta.get("cost_tier", "standard"),
                description=meta.get("description", "")
            )
            model_infos.append(model_info)

            # Add to flat list
            flat_models.append(FlatModelInfo(
                name=model_name,
                provider=provider_name,
                available=configured,
                is_default=is_default
            ))

            total_models += 1
            if configured:
                available_models += 1

        # Add provider info
        providers_info.append(ProviderInfo(
            name=provider_name,
            display_name=provider_meta.get("display_name", provider_name.title()),
            configured=configured,
            api_key_env_var=api_key_env_var,
            models=model_infos
        ))

    return ModelsResponse(
        default_model=default_model,
        default_provider=default_provider,
        total_models=total_models,
        available_models=available_models,
        providers=providers_info,
        flat_models=flat_models
    )


def _is_provider_configured(provider_name: str, api_key_env_var: str | None) -> bool:
    """
    Check if provider API key is configured.

    Args:
        provider_name: Provider name
        api_key_env_var: Environment variable name for API key

    Returns:
        True if API key is configured, False otherwise
    """
    if not api_key_env_var:
        return False

    # Check if API key exists in environment
    api_key = os.getenv(api_key_env_var)
    return api_key is not None and len(api_key) > 0
