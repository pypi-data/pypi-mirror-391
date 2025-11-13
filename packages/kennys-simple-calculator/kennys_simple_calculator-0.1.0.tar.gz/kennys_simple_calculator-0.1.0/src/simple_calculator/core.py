""" Core calculator functionality. """
from typing import Union


class Calculator:
    """A caclulator class that performs basic arithmetic operations."""

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers.
        Args:
            a (Union[int, float]): The first number.
            b (Union[int, float]): The second number.
        Returns:
            Union[int, float]: The sum of the two numbers.
        """
        return a + b

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract two numbers.

        Args:
            a: First number
            b: Second number (will be subtracted from a)

        Returns:
            Difference of a and b
        """
        return a - b

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b
        """
        return a * b

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> float:
        """Divide two numbers.

        Args:
            a: Dividend (numerator)
            b: Divisor (denominator)

        Returns:
            Quotient of a divided by b

        Raises:
            ValueError: If b (divisor) is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
