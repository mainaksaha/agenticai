# arcade_arithmetic/tools/operations.py
from typing import Annotated
 
from arcade_tdk import tool
 
 
@tool
def add(
    a: Annotated[int, "The first number"],
    b: Annotated[int, "The second number"]
) -> Annotated[int, "The sum of the two numbers"]:
    """
    Add two numbers together
 
    Examples:
        add(3, 4) -> 7
        add(-1, 5) -> 4
    """
    return a + b
 
@tool
def subtract(
    a: Annotated[int, "The first number"],
    b: Annotated[int, "The second number"]
) -> Annotated[int, "The difference of the two numbers"]:
    """
    Subtract the second number from the first
 
    Examples:
        subtract(10, 4) -> 6
        subtract(5, 7) -> -2
    """
    return a - b
 
@tool
def multiply(
    a: Annotated[int, "The first number"],
    b: Annotated[int, "The second number"]
) -> Annotated[int, "The product of the two numbers"]:
    """
    Multiply two numbers together
 
    Examples:
        multiply(3, 4) -> 12
        multiply(-2, 5) -> -10
    """
    return a * b