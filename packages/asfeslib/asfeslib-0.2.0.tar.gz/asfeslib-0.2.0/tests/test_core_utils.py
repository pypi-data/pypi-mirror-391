import re
from asfeslib.core import utils


def test_now_str_format():
    ts = utils.now_str()
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ts)


def test_gen_token_length():
    token = utils.gen_token(32)
    assert isinstance(token, str)
    assert len(token) == 32


def test_hash_text_consistency():
    h1 = utils.hash_text("test")
    h2 = utils.hash_text("test")
    assert h1 == h2


def test_random_string_unique():
    s1 = utils.random_string(8)
    s2 = utils.random_string(8)
    assert s1 != s2


def test_pretty_json():
    obj = {"a": 1, "b": True}
    js = utils.pretty_json(obj)
    assert '"a": 1' in js
