import pytest

from gateway.platforms.napcat import _extract_text, _has_bot_mention, _strip_bot_mention


def test_group_message_requires_mention_of_self_id():
    segments = [{"type": "text", "data": {"text": "你好"}}]
    assert _has_bot_mention(segments, "123456") is False


def test_group_message_detects_and_removes_bot_mention():
    segments = [
        {"type": "at", "data": {"qq": "123456"}},
        {"type": "text", "data": {"text": " 你好"}},
    ]
    assert _has_bot_mention(segments, "123456") is True
    assert _extract_text(_strip_bot_mention(segments, "123456")) == "你好"
