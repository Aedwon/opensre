"""Small text/value helpers (truncate, coerce, URL checks, Markdown)."""

from platform.text.coercion import safe_int
from platform.text.markdown import tighten_markdown_emphasis
from platform.text.truncation import truncate
from platform.text.url_validation import is_loopback_host, validate_https_or_loopback_http_url

__all__ = [
    "is_loopback_host",
    "safe_int",
    "tighten_markdown_emphasis",
    "truncate",
    "validate_https_or_loopback_http_url",
]
