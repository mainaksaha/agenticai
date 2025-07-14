# tests/test_operations.py
import pytest
 
from arcade_arithmetic.tools.operations import add, multiply, subtract
 
 
def test_add():
    assert add(3, 4) == 7
    assert add(-1, 5) == 4
    assert add(0, 0) == 0
 
def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(5, 7) == -2
    assert subtract(0, 0) == 0
 
def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 5) == 0