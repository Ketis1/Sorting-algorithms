from backend.security import (
    SECURITY_HEADERS,
    sanitize_text,
    sanitize_timeout_ms,
    sanitize_viz_tier,
)


def test_sanitize_text_strips_and_truncates():
    assert sanitize_text("  hello  ") == "hello"
    assert sanitize_text("a" * 600, max_length=10) == "a" * 10
    assert sanitize_text(None) is None
    assert sanitize_text({"x": 1}) == "{'x': 1}"


def test_sanitize_text_removes_null_bytes():
    assert sanitize_text("hello\x00world") == "helloworld"


def test_sanitize_viz_tier_rejects_unknown_values():
    assert sanitize_viz_tier("full") == "full"
    assert sanitize_viz_tier("<script>alert(1)</script>", default="partial") == "partial"
    assert sanitize_viz_tier(None, default="result_only") == "result_only"


def test_sanitize_timeout_ms_bounds():
    assert sanitize_timeout_ms(3000) == 3000
    assert sanitize_timeout_ms(50) is None
    assert sanitize_timeout_ms("not-a-number") is None


def test_security_headers_present():
    assert "Content-Security-Policy" in SECURITY_HEADERS
    assert SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"
