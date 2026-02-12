import hashlib


def hash_author(username: str, salt: str) -> str:
    """Return a SHA-256 hex digest of the salted username."""
    return hashlib.sha256(f"{salt}:{username}".encode()).hexdigest()
