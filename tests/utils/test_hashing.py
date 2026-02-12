import re

from libs.utils.hashing import hash_author


def test_hash_is_64_char_hex():
    result = hash_author("pg", "secret")
    assert re.fullmatch(r"[0-9a-f]{64}", result)


def test_hash_is_consistent():
    assert hash_author("dang", "salt1") == hash_author("dang", "salt1")


def test_different_salt_produces_different_hash():
    assert hash_author("dang", "salt1") != hash_author("dang", "salt2")


def test_different_username_produces_different_hash():
    assert hash_author("alice", "salt") != hash_author("bob", "salt")
