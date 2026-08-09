"""
CivicPulse — Lakebase (Postgres) client.

Thin psycopg connection-pool wrapper used by both the agent's write tools
(agent/tools.py) and the Databricks App pages. Deliberately raw SQL, no ORM —
the schema is small and fixed (sql/lakebase_ddl.sql) and the write paths need
to stay easy to reason about for the agent's tool-calling loop.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import date
from typing import Any, Optional

from config.settings import (
    LAKEBASE_DATABASE,
    LAKEBASE_HOST,
    LAKEBASE_PASSWORD,
    LAKEBASE_PORT,
    LAKEBASE_USER,
)

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        from psycopg_pool import ConnectionPool

        conninfo = (
            f"host={LAKEBASE_HOST} port={LAKEBASE_PORT} "
            f"dbname={LAKEBASE_DATABASE} user={LAKEBASE_USER} password={LAKEBASE_PASSWORD} "
            f"sslmode=require"
        )
        _pool = ConnectionPool(conninfo, min_size=1, max_size=5)
    return _pool


@contextmanager
def get_cursor():
    pool = _get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            yield cur
        conn.commit()


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

def get_user_profile(user_id: str) -> Optional[dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT user_id, email, state, city, topics, stake_statement "
            "FROM users WHERE user_id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = ["user_id", "email", "state", "city", "topics", "stake_statement"]
        return dict(zip(cols, row))


def create_user(email: str, state: str, city: str, topics: list[str], stake_statement: str) -> str:
    user_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, email, state, city, topics, stake_statement) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, email, state, city, topics, stake_statement),
        )
    return user_id


# ---------------------------------------------------------------------------
# tracked_issues
# ---------------------------------------------------------------------------

def track_issue(user_id: str, bill_id: str, source_type: str, status: str = "introduced",
                 next_hearing_date: Optional[date] = None) -> str:
    issue_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO tracked_issues (issue_id, user_id, bill_id, source_type, status, next_hearing_date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (issue_id, user_id, bill_id, source_type, status, next_hearing_date),
        )
    return issue_id


def list_tracked_issues(user_id: str) -> list[dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT issue_id, bill_id, source_type, status, next_hearing_date, tracked_at "
            "FROM tracked_issues WHERE user_id = %s ORDER BY next_hearing_date NULLS LAST",
            (user_id,),
        )
        cols = ["issue_id", "bill_id", "source_type", "status", "next_hearing_date", "tracked_at"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def update_issue_status(issue_id: str, new_status: str) -> None:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE tracked_issues SET status = %s, status_updated_at = now() WHERE issue_id = %s",
            (new_status, issue_id),
        )


# ---------------------------------------------------------------------------
# testimony_drafts
# ---------------------------------------------------------------------------

def save_testimony_draft(user_id: str, issue_id: str, draft_text: str,
                          tone: Optional[str] = None, cited_sections: Optional[list[str]] = None) -> str:
    draft_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO testimony_drafts (draft_id, user_id, issue_id, draft_text, tone, cited_sections) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (draft_id, user_id, issue_id, draft_text, tone, cited_sections or []),
        )
    return draft_id


def list_testimony_drafts(user_id: str) -> list[dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT draft_id, issue_id, draft_text, tone, cited_sections, created_at, submitted "
            "FROM testimony_drafts WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        )
        cols = ["draft_id", "issue_id", "draft_text", "tone", "cited_sections", "created_at", "submitted"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# notifications
# ---------------------------------------------------------------------------

def create_notification(user_id: str, message: str, issue_id: Optional[str] = None,
                         due_date: Optional[date] = None) -> str:
    notification_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO notifications (notification_id, user_id, issue_id, message, due_date) "
            "VALUES (%s, %s, %s, %s, %s)",
            (notification_id, user_id, issue_id, message, due_date),
        )
    return notification_id


def list_unread_notifications(user_id: str) -> list[dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT notification_id, issue_id, message, due_date, created_at "
            "FROM notifications WHERE user_id = %s AND read = false ORDER BY due_date NULLS LAST",
            (user_id,),
        )
        cols = ["notification_id", "issue_id", "message", "due_date", "created_at"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
