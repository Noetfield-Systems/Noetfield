"""JSONB coercion for asyncpg row values."""

from noetfield_types import coerce_jsonb_mapping


def test_coerce_none_and_dict() -> None:
    assert coerce_jsonb_mapping(None) == {}
    assert coerce_jsonb_mapping({"a": 1}) == {"a": 1}


def test_coerce_json_string() -> None:
    assert coerce_jsonb_mapping("{}") == {}
    assert coerce_jsonb_mapping('{"phase": "smoke"}') == {"phase": "smoke"}


def test_coerce_invalid_string_not_dict() -> None:
    assert coerce_jsonb_mapping("[]") == {}
