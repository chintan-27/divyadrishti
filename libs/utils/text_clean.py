from __future__ import annotations

import hashlib
import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_CODE_BLOCK_RE = re.compile(r"<pre><code>(.*?)</code></pre>", re.DOTALL)


def clean_hn_html(text: str) -> str:
    """Strip HTML tags, decode entities, collapse whitespace.

    Preserves code block contents as plain text separated by newlines.
    """
    if not text:
        return ""

    # preserve code blocks as plain text
    def _replace_code(m: re.Match[str]) -> str:
        code = html.unescape(m.group(1))
        return "\n" + code.strip() + "\n"

    result = _CODE_BLOCK_RE.sub(_replace_code, text)
    # convert <p> to newline
    result = re.sub(r"<p>", "\n", result, flags=re.IGNORECASE)
    # strip remaining tags
    result = _TAG_RE.sub("", result)
    # decode entities
    result = html.unescape(result)
    # collapse whitespace (but preserve single newlines)
    lines = result.split("\n")
    lines = [_WHITESPACE_RE.sub(" ", line).strip() for line in lines]
    result = "\n".join(line for line in lines if line)
    return result.strip()


def content_hash(text: str) -> str:
    """SHA-256 hash for dedup."""
    return hashlib.sha256(text.encode()).hexdigest()
