"""Initial schema migration - Baseline schema for Aii CLI storage"""

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
    """Create initial schema for chat storage"""
    await db.executescript(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            metadata TEXT DEFAULT '{}',
            archived BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            message_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS chat_tags (
            chat_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (chat_id, tag),
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            function_name TEXT NOT NULL,
            parameters TEXT DEFAULT '{}',
            result TEXT DEFAULT '{}',
            timestamp TIMESTAMP NOT NULL,
            success BOOLEAN DEFAULT FALSE
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats (updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_chats_archived ON chats (archived);
        CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id);
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp);
        CREATE INDEX IF NOT EXISTS idx_chat_tags_tag ON chat_tags (tag);
        CREATE INDEX IF NOT EXISTS idx_executions_chat_id ON executions (chat_id);
        """
    )


# Migration definition
migration = Migration(
    version=1,
    name="initial_schema",
    description="Create baseline schema for chats, messages, tags, and executions",
    up=upgrade,
)
