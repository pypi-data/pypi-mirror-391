# tests/test_format.py
from cobra_color import fmt_dict, fmt_list


def test_fmt_dict():
    d = {"a": 1, "b": [1, 2, 3], "c": {"d": 4, "e": 5}}
    result = fmt_dict(d, title="Sample Dict")
    assert isinstance(result, str)


def test_fmt_list():
    l = [1, 2, 3, {"a": 4, "b": [5, 6]}, [7, 8, 9], "text"]
    result = fmt_list(l)
    assert isinstance(result, str)
