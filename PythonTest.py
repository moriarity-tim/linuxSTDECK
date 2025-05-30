import pytest
from homegrown import multiply

def test_multiply_positive_numbers():
    assert multiply(2, 3) == 6

def test_multiply_negative_numbers():
    assert multiply(-1, -2) == 2

def test_multiply_NegativeAndPositive_number():
    assert multiply(-1, 4) == -4

def test_multiply_zero():
    assert multiply(0, 5) == 0