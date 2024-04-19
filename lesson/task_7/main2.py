import pytest

@pytest.mark.parametrize("a, b, result", [
    (1, 2, 3),
    (2, 3, 5),
    (3, 4, 7)
])
def test_addition(a, b, result):
    assert a + b == result

@pytest.mark.parametrize('test_input, expected_output', [
    ('3+5', 8),
    ('2+4', 6),
    ('6*9', 54)
])
def test_eval(test_input, expected_output):
    assert eval(test_input) == expected_output


@pytest.mark.parametrize("test_input, expected_output", [("1+2", 3),("2+2", 4),("22+22", 44)])
def test_eval1(test_input, expected_output):
    assert eval(test_input) == expected_output


