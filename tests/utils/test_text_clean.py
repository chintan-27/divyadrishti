from libs.utils.text_clean import clean_hn_html, content_hash


def test_strip_tags():
    assert clean_hn_html("<b>bold</b> text") == "bold text"


def test_decode_entities():
    assert clean_hn_html("foo &amp; bar &lt;baz&gt;") == "foo & bar <baz>"


def test_collapse_whitespace():
    assert clean_hn_html("hello   world") == "hello world"


def test_code_block_preserved():
    html = "<pre><code>x = 1\ny = 2</code></pre>"
    result = clean_hn_html(html)
    assert "x = 1" in result
    assert "y = 2" in result


def test_paragraph_to_newline():
    result = clean_hn_html("first<p>second<p>third")
    assert "first" in result
    assert "second" in result
    assert "third" in result
    lines = result.split("\n")
    assert len(lines) == 3


def test_empty_string():
    assert clean_hn_html("") == ""


def test_content_hash():
    h = content_hash("hello")
    assert len(h) == 64
    assert h == content_hash("hello")
    assert h != content_hash("world")
