"""Model Pricing - Token pricing for LLM cost calculation"""

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


# Pricing per 1M tokens (input, output) in USD
MODEL_PRICING = {
    # OpenAI GPT-5 models
    "gpt-5": {"input": 10.00, "output": 30.00},
    "gpt-5.1": {"input": 10.00, "output": 30.00},  # New flagship model (2025-11-14)
    # OpenAI GPT-4 models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1-mini": {"input": 0.15, "output": 0.60},  # Alias for gpt-4o-mini
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    # OpenAI GPT-3.5 models
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    # Anthropic Claude models
    "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    # Google Gemini models
    "gemini-2.0-flash": {"input": 0.00, "output": 0.00},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    # DeepSeek models
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost in USD"""
    # Strip provider prefix if present (e.g., "openai:gpt-4o-mini" -> "gpt-4o-mini")
    model_name = model.split(":")[-1] if ":" in model else model

    pricing = MODEL_PRICING.get(model_name.lower())
    if not pricing:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
