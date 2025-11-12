#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "broken-package-syntax===invalid",
#   "missing-quote
# ]
# ///
"""Test script with malformed PEP 723 syntax."""


def broken_function() -> None:
    """This function won't work due to malformed PEP 723 metadata."""
    print("This should fail during dependency parsing")


if __name__ == "__main__":
    broken_function()
