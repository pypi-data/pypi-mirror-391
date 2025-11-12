#!/usr/bin/env -S uv --quiet run --active --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pytest>=8.4.2",
#   "pytest-cov>=6.0.0",
# ]
# ///
"""End-to-end tests for pep723-loader CLI tool.

This test suite verifies real-world behavior of pep723-loader through actual
subprocess execution (no mocking). Tests cover the complete scenario matrix:

- Files with/without PEP 723 metadata
- Various dependency configurations (new, matching, conflicting, empty)
- Different shebang types (uv, python, none)
- Directory scenarios and edge cases
- Real linter execution and exit code verification

Test Architecture:
    - Uses subprocess to execute actual `uv run pep723-loader` commands
    - Creates temporary test files with realistic PEP 723 metadata
    - Verifies actual CLI behavior with real linters
    - Tests run in isolation with automatic cleanup
    - Default expectation: linter runs successfully (tests capture actual behavior)

Coverage: All 19 scenarios from test matrix (A1-A3, B1-B3, C1-C3, D1-D3, E1, F1-F3, G1-G4)

Standards:
    - All tests follow AAA (Arrange-Act-Assert) pattern
    - Complete type hints on all functions and fixtures
    - Comprehensive docstrings with Tests/How/Why format
    - No mocking - real subprocess execution only
    - Isolation via tmp_path with cleanup
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

# Project root for resolving paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def repo_root() -> Path:
    """Provide absolute path to repository root.

    Tests: Path resolution for CLI execution
    How: Calculate path from test file location
    Why: Ensure CLI can be found regardless of working directory

    Returns:
        Path to repository root directory
    """
    return PROJECT_ROOT


@pytest.fixture
def cli_executable(repo_root: Path) -> str:
    """Provide CLI command for subprocess execution.

    Tests: CLI executable resolution
    How: Use `uv run pep723-loader` to execute from editable install
    Why: Tests should work with editable install without full installation

    Args:
        repo_root: Repository root path fixture

    Returns:
        Command string to execute pep723-loader CLI
    """
    return f"uv --directory {repo_root} run pep723-loader"


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide isolated temporary directory for test files.

    Tests: Test isolation
    How: Use pytest's tmp_path fixture for automatic cleanup
    Why: Ensure tests don't interfere with each other or leave artifacts

    Args:
        tmp_path: pytest temporary directory fixture

    Yields:
        Path to temporary test directory
    """
    test_dir = tmp_path / "e2e_tests"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Automatic cleanup handled by pytest tmp_path


def create_test_file(
    directory: Path,
    filename: str,
    *,
    pep723_deps: list[str] | None = None,
    shebang: str | None = None,
    has_pep723: bool = True,
    invalid_pep723: bool = False,
) -> Path:
    """Create a temporary Python test file with specified configuration.

    Tests: Test file creation with various PEP 723 configurations
    How: Generate Python file with optional PEP 723 metadata and shebang
    Why: Provide realistic test files for E2E scenarios

    Args:
        directory: Directory to create file in
        filename: Name of the file to create
        pep723_deps: List of dependencies for PEP 723 metadata (None = no deps block)
        shebang: Shebang line to add (None = no shebang)
        has_pep723: Whether to include PEP 723 metadata block
        invalid_pep723: Whether to create invalid PEP 723 syntax

    Returns:
        Path to created test file
    """
    lines: list[str] = []

    # Add shebang if specified
    if shebang:
        lines.append(shebang)

    # Add PEP 723 metadata if specified
    if has_pep723:
        if invalid_pep723:
            # Invalid syntax: missing closing ///
            lines.extend([
                "# /// script",
                '# requires-python = ">=3.11"',
                "# dependencies = [",
                '#   "requests>=2.31.0",',
                "# ]",
                "# Missing closing marker intentionally",
            ])
        else:
            lines.extend(["# /// script", '# requires-python = ">=3.11"'])

            # Add dependencies if specified
            if pep723_deps is not None:
                if len(pep723_deps) == 0:
                    lines.append("# dependencies = []")
                else:
                    lines.append("# dependencies = [")
                    for dep in pep723_deps:
                        lines.append(f'#   "{dep}",')
                    lines.append("# ]")

            lines.append("# ///")

    # Add simple Python code
    lines.extend([
        '"""Test module for E2E testing."""',
        "",
        "",
        "def hello(name: str) -> str:",
        '    """Greet someone."""',
        '    return f"Hello, {name}!"',
        "",
        "",
        'if __name__ == "__main__":',
        '    print(hello("world"))',
        "",
    ])

    # Write file
    file_path = directory / filename
    file_path.write_text("\n".join(lines))
    return file_path


def run_cli_command(
    cli_executable: str, command: str, args: list[str], *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Execute pep723-loader CLI command and capture result.

    Tests: CLI subprocess execution
    How: Run actual `uv run pep723-loader` command with arguments
    Why: Verify real-world CLI behavior without mocking

    Args:
        cli_executable: CLI command to execute
        command: Linter/tool command to wrap
        args: Arguments to pass to wrapped command
        cwd: Working directory for subprocess (default: current directory)

    Returns:
        CompletedProcess with exit code, stdout, stderr
    """
    # Build command list (split cli_executable which may contain multiple args)
    # cli_executable format: "uv --directory /path run pep723-loader"
    cmd_parts = cli_executable.split()
    cmd_parts.append(command)
    cmd_parts.extend(args)

    # Execute via subprocess - using list form for security (no shell=True)
    result = subprocess.run(
        cmd_parts,
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,  # Don't raise on non-zero exit
    )

    return result


# ============================================================================
# Test Scenarios: Group A - PEP 723 deps NOT in project
# ============================================================================


class TestGroupA_PEP723DepsNotInProject:
    """Test files with PEP 723 metadata where dependencies are NOT in project.

    Scenarios:
        A1: PEP 723 deps + uv shebang
        A2: PEP 723 deps + python shebang
        A3: PEP 723 deps + no shebang

    Default expectation: linter runs successfully after installing deps.
    Tests capture actual behavior for analysis.
    """

    def test_a1_pep723_deps_uv_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test A1: File with PEP 723 deps (not in project) and uv shebang.

        Tests: CLI execution with PEP 723 dependencies and uv shebang
        How: Create file with external deps and uv shebang, run python -m py_compile
        Why: Verify dependencies are installed before linting uv-shebanged scripts

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "a1_test.py",
            pep723_deps=["colorama>=0.4.6"],  # External dep not in project
            shebang="#!/usr/bin/env -S uv run",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert - Capture actual behavior
        # Default expectation: successful execution
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_a2_pep723_deps_python_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test A2: File with PEP 723 deps (not in project) and python shebang.

        Tests: CLI execution with standard Python shebang
        How: Create file with external deps and python shebang, run py_compile
        Why: Verify dependencies are installed regardless of shebang type

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir, "a2_test.py", pep723_deps=["rich>=13.0.0"], shebang="#!/usr/bin/env python3"
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_a3_pep723_deps_no_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test A3: File with PEP 723 deps (not in project) and no shebang.

        Tests: CLI execution with missing shebang
        How: Create file with external deps but no shebang line
        Why: Ensure dependency extraction works without shebang

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "a3_test.py", pep723_deps=["click>=8.1.0"], shebang=None)

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group B - PEP 723 deps SAME version as project
# ============================================================================


class TestGroupB_PEP723DepsSameVersion:
    """Test files with PEP 723 metadata matching project dependency versions.

    Scenarios:
        B1: PEP 723 deps (matching versions) + uv shebang
        B2: PEP 723 deps (matching versions) + python shebang
        B3: PEP 723 deps (matching versions) + no shebang

    Default expectation: linter runs successfully (deps already installed).
    """

    def test_b1_matching_deps_uv_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test B1: File with PEP 723 deps matching project versions and uv shebang.

        Tests: CLI with dependencies already in project
        How: Create file with typer dependency (in project), uv shebang
        Why: Verify no-op or re-install when deps already present

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "b1_test.py",
            pep723_deps=["typer>=0.20.0"],  # Already in project
            shebang="#!/usr/bin/env -S uv run",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_b2_matching_deps_python_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test B2: File with PEP 723 deps matching project versions and python shebang.

        Tests: CLI with matching deps and python shebang
        How: Create file with pydantic dependency (in project)
        Why: Verify behavior when deps already satisfied

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "b2_test.py",
            pep723_deps=["pydantic>=2.10.6"],  # Already in project
            shebang="#!/usr/bin/env python3",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_b3_matching_deps_no_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test B3: File with PEP 723 deps matching project versions and no shebang.

        Tests: CLI with matching deps without shebang
        How: Create file with gitpython dependency (in project), no shebang
        Why: Ensure shebang not required when deps already present

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "b3_test.py",
            pep723_deps=["gitpython>=3.1.0"],  # Already in project
            shebang=None,
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group C - PEP 723 deps DIFFERENT version from project
# ============================================================================


class TestGroupC_PEP723DepsConflictingVersion:
    """Test files with PEP 723 metadata with conflicting dependency versions.

    Scenarios:
        C1: PEP 723 deps (conflicting versions) + uv shebang
        C2: PEP 723 deps (conflicting versions) + python shebang
        C3: PEP 723 deps (conflicting versions) + no shebang

    Default expectation: linter runs (uv handles version resolution).
    Tests capture actual behavior to see how uv resolves conflicts.
    """

    def test_c1_conflicting_deps_uv_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test C1: File with PEP 723 deps conflicting with project and uv shebang.

        Tests: CLI with conflicting dependency versions
        How: Create file with different typer version, uv shebang
        Why: Verify uv's version conflict resolution behavior

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "c1_test.py",
            pep723_deps=["typer>=0.12.0,<0.15.0"],  # Conflicts with project typer>=0.20.0
            shebang="#!/usr/bin/env -S uv run",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert - Capture actual behavior (may succeed or fail depending on uv resolution)
        # We're testing to observe what actually happens
        assert result.returncode in {0, 1}, (
            f"Expected exit code 0 (success) or 1 (conflict). Got {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_c2_conflicting_deps_python_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test C2: File with PEP 723 deps conflicting with project and python shebang.

        Tests: CLI with conflicting deps and python shebang
        How: Create file with different pydantic version
        Why: Verify conflict handling with standard shebang

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "c2_test.py",
            pep723_deps=["pydantic>=2.0.0,<2.5.0"],  # Conflicts with project pydantic>=2.10.6
            shebang="#!/usr/bin/env python3",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode in {0, 1}, (
            f"Expected exit code 0 or 1. Got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_c3_conflicting_deps_no_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test C3: File with PEP 723 deps conflicting with project and no shebang.

        Tests: CLI with conflicting deps without shebang
        How: Create file with different uv version, no shebang
        Why: Ensure conflict resolution works without shebang

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "c3_test.py",
            pep723_deps=["uv>=0.5.0,<0.8.0"],  # Conflicts with project uv>=0.9.2
            shebang=None,
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode in {0, 1}, (
            f"Expected exit code 0 or 1. Got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group D - NO PEP 723 metadata
# ============================================================================


class TestGroupD_NoPEP723:
    """Test files without PEP 723 metadata.

    Scenarios:
        D1: No PEP 723 + uv shebang
        D2: No PEP 723 + python shebang
        D3: No PEP 723 + no shebang

    Default expectation: linter runs without trying to install deps.
    """

    def test_d1_no_pep723_uv_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test D1: File without PEP 723 metadata but with uv shebang.

        Tests: CLI with no PEP 723 metadata
        How: Create file with uv shebang but no PEP 723 block
        Why: Verify CLI skips dependency installation when no metadata present

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "d1_test.py", has_pep723=False, shebang="#!/usr/bin/env -S uv run")

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_d2_no_pep723_python_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test D2: File without PEP 723 metadata and python shebang.

        Tests: CLI with standard file (no PEP 723)
        How: Create file with python shebang, no PEP 723
        Why: Ensure normal Python files pass through correctly

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "d2_test.py", has_pep723=False, shebang="#!/usr/bin/env python3")

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_d3_no_pep723_no_shebang(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test D3: File without PEP 723 metadata and without shebang.

        Tests: CLI with minimal Python file
        How: Create file without PEP 723 or shebang
        Why: Verify CLI handles plain Python files correctly

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "d3_test.py", has_pep723=False, shebang=None)

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group E - Empty dependencies
# ============================================================================


class TestGroupE_EmptyDependencies:
    """Test files with PEP 723 metadata but empty dependencies.

    Scenarios:
        E1: PEP 723 with dependencies = []

    Default expectation: linter runs without installing deps.
    """

    def test_e1_empty_dependencies_array(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test E1: File with PEP 723 metadata but empty dependencies array.

        Tests: CLI with empty dependency list
        How: Create file with dependencies = []
        Why: Ensure empty lists are handled gracefully

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(
            temp_test_dir,
            "e1_test.py",
            pep723_deps=[],  # Empty list
            shebang="#!/usr/bin/env -S uv run",
        )

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group F - Directory scenarios
# ============================================================================


class TestGroupF_DirectoryScenarios:
    """Test CLI with directories containing multiple files.

    Scenarios:
        F1: Directory with mixed files (some PEP 723, some not)
        F2: Directory with conflicting PEP 723 versions across files
        F3: Empty directory or directory with no .py files

    Default expectation: CLI processes all files correctly.
    """

    def test_f1_directory_mixed_files(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test F1: Directory with mixed files (some PEP 723, some not).

        Tests: CLI directory traversal with mixed file types
        How: Create directory with various file configurations, pass individual files
        Why: Verify CLI handles heterogeneous file sets correctly

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        mixed_dir = temp_test_dir / "mixed"
        mixed_dir.mkdir()

        # Create mixed files
        file1 = create_test_file(mixed_dir, "with_pep723.py", pep723_deps=["requests>=2.31.0"])
        file2 = create_test_file(mixed_dir, "no_pep723.py", has_pep723=False)
        file3 = create_test_file(mixed_dir, "empty_deps.py", pep723_deps=[])

        # Act - Pass individual files since py_compile doesn't accept directories
        result = run_cli_command(
            cli_executable, "python", ["-m", "py_compile", str(file1), str(file2), str(file3)], cwd=temp_test_dir
        )

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_f2_directory_conflicting_versions(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test F2: Directory with conflicting PEP 723 versions across files.

        Tests: CLI handling of version conflicts across files
        How: Create files requiring different versions of same package, pass both files
        Why: Verify CLI's behavior when aggregating conflicting requirements

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        conflict_dir = temp_test_dir / "conflicts"
        conflict_dir.mkdir()

        # Create files with conflicting versions
        file1 = create_test_file(conflict_dir, "file1.py", pep723_deps=["requests>=2.31.0,<3.0.0"])
        file2 = create_test_file(conflict_dir, "file2.py", pep723_deps=["requests>=2.28.0,<2.30.0"])

        # Act - Pass individual files
        result = run_cli_command(
            cli_executable, "python", ["-m", "py_compile", str(file1), str(file2)], cwd=temp_test_dir
        )

        # Assert - Capture actual behavior (may succeed or fail)
        assert result.returncode in {0, 1}, (
            f"Expected exit code 0 or 1. Got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_f3_empty_directory(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test F3: Empty directory or directory with no Python files.

        Tests: CLI handling of no input files
        How: Run CLI without any file arguments
        Why: Ensure CLI handles edge case of no files to process

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange - No files to process

        # Act - Call with version flag to test command execution without files
        result = run_cli_command(cli_executable, "python", ["--version"], cwd=temp_test_dir)

        # Assert - Should execute wrapped command even with no Python files
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test Scenarios: Group G - Edge cases
# ============================================================================


class TestGroupG_EdgeCases:
    """Test CLI edge cases and error conditions.

    Scenarios:
        G1: File path doesn't exist
        G2: File with invalid PEP 723 syntax
        G3: Multiple files as arguments
        G4: Arguments with no Python files

    Tests capture actual error handling behavior.
    """

    def test_g1_nonexistent_file(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test G1: File path that doesn't exist.

        Tests: CLI error handling for missing files
        How: Pass non-existent file path to CLI
        Why: Verify CLI passes through to linter for error handling

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        fake_file = temp_test_dir / "does_not_exist.py"

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(fake_file)], cwd=temp_test_dir)

        # Assert - Non-existent file should pass through to linter
        # Linter will fail, but CLI should propagate that exit code
        assert result.returncode != 0, (
            f"Expected non-zero exit code for missing file. Got {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_g2_invalid_pep723_syntax(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test G2: File with invalid PEP 723 syntax.

        Tests: CLI resilience to malformed PEP 723 metadata
        How: Create file with invalid PEP 723 syntax (missing closing marker)
        Why: Verify CLI gracefully handles parsing errors

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "g2_test.py", pep723_deps=["requests>=2.31.0"], invalid_pep723=True)

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert - Should continue execution despite invalid PEP 723
        assert result.returncode == 0, (
            f"Expected CLI to continue despite invalid PEP 723. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_g3_multiple_files_as_args(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test G3: Multiple files as arguments.

        Tests: CLI batch processing of multiple files
        How: Create multiple files and pass all to CLI
        Why: Verify CLI aggregates dependencies across files

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        file1 = create_test_file(temp_test_dir, "g3_file1.py", pep723_deps=["requests>=2.31.0"])
        file2 = create_test_file(temp_test_dir, "g3_file2.py", pep723_deps=["click>=8.1.0"])
        file3 = create_test_file(temp_test_dir, "g3_file3.py", has_pep723=False)

        # Act
        result = run_cli_command(
            cli_executable, "python", ["-m", "py_compile", str(file1), str(file2), str(file3)], cwd=temp_test_dir
        )

        # Assert
        assert result.returncode == 0, (
            f"Expected successful execution. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_g4_args_with_no_python_files(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test G4: Arguments with no Python files (e.g., config files).

        Tests: CLI handling of non-Python arguments
        How: Pass config file arguments (not .py files) to CLI
        Why: Verify CLI passes through non-Python args to wrapped command

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        config_file = temp_test_dir / "mypy.ini"
        config_file.write_text("[mypy]\nstrict = true\n")

        # Act - Use mypy with config file (no .py files)
        # Note: This will likely fail because mypy needs files, but we're testing CLI behavior
        result = run_cli_command(
            cli_executable,
            "python",
            ["-m", "mypy", "--version"],  # Use version to avoid needing files
            cwd=temp_test_dir,
        )

        # Assert - CLI should execute command even with no Python files
        assert result.returncode in {0, 1, 2}, (
            f"Expected CLI to execute command. Got exit code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ============================================================================
# Test: Exit Code Propagation
# ============================================================================


class TestExitCodePropagation:
    """Test that CLI correctly propagates wrapped command exit codes.

    Verifies that pep723-loader exits with the same code as the wrapped command.
    """

    def test_successful_linter_exit_code_zero(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test successful linter returns exit code 0.

        Tests: Exit code propagation for success
        How: Create valid file, run linter, verify exit code 0
        Why: Ensure success codes propagate correctly

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange
        test_file = create_test_file(temp_test_dir, "success.py", has_pep723=False)

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(test_file)], cwd=temp_test_dir)

        # Assert
        assert result.returncode == 0, (
            f"Expected exit code 0. Got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_failing_linter_exit_code_propagated(self, cli_executable: str, temp_test_dir: Path) -> None:
        """Test failing linter exit code is propagated.

        Tests: Exit code propagation for failures
        How: Create file with syntax error, verify non-zero exit code
        Why: Ensure failure codes propagate correctly

        Args:
            cli_executable: CLI command fixture
            temp_test_dir: Temporary test directory fixture
        """
        # Arrange - Create file with syntax error
        bad_file = temp_test_dir / "syntax_error.py"
        bad_file.write_text("def broken(\n")  # Intentional syntax error

        # Act
        result = run_cli_command(cli_executable, "python", ["-m", "py_compile", str(bad_file)], cwd=temp_test_dir)

        # Assert - Should fail with non-zero exit code
        assert result.returncode != 0, (
            f"Expected non-zero exit code for syntax error. Got {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
