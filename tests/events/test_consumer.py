import fakeredis

from libs.events.consumer import EventConsumer
from libs.events.publisher import EventPublisher


def test_consumer_reads_published_events():
    r = fakeredis.FakeRedis()
    pub = EventPublisher(r)
    pub.publish("test.channel", {"item": 1})
    pub.publish("test.channel", {"item": 2})

    consumer = EventConsumer(r, "test.channel", "grp", "worker-1")
    events = consumer.read(count=10)
    assert len(events) == 2
    assert events[0]["item"] == 1
    assert events[1]["item"] == 2


def test_consumer_acks_messages():
    r = fakeredis.FakeRedis()
    pub = EventPublisher(r)
    pub.publish("test.channel", {"item": 1})

    consumer = EventConsumer(r, "test.channel", "grp", "worker-1")
    events = consumer.read(count=10)
    assert len(events) == 1

    # second read returns nothing (already acked)
    events = consumer.read(count=10)
    assert len(events) == 0


def test_consumer_empty_stream():
    r = fakeredis.FakeRedis()
    consumer = EventConsumer(r, "test.channel", "grp", "worker-1")
    events = consumer.read(count=10)
    assert events == []
