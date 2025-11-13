"""Tests for CLI functionality."""

import subprocess


def run_calc(operation: str, num1: str, num2: str) -> str:
    """Run calc command and return output.

    Args:
        operation: Calculator operation (Add, Subtract, etc.)
        num1: First number
        num2: Second number

    Returns:
        Output from calc command
    """
    result = subprocess.run(
        ["python", "-m", "simple_calculator.cli", operation, num1, num2],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def test_add_command() -> None:
    """Test Add command."""
    output = run_calc("Add", "5", "3")
    assert "5.0 add 3.0 = 8.0" in output


def test_subtract_command() -> None:
    """Test Subtract command."""
    output = run_calc("Subtract", "10", "3")
    assert "10.0 subtract 3.0 = 7.0" in output


def test_multiply_command() -> None:
    """Test Multiply command."""
    output = run_calc("Multiply", "5", "4")
    assert "5.0 multiply 4.0 = 20.0" in output


def test_divide_command() -> None:
    """Test Divide command."""
    output = run_calc("Divide", "10", "2")
    assert "10.0 divide 2.0 = 5.0" in output


def test_divide_by_zero_error() -> None:
    """Test Divide by zero error."""
    result = subprocess.run(
        ["python", "-m", "simple_calculator.cli", "Divide", "10", "0"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Cannot divide by zero" in result.stderr


def test_invalid_operation_error() -> None:
    """Test invalid operation error."""
    result = subprocess.run(
        ["python", "-m", "simple_calculator.cli", "Power", "2", "3"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Unknown operation" in result.stderr


def test_missing_arguments_error() -> None:
    """Test missing arguments error."""
    result = subprocess.run(
        ["python", "-m", "simple_calculator.cli", "Add", "5"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Usage" in result.stderr


def test_invalid_number_error() -> None:
    """Test invalid number error."""
    result = subprocess.run(
        ["python", "-m", "simple_calculator.cli", "Add", "abc", "5"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Numbers must be valid" in result.stderr
