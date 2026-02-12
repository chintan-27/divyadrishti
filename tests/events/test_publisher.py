import json

import fakeredis

from libs.events.channels import HN_DISCOVERY
from libs.events.publisher import EventPublisher


def test_publish_adds_to_stream():
    r = fakeredis.FakeRedis()
    pub = EventPublisher(r)
    msg_id = pub.publish(HN_DISCOVERY, {"story_id": 42})
    assert msg_id  # non-empty string
    messages = r.xrange(HN_DISCOVERY)
    assert len(messages) == 1
    data = json.loads(messages[0][1][b"data"])
    assert data["story_id"] == 42


def test_publish_returns_unique_ids():
    r = fakeredis.FakeRedis()
    pub = EventPublisher(r)
    id1 = pub.publish(HN_DISCOVERY, {"a": 1})
    id2 = pub.publish(HN_DISCOVERY, {"a": 2})
    assert id1 != id2
