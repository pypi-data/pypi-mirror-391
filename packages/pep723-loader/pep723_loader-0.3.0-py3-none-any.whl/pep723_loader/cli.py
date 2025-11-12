"""PEP 723 wrapper for linting Python scripts

This script ensures that 'uv' is available locally, and uses it to install the dependencies for the script into the current environment.

This is useful for using mypy, ruff, pyright, basedpright, pylint, flake8, bandit, etc. without having to have a vnv with the script dependencies or tools installed..

Architecture:
    - Follows SOLID principles with abstract interfaces
    - Dependency injection for flexibility and testability
    - Generic and project-agnostic design
    - Parses all build parameters from CMake arguments (no hardcoded fields)

SOLID Principles Applied:
    S: Single Responsibility - Each class has one clear purpose
    O: Open/Closed - Extensible via interfaces without modification
    L: Liskov Substitution - Implementations are interchangeable
    I: Interface Segregation - Specific interfaces for each concern
    D: Dependency Inversion - Depends on abstractions, not concretions
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from .pep723_checker import Pep723Checker

app = typer.Typer(
    name="pep723-loader",
    help="Wrap linters/tools to auto-install PEP 723 dependencies before execution",
    add_completion=False,
)


@app.command(context_settings={"allow_interspersed_args": False})
def run(
    command: Annotated[str, typer.Argument(help="Command to execute (e.g., mypy, ruff, basedpyright)")],
    args: Annotated[list[str] | None, typer.Argument(help="Arguments to pass to the command")] = None,
) -> None:
    """Execute a command after installing PEP 723 dependencies from Python files.

    This wrapper:
    1. Extracts Python files from arguments
    2. Uses Pep723Checker to discover PEP 723 dependencies
    3. Installs dependencies via 'uv pip install -r -'
    4. Executes the wrapped command with original arguments
    5. Propagates the command's exit code

    Example:
        pep723-loader mypy --strict packages/pep723-linter/
        pep723-loader basedpyright file.py

    Args:
        command: The tool/linter to execute
        args: All arguments to pass to the tool (files, directories, options)
    """
    # Handle None default for args
    if args is None:
        args = []

    # Step 1: Extract Python files from args
    # Pep723Checker handles both direct .py files and directories
    python_paths: list[str] = []
    for arg in args:
        arg_path = Path(arg)
        if arg_path.exists() and (arg_path.is_file() or arg_path.is_dir()):
            python_paths.append(arg)

    # Step 2: Get PEP 723 dependencies
    if python_paths:
        checker = Pep723Checker(python_paths)
        requirements = checker.requirements_set

        # Step 3: Install dependencies if any found
        if requirements:
            # Join all requirements.txt outputs with newlines
            requirements_text = "\n".join(requirements)

            # Get full uv path to satisfy S607
            uv_path = checker.resolve_uv()

            # Pipe to uv pip install -r -
            install_result = subprocess.run(
                [uv_path, "pip", "install", "--quiet", "-r", "-"], input=requirements_text, text=True, check=False
            )

            # If installation fails, exit with install error code
            if install_result.returncode != 0:
                sys.exit(install_result.returncode)

    # Step 4: Execute wrapped command with all original args
    wrapped_result = subprocess.run([command, *args], check=False)

    # Step 5: Exit with command's exit code
    sys.exit(wrapped_result.returncode)


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
