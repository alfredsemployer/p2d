import pytest

from p2d_reasoning_lab.jsonutil import parse_json_object


def test_parse_plain_object():
    assert parse_json_object('{"x": 1}') == {"x": 1}


def test_parse_fenced_object():
    assert parse_json_object('```json\n{"x": 1}\n```') == {"x": 1}


def test_parse_embedded_object():
    assert parse_json_object('answer: {"x": 1} done') == {"x": 1}


def test_repair_truncated_model_json():
    assert parse_json_object('{"x": 1, "items": ["a", "b"]') == {
        "x": 1,
        "items": ["a", "b"],
    }


def test_reject_array():
    with pytest.raises(ValueError):
        parse_json_object("[1, 2]")
