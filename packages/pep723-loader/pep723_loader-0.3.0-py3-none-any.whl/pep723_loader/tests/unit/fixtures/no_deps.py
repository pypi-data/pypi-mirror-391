#!/usr/bin/env python3
"""Test script with no PEP 723 metadata - uses only stdlib."""


def calculate_sum(numbers: list[int]) -> int:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of integers to sum

    Returns:
        Sum of all numbers
    """
    return sum(numbers)


def main() -> None:
    """Run a simple calculation."""
    result = calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")


if __name__ == "__main__":
    main()
