import pytest
from .adjust_objects import include_cc


@pytest.mark.parametrize(
    "obj, expected_cc",
    [
        ({}, []),
        ({"cc": []}, []),
        ({"cc": "http://value.test"}, "http://value.test"),
        ({"cc": None}, None),
    ],
)
def test_adds_cc(obj, expected_cc):
    include_cc(obj)

    assert obj["cc"] == expected_cc
