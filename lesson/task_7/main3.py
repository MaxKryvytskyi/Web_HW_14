import pytest


@pytest.fixture
def add_fixture():
    return lambda x, y: x + y


@pytest.mark.parametrize('a, b, expected', [
    (1, 2, 3),
    (3, 4, 7),
    (7, 5, 12),
    (-2, 35, 33),
    (-21, 45, 24),
    (42, 5, 47),
    (1000, 5, 1005),
    (100, 5, 105),
    (10, 5, 15),
    (4, 5, 9),
    (111, 111, 222),
    ("1", "2", "12"),
])
def test_addition(add_fixture, a, b, expected):
    assert add_fixture(a, b) == expected



