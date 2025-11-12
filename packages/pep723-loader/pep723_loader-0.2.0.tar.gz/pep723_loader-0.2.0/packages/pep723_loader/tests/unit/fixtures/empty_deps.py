#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Test script with PEP 723 metadata but empty dependencies list."""

import json
from pathlib import Path


def read_config(config_path: Path) -> dict[str, str]:
    """Read JSON configuration file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    return json.loads(config_path.read_text())


def main() -> None:
    """Load and print configuration."""
    config = read_config(Path("config.json"))
    print(f"Config: {config}")


if __name__ == "__main__":
    main()
