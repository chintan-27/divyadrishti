from __future__ import annotations

import duckdb
from fastapi import APIRouter, Depends, HTTPException

from apps.api.db import get_db
from libs.schemas.api_responses import CommentResponse, StoryResponse

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/trending", response_model=list[StoryResponse])
def trending(limit: int = 30, conn: duckdb.DuckDBPyConnection = Depends(get_db)) -> list[StoryResponse]:
    rows = conn.execute(
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
def get_story(story_id: int, conn: duckdb.DuckDBPyConnection = Depends(get_db)) -> StoryResponse:
    row = conn.execute(
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
def get_comments(
    story_id: int, limit: int = 100, conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> list[CommentResponse]:
    rows = conn.execute(
        'SELECT id, "by", "text", "time", parent FROM hn_item '
        'WHERE parent = ? AND "type" = \'comment\' ORDER BY "time" ASC LIMIT ?',
        [story_id, limit],
    ).fetchall()
    return [
        CommentResponse(id=r[0], by=r[1], text=r[2], time=r[3], parent=r[4])
        for r in rows
    ]
