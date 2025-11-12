from unittest.mock import MagicMock
from .actor import Actor


def test_as_dict():
    a = Actor(name="alice", handle="a")

    result = a.as_json()

    assert result == '{"name": "alice", "handle": "a", "summary": null, "icon": null}'

    assert a.as_file(MagicMock())
