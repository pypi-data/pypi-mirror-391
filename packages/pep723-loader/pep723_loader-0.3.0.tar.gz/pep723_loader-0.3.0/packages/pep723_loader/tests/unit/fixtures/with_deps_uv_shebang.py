#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31.0",
#   "pydantic>=2.0.0",
# ]
# ///
"""Test script with PEP 723 dependencies and uv shebang."""

import requests
from pydantic import BaseModel


class User(BaseModel):
    """Example user model."""

    name: str
    email: str


def main() -> None:
    """Fetch and validate user data."""
    response = requests.get("https://api.example.com/users/1", timeout=10)
    user = User(**response.json())
    print(f"User: {user.name}")


if __name__ == "__main__":
    main()
