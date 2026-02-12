from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException

from libs.schemas.api_responses import CommentResponse, StoryResponse

if TYPE_CHECKING:
    import duckdb

router = APIRouter(prefix="/stories", tags=["stories"])

_db_conn: duckdb.DuckDBPyConnection | None = None


def set_db(conn: duckdb.DuckDBPyConnection) -> None:
    global _db_conn  # noqa: PLW0603
    _db_conn = conn


def _conn() -> duckdb.DuckDBPyConnection:
    if _db_conn is None:
        raise RuntimeError("Database not initialized")
    return _db_conn


@router.get("/trending", response_model=list[StoryResponse])
def trending(limit: int = 30) -> list[StoryResponse]:
    rows = _conn().execute(
        'SELECT id, title, url, score, "by", "time", descendants, "type" '
        'FROM hn_item WHERE "type" = \'story\' ORDER BY score DESC NULLS LAST LIMIT ?',
        [limit],
    ).fetchall()
    return [
        StoryResponse(
            id=r[0], title=r[1], url=r[2], score=r[3],
            by=r[4], time=r[5], descendants=r[6], type=r[7],
        )
        for r in rows
    ]


@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: int) -> StoryResponse:
    row = _conn().execute(
        'SELECT id, title, url, score, "by", "time", descendants, "type" '
        "FROM hn_item WHERE id = ?",
        [story_id],
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryResponse(
        id=row[0], title=row[1], url=row[2], score=row[3],
        by=row[4], time=row[5], descendants=row[6], type=row[7],
    )


@router.get("/{story_id}/comments", response_model=list[CommentResponse])
def get_comments(story_id: int, limit: int = 100) -> list[CommentResponse]:
    rows = _conn().execute(
        'SELECT id, "by", "text", "time", parent FROM hn_item '
        'WHERE parent = ? AND "type" = \'comment\' ORDER BY "time" ASC LIMIT ?',
        [story_id, limit],
    ).fetchall()
    return [
        CommentResponse(id=r[0], by=r[1], text=r[2], time=r[3], parent=r[4])
        for r in rows
    ]
