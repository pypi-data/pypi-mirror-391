"""Command-line interface for the calculator."""

import sys

from simple_calculator.core import Calculator


def main() -> None:
    """Run the calculator CLI.

    Usage:
        calc Add 2 6
        calc Multiply 3 4
        calc Divide 20 5
    """
    if len(sys.argv) != 4:
        print("Usage: calc Operation num1 num2", file=sys.stderr)
        print("Example: calc Add 2 6", file=sys.stderr)
        print("Operations: Add, Subtract, Multiply, Divide", file=sys.stderr)
        sys.exit(1)

    operation = sys.argv[1]
    num1_str = sys.argv[2]
    num2_str = sys.argv[3]

    try:
        num1 = float(num1_str)
        num2 = float(num2_str)
    except ValueError:
        print(
            f"Error: Numbers must be valid numbers, got '{num1_str}' and '{num2_str}'",
            file=sys.stderr,
        )
        sys.exit(1)

    operation_lower = operation.lower()

    try:
        if operation_lower == "add":
            result = Calculator.add(num1, num2)
        elif operation_lower == "subtract":
            result = Calculator.subtract(num1, num2)
        elif operation_lower == "multiply":
            result = Calculator.multiply(num1, num2)
        elif operation_lower == "divide":
            result = Calculator.divide(num1, num2)
        else:
            print(f"Error: Unknown operation: {operation}", file=sys.stderr)
            print("Operations: Add, Subtract, Multiply, Divide", file=sys.stderr)
            sys.exit(1)

        print(f"{num1} {operation.lower()} {num2} = {result}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
