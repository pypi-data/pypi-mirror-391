"""Tests for calculator core functionality."""

import pytest

from simple_calculator.core import Calculator


class TestCalculatorBasicOperations:
    """Test basic arithmetic operations."""

    def test_add(self) -> None:
        """Test addition."""
        assert Calculator.add(5, 3) == 8
        assert Calculator.add(-5, 3) == -2
        assert Calculator.add(0, 0) == 0
        assert Calculator.add(1.5, 2.5) == 4.0

    def test_subtract(self) -> None:
        """Test subtraction."""
        assert Calculator.subtract(5, 3) == 2
        assert Calculator.subtract(3, 5) == -2
        assert Calculator.subtract(0, 0) == 0
        assert Calculator.subtract(5.5, 2.5) == 3.0

    def test_multiply(self) -> None:
        """Test multiplication."""
        assert Calculator.multiply(5, 3) == 15
        assert Calculator.multiply(-5, 3) == -15
        assert Calculator.multiply(0, 100) == 0
        assert Calculator.multiply(2.5, 4) == 10.0

    def test_divide(self) -> None:
        """Test division."""
        assert Calculator.divide(10, 2) == 5.0
        assert Calculator.divide(7, 2) == 3.5
        assert Calculator.divide(-10, 2) == -5.0
        assert Calculator.divide(0, 5) == 0.0

    def test_divide_by_zero(self) -> None:
        """Test division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            Calculator.divide(5, 0)
