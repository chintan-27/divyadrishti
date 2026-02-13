from libs.utils.moderation import check_offensive, redact_pii


def test_redact_email():
    assert redact_pii("contact me at foo@bar.com") == "contact me at [EMAIL]"


def test_redact_phone():
    assert redact_pii("call 555-123-4567") == "call [PHONE]"


def test_redact_multiple():
    text = "email: a@b.com phone: (555) 123-4567"
    result = redact_pii(text)
    assert "[EMAIL]" in result
    assert "[PHONE]" in result


def test_no_pii():
    text = "just a normal comment"
    assert redact_pii(text) == text


def test_offensive_detected():
    is_off, reason = check_offensive("you should kys lol")
    assert is_off
    assert reason is not None


def test_clean_text():
    is_off, reason = check_offensive("this is a nice comment")
    assert not is_off
    assert reason is None
