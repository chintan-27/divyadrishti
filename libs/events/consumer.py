from __future__ import annotations

import json
from typing import Any

from redis import Redis


class EventConsumer:
    def __init__(
        self,
        redis: Redis[bytes],
        channel: str,
        group: str,
        name: str,
    ) -> None:
        self._redis = redis
        self._channel = channel
        self._group = group
        self._name = name
        self._ensure_group()

    def _ensure_group(self) -> None:
        try:
            self._redis.xgroup_create(self._channel, self._group, id="0", mkstream=True)
        except Exception:  # noqa: BLE001
            pass  # group already exists

    def read(self, count: int = 10, block_ms: int = 0) -> list[dict[str, Any]]:
        """Read pending messages from the consumer group."""
        raw = self._redis.xreadgroup(
            self._group,
            self._name,
            {self._channel: ">"},
            count=count,
            block=block_ms if block_ms > 0 else None,
        )
        if not raw:
            return []

        events: list[dict[str, Any]] = []
        for _stream, messages in raw:
            for msg_id, fields in messages:
                mid = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                data_raw = fields.get(b"data", b"{}")
                data_str = data_raw.decode() if isinstance(data_raw, bytes) else str(data_raw)
                event: dict[str, Any] = {"id": mid, **json.loads(data_str)}
                events.append(event)
                self._redis.xack(self._channel, self._group, msg_id)
        return events
