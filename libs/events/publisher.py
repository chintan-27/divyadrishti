from __future__ import annotations

import json
from typing import Any

from redis import Redis


class EventPublisher:
    def __init__(self, redis: Redis[bytes]) -> None:
        self._redis = redis

    def publish(self, channel: str, data: dict[str, Any]) -> str:
        """Publish an event to a Redis Stream via XADD. Returns the message ID."""
        msg_id: bytes = self._redis.xadd(channel, {"data": json.dumps(data)})  # type: ignore[assignment]
        return msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
