"""v0.9.0 Migration - Add client_type for unified cross-platform analytics"""

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


import aiosqlite

from ..migration_manager import Migration


async def upgrade(db: aiosqlite.Connection) -> None:
    """
    Add client_type column to track which interface was used.

    This enables unified analytics across all Aii clients:
    - "cli": Terminal interface (direct `aii` commands)
    - "vscode": VSCode extension
    - "chrome": Chrome browser extension
    - "api": Direct API calls (programmatic usage)

    This migration adds:
    - client_type: Client interface identifier (enum-like string)

    Benefits:
    - Track usage patterns across different interfaces
    - Analyze cost by client type
    - Understand user workflow preferences
    - Enable cross-platform usage insights
    """

    # Check if column already exists
    async with db.execute("PRAGMA table_info(executions)") as cursor:
        existing_columns = {row[1] for row in await cursor.fetchall()}

    if "client_type" not in existing_columns:
        # Add client_type column with default value "cli" for existing records
        await db.execute(
            """
            ALTER TABLE executions
            ADD COLUMN client_type TEXT DEFAULT 'cli'
            """
        )

        # Create index for client_type queries
        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_executions_client_type
            ON executions (client_type)
            """
        )

        # Create composite index for client+timestamp queries
        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_executions_client_timestamp
            ON executions (client_type, timestamp DESC)
            """
        )


# Migration definition
migration = Migration(
    version=3,
    name="add_client_type",
    description="Add client_type column for unified cross-platform analytics (v0.9.0)",
    up=upgrade,
)
