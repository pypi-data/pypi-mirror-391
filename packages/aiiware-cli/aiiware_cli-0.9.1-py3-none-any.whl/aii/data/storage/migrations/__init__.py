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

"""Database migrations for Aii CLI storage"""

# Import migration definitions
from .migrations_001_initial_schema import migration as migration_001_initial_schema
from .migrations_002_enhance_executions import (
    migration as migration_002_enhance_executions,
)
from .migrations_003_add_client_type import migration as migration_003_add_client_type
from .migrations_004_backfill_costs import migration as migration_004_backfill_costs
from .migrations_005_normalize_model_names import (
    migration as migration_005_normalize_model_names,
)

__all__ = [
    "migration_001_initial_schema",
    "migration_002_enhance_executions",
    "migration_003_add_client_type",
    "migration_004_backfill_costs",
    "migration_005_normalize_model_names",
]
