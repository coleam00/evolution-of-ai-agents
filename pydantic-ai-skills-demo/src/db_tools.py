"""Database tools for persistent note storage using asyncpg (Neon / Postgres)."""

import logging
from typing import Any, List, Optional

import asyncpg
from pydantic_ai import RunContext

logger = logging.getLogger(__name__)

# Module-level connection pool, shared across tool calls within a process.
_pool: Optional[asyncpg.Pool] = None

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS notes (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    content    TEXT NOT NULL,
    source     TEXT NOT NULL DEFAULT 'unknown',
    tags       TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

_SEARCH_SQL = """
SELECT id, title, content, source, tags, created_at
FROM notes
WHERE title   ILIKE '%' || $1 || '%'
   OR content ILIKE '%' || $1 || '%'
   OR EXISTS (SELECT 1 FROM unnest(tags) t WHERE t ILIKE '%' || $1 || '%')
ORDER BY created_at DESC
LIMIT 20;
"""


async def _get_pool(database_url: str) -> asyncpg.Pool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        logger.info("db_pool_creating")
        _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
        # Ensure table exists
        async with _pool.acquire() as conn:
            await conn.execute(_CREATE_TABLE_SQL)
        logger.info("db_pool_created: table_ensured=True")
    return _pool


def _get_database_url(ctx: RunContext[Any]) -> Optional[str]:
    """Extract DATABASE_URL from agent settings via context deps."""
    try:
        settings = ctx.deps.settings
        if settings is None:
            from src.settings import load_settings
            settings = load_settings()
        url: Optional[str] = getattr(settings, "database_url", None)
        return url
    except Exception as e:
        logger.error(f"db_url_error: {str(e)}")
        return None


async def save_note(
    ctx: RunContext[Any],
    title: str,
    content: str,
    source: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Save a note to the Neon Postgres database.

    Inserts a new row into the notes table and returns the assigned ID and
    timestamp so the caller can confirm what was persisted.

    Args:
        ctx: Agent runtime context with dependencies
        title: Short title summarizing the note
        content: Full body of the note
        source: Optional URL or citation for the source material
        tags: Optional comma-separated tag string (e.g. "ai,research,tools")

    Returns:
        Confirmation message with the new note ID, or an error message.
    """
    database_url = _get_database_url(ctx)
    if not database_url:
        return (
            "Error: DATABASE_URL is not configured. "
            "Set DATABASE_URL in your .env file to a valid Neon Postgres connection string."
        )

    try:
        pool = await _get_pool(database_url)
        tags_list = [t.strip() for t in tags.split(",")] if tags else []

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO notes (title, content, source, tags) "
                "VALUES ($1, $2, $3, $4) RETURNING id, created_at",
                title,
                content,
                source or "unknown",
                tags_list,
            )

        note_id: int = row["id"]
        created_at = row["created_at"]
        logger.info(f"save_note_success: id={note_id}, title={title!r}")
        return (
            f"Note saved successfully.\n"
            f"ID: {note_id}\n"
            f"Title: {title}\n"
            f"Saved at: {created_at.isoformat()}"
        )

    except asyncpg.PostgresError as e:
        logger.error(f"save_note_db_error: error={str(e)}")
        return f"Error: Database error while saving note — {str(e)}"
    except Exception as e:
        logger.exception(f"save_note_error: error={str(e)}")
        return f"Error: {str(e)}"


async def search_notes(
    ctx: RunContext[Any],
    keyword: str,
) -> str:
    """
    Search saved notes by keyword.

    Performs a case-insensitive ILIKE search across the title, content, and
    tags columns. Returns up to 20 most-recent matching notes.

    Args:
        ctx: Agent runtime context with dependencies
        keyword: Search term to match against title, content, and tags

    Returns:
        Formatted list of matching notes, or an error message.
    """
    database_url = _get_database_url(ctx)
    if not database_url:
        return (
            "Error: DATABASE_URL is not configured. "
            "Set DATABASE_URL in your .env file to a valid Neon Postgres connection string."
        )

    try:
        pool = await _get_pool(database_url)

        async with pool.acquire() as conn:
            rows: List[asyncpg.Record] = await conn.fetch(_SEARCH_SQL, keyword)

        if not rows:
            logger.info(f"search_notes_no_results: keyword={keyword!r}")
            return f"No notes found matching '{keyword}'."

        logger.info(f"search_notes_success: keyword={keyword!r}, count={len(rows)}")

        parts = [f"Found {len(rows)} note(s) matching '{keyword}':\n"]
        for row in rows:
            parts.append(f"--- Note #{row['id']} ---")
            parts.append(f"Title: {row['title']}")
            # Truncate long content in the result preview
            preview = row["content"]
            if len(preview) > 300:
                preview = preview[:300] + "..."
            parts.append(f"Content: {preview}")
            if row["source"]:
                parts.append(f"Source: {row['source']}")
            if row["tags"]:
                parts.append(f"Tags: {', '.join(row['tags'])}")
            parts.append(f"Saved: {row['created_at'].isoformat()}")
            parts.append("")

        return "\n".join(parts).rstrip()

    except asyncpg.PostgresError as e:
        logger.error(f"search_notes_db_error: error={str(e)}")
        return f"Error: Database error while searching notes — {str(e)}"
    except Exception as e:
        logger.exception(f"search_notes_error: error={str(e)}")
        return f"Error: {str(e)}"
