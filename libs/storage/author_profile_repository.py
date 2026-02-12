from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.author_profile import AuthorProfile

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO author_profile (
    author_hash, first_seen_time, last_seen_time,
    comment_count, story_count, spam_score, bot_likelihood, influence_cap_state
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (author_hash) DO UPDATE SET
    first_seen_time = LEAST(author_profile.first_seen_time, excluded.first_seen_time),
    last_seen_time = GREATEST(author_profile.last_seen_time, excluded.last_seen_time),
    comment_count = excluded.comment_count,
    story_count = excluded.story_count,
    spam_score = excluded.spam_score,
    bot_likelihood = excluded.bot_likelihood,
    influence_cap_state = excluded.influence_cap_state
"""

_COLUMNS = (
    "author_hash, first_seen_time, last_seen_time, "
    "comment_count, story_count, spam_score, bot_likelihood, influence_cap_state"
)


def _row_to_profile(row: tuple[object, ...]) -> AuthorProfile:
    return AuthorProfile(
        author_hash=row[0],  # type: ignore[arg-type]
        first_seen_time=row[1],  # type: ignore[arg-type]
        last_seen_time=row[2],  # type: ignore[arg-type]
        comment_count=row[3],  # type: ignore[arg-type]
        story_count=row[4],  # type: ignore[arg-type]
        spam_score=row[5],  # type: ignore[arg-type]
        bot_likelihood=row[6],  # type: ignore[arg-type]
        influence_cap_state=row[7],  # type: ignore[arg-type]
    )


class AuthorProfileRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, profile: AuthorProfile) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [
                profile.author_hash, profile.first_seen_time, profile.last_seen_time,
                profile.comment_count, profile.story_count, profile.spam_score,
                profile.bot_likelihood, profile.influence_cap_state,
            ],
        )

    def get_by_hash(self, author_hash: str) -> AuthorProfile | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM author_profile WHERE author_hash = ?",
            [author_hash],
        ).fetchone()
        return _row_to_profile(row) if row else None

    def get_all(self) -> list[AuthorProfile]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM author_profile"
        ).fetchall()
        return [_row_to_profile(r) for r in rows]
