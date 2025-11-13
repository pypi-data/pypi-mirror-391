"""Pydantic models for API requests and responses."""

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



from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, List

# Export error models for use in routes
from .errors import ErrorResponse, ErrorDetail, ErrorCode


class ExecuteRequest(BaseModel):
    """Request to execute AII function.

    Supports two execution patterns:
    1. Natural Language (LLM-First): Provide 'user_prompt' for natural language input
    2. Direct Execution: Provide 'function' + 'params' for explicit function calls

    Examples:
        # Pattern 1: Natural language (like WebSocket)
        {"user_prompt": "translate hello to spanish", "model": "gpt-4o"}

        # Pattern 2: Direct execution (backward compatible)
        {"function": "translate", "params": {"text": "hello", "target_language": "spanish"}}
    """

    # Pattern selection (one required)
    user_prompt: Optional[str] = Field(default=None, description="Natural language request (LLM-first pattern)")
    function: Optional[str] = Field(default=None, description="Function name to execute (direct pattern)")

    # Common fields
    params: Dict[str, Any] = Field(default_factory=dict, description="Function parameters (direct pattern only)")
    streaming: bool = Field(default=False, description="Enable streaming response")
    model: Optional[str] = Field(default=None, description="Model override (e.g., 'kimi-k2-thinking')")  # v0.8.0
    provider: Optional[str] = Field(default=None, description="Provider override (auto-detected if omitted)")  # v0.8.0

    @model_validator(mode='after')
    def validate_pattern(self):
        """Validate that exactly one pattern is provided."""
        has_user_prompt = self.user_prompt is not None
        has_function = self.function is not None

        if not has_user_prompt and not has_function:
            raise ValueError("Must provide either 'user_prompt' (natural language) or 'function' (direct execution)")

        if has_user_prompt and has_function:
            raise ValueError("Cannot provide both 'user_prompt' and 'function' - choose one pattern")

        if has_user_prompt and self.params:
            raise ValueError("'params' field only valid with 'function' pattern, not 'user_prompt'")

        return self

    def get_formatted_input(self) -> str:
        """
        Format as natural language input for engine.

        The engine will recognize the function and parameters through
        its LLM-first intent recognition system.
        """
        # v0.8.0: Support both patterns
        if self.user_prompt:
            return self.user_prompt

        if not self.params:
            return self.function

        # Format parameters as key=value pairs
        param_str = " ".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.function} {param_str}"


class ExecuteResponse(BaseModel):
    """Response from function execution."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FunctionInfo(BaseModel):
    """Function metadata."""

    name: str
    description: str
    parameters: Dict[str, Any]
    safety: str
    default_output_mode: Optional[str] = None


class FunctionsResponse(BaseModel):
    """List of available functions."""

    functions: List[FunctionInfo]


class StatusResponse(BaseModel):
    """Server health status."""

    status: str
    version: str
    uptime: float
    mcp_servers: Optional[Dict[str, int]] = None
    initialization: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Initialization status for LLM provider and integrations"
    )


class MCPStatusRequest(BaseModel):
    """Request MCP server status."""

    server_name: Optional[str] = Field(
        default=None,
        description="Specific server name (null for all servers)"
    )


# v0.8.0: Models endpoint response models
class ModelInfo(BaseModel):
    """Information about a specific model."""

    name: str = Field(..., description="Model identifier (e.g., 'gpt-4.1-mini')")
    display_name: str = Field(..., description="Human-readable model name")
    available: bool = Field(..., description="Whether this model can be used (API key configured)")
    is_default: bool = Field(..., description="Whether this is the default model")
    is_custom: bool = Field(..., description="Whether this is a custom user-configured model")
    cost_tier: str = Field(..., description="Cost tier: 'free', 'cheap', 'standard', 'premium', 'expensive'")
    description: str = Field(..., description="Brief description of model capabilities")


class ProviderInfo(BaseModel):
    """Information about a model provider."""

    name: str = Field(..., description="Provider identifier (lowercase)")
    display_name: str = Field(..., description="Human-readable provider name")
    configured: bool = Field(..., description="Whether API key is configured for this provider")
    api_key_env_var: Optional[str] = Field(..., description="Environment variable name for API key")
    models: List[ModelInfo] = Field(..., description="List of models for this provider")


class FlatModelInfo(BaseModel):
    """Flattened model info for simple dropdowns."""

    name: str = Field(..., description="Model identifier")
    provider: str = Field(..., description="Provider identifier")
    available: bool = Field(..., description="Whether this model can be used")
    is_default: bool = Field(..., description="Whether this is the default model")


class ModelsResponse(BaseModel):
    """Response for /api/models endpoint."""

    default_model: str = Field(..., description="Currently configured default model name")
    default_provider: str = Field(..., description="Provider of the default model")
    total_models: int = Field(..., description="Total number of models across all providers")
    available_models: int = Field(..., description="Number of models with API keys configured")
    providers: List[ProviderInfo] = Field(..., description="Detailed provider and model information")
    flat_models: List[FlatModelInfo] = Field(..., description="Flattened list of all models (for simple dropdowns)")
