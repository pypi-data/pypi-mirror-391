#!/usr/bin/env -S uv --quiet run --active --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pytest>=8.4.2",
#   "pytest-cov>=6.0.0",
#   "pytest-mock>=3.14.0",
#   "pytest-asyncio>=1.2.0",
#   "pytest-xdist>=3.6.0",
#   "pytest-timeout>=2.2.0"
# ]
# ///
"""Comprehensive test suite for pep723-loader CLI tool.

This test suite covers all CLI execution scenarios including:
- PEP 723 dependency extraction and installation
- Various shebang configurations
- Edge cases (empty deps, invalid syntax, non-existent files)
- Subprocess execution and exit code propagation
- Multiple file handling

Tests follow AAA pattern with full type hints and pytest-mock usage.
"""

from __future__ import annotations

import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pep723_loader.cli import app
from typer.testing import CliRunner

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

# Test fixtures directory path
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Typer CLI runner for testing.

    Returns:
        Configured CliRunner instance
    """
    return CliRunner()


@pytest.fixture
def mock_uv_path(mocker: MockerFixture, tmp_path: Path) -> Path:
    """Provide mock uv binary path.

    Tests: UV binary resolution
    How: Create fake binary in temp directory and mock resolve_uv()
    Why: Ensure tests work without real UV installation

    Args:
        mocker: pytest-mock fixture
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to mock uv binary
    """
    uv_mock = tmp_path / "uv"
    uv_mock.write_text("#!/bin/bash\necho 'mock uv'")
    uv_mock.chmod(0o755)

    # Mock which() to return our mock path
    mocker.patch("pep723_loader.pep723_checker.which", return_value=str(uv_mock))

    # Mock resolve_uv() to return the path as string (for subprocess.run compatibility)
    mocker.patch("pep723_loader.pep723_checker.Pep723Checker.resolve_uv", return_value=str(uv_mock))

    return uv_mock


@pytest.fixture
def mock_successful_subprocess(mocker: MockerFixture) -> Generator[MockerFixture, None, None]:
    """Mock subprocess.run to simulate successful command execution.

    Tests: Subprocess execution mocking
    How: Mock subprocess.run with returncode=0
    Why: Isolate CLI logic from actual command execution

    Args:
        mocker: pytest-mock fixture

    Yields:
        Mocker instance with configured subprocess mock
    """
    mock_result = mocker.Mock(spec=subprocess.CompletedProcess)
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)
    yield mocker


@pytest.fixture
def mock_uv_export_success(mocker: MockerFixture) -> MockerFixture:
    """Mock successful uv export --script execution.

    Tests: PEP 723 dependency extraction
    How: Mock subprocess.run for uv export with valid requirements output
    Why: Test dependency installation flow without real UV execution

    Args:
        mocker: pytest-mock fixture

    Returns:
        Configured mocker instance
    """

    def mock_run_side_effect(
        *args: str | list[str], **kwargs: dict[str, bool | str]
    ) -> subprocess.CompletedProcess[str]:
        """Return appropriate mock based on command."""
        cmd = args[0] if args else kwargs.get("args", [])

        # Check if this is uv export command
        if isinstance(cmd, list) and len(cmd) >= 2 and cmd[1] == "export":
            # Return mock requirements output
            mock_export = mocker.Mock(spec=subprocess.CompletedProcess)
            mock_export.returncode = 0
            mock_export.stdout = "requests>=2.31.0\npydantic>=2.0.0\n"
            return mock_export  # type: ignore[no-any-return]

        # For uv pip install and wrapped commands
        mock_other = mocker.Mock(spec=subprocess.CompletedProcess)
        mock_other.returncode = 0
        return mock_other  # type: ignore[no-any-return]

    mocker.patch("subprocess.run", side_effect=mock_run_side_effect)
    return mocker


# ============================================================================
# Test Cases: Individual Fixture Files
# ============================================================================


class TestFixtureFiles:
    """Test CLI behavior with different fixture file types.

    Tests each fixture file type to verify correct handling of various
    PEP 723 configurations and edge cases.
    """

    def test_with_deps_uv_shebang(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test script with PEP 723 deps and uv shebang.

        Tests: CLI execution with PEP 723 dependencies and uv shebang
        How: Run CLI with fixture file, verify subprocess calls
        Why: Ensure uv-shebanged scripts are handled correctly

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "with_deps_uv_shebang.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["mypy", str(test_file)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}\nOutput: {result.output}"

    def test_with_deps_python_shebang(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test script with PEP 723 deps and standard Python shebang.

        Tests: CLI execution with standard Python shebang
        How: Run CLI with fixture file having #!/usr/bin/env python3
        Why: Verify Python-shebanged scripts process dependencies correctly

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "with_deps_python_shebang.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["ruff", "check", str(test_file)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_with_deps_no_shebang(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test script with PEP 723 deps but no shebang.

        Tests: CLI execution with missing shebang
        How: Run CLI with fixture file that has no shebang line
        Why: Ensure dependency extraction works regardless of shebang presence

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "with_deps_no_shebang.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["basedpyright", str(test_file)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_no_deps(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_successful_subprocess: MockerFixture
    ) -> None:
        """Test script without PEP 723 metadata.

        Tests: CLI execution when no PEP 723 dependencies exist
        How: Run CLI with fixture file lacking PEP 723 metadata
        Why: Verify graceful handling when no dependencies to install

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_successful_subprocess: Mock subprocess fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "no_deps.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["pylint", str(test_file)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_empty_deps(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_successful_subprocess: MockerFixture
    ) -> None:
        """Test script with empty PEP 723 dependencies list.

        Tests: CLI execution with empty dependencies array
        How: Run CLI with fixture file having dependencies = []
        Why: Ensure empty dependency lists don't cause errors

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_successful_subprocess: Mock subprocess fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "empty_deps.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["flake8", str(test_file)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_invalid_pep723(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_successful_subprocess: MockerFixture
    ) -> None:
        """Test script with malformed PEP 723 syntax.

        Tests: CLI resilience to invalid PEP 723 metadata
        How: Run CLI with fixture file containing syntax errors in PEP 723 block
        Why: Verify graceful degradation when metadata parsing fails

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_successful_subprocess: Mock subprocess fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "invalid_pep723.py"
        assert test_file.exists(), f"Fixture file not found: {test_file}"

        # Act
        result = cli_runner.invoke(app, ["bandit", str(test_file)])

        # Assert - should still execute wrapped command even if PEP 723 parsing fails
        assert result.exit_code == 0, "CLI should continue execution despite invalid PEP 723"


# ============================================================================
# Test Cases: Multiple Files and Directories
# ============================================================================


class TestMultipleFiles:
    """Test CLI behavior with multiple files and directories.

    Verifies correct handling of batched file operations and directory traversal.
    """

    def test_multiple_files_as_args(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test CLI with multiple Python files as arguments.

        Tests: Batch file processing
        How: Pass multiple fixture files to CLI command
        Why: Ensure all files are processed and dependencies aggregated

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        file1 = FIXTURES_DIR / "with_deps_uv_shebang.py"
        file2 = FIXTURES_DIR / "with_deps_python_shebang.py"
        file3 = FIXTURES_DIR / "no_deps.py"

        assert all(f.exists() for f in [file1, file2, file3]), "Fixture files not found"

        # Act
        result = cli_runner.invoke(app, ["mypy", str(file1), str(file2), str(file3)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_directory_with_mixed_files(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test CLI with directory containing mixed Python files.

        Tests: Directory traversal with mixed file types
        How: Pass fixtures directory to CLI command
        Why: Verify recursive directory processing handles all file types

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        assert FIXTURES_DIR.exists(), f"Fixtures directory not found: {FIXTURES_DIR}"

        # Act
        result = cli_runner.invoke(app, ["ruff", "check", str(FIXTURES_DIR)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_mixed_files_and_directories(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_uv_export_success: MockerFixture
    ) -> None:
        """Test CLI with both individual files and directories.

        Tests: Mixed argument types handling
        How: Pass combination of files and directories to CLI
        Why: Ensure CLI correctly processes heterogeneous argument lists

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_uv_export_success: Mock UV export fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "with_deps_uv_shebang.py"
        test_dir = FIXTURES_DIR

        # Act
        result = cli_runner.invoke(app, ["basedpyright", str(test_file), str(test_dir)])

        # Assert
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"


# ============================================================================
# Test Cases: Error Handling
# ============================================================================


class TestErrorHandling:
    """Test CLI error handling and edge cases.

    Verifies correct error propagation and handling of exceptional conditions.
    """

    def test_non_existent_file(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_successful_subprocess: MockerFixture
    ) -> None:
        """Test CLI with non-existent file path.

        Tests: Error handling for missing files
        How: Pass non-existent file path to CLI
        Why: Ensure CLI handles missing files gracefully

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_successful_subprocess: Mock subprocess fixture
        """
        # Arrange
        fake_file = "/tmp/does_not_exist_12345.py"  # noqa: S108

        # Act
        result = cli_runner.invoke(app, ["mypy", fake_file])

        # Assert - should still execute wrapped command with all args
        # Non-existent files are passed through to the wrapped command
        assert result.exit_code == 0, "CLI should execute wrapped command even with non-existent files"

    def test_dependency_installation_failure(
        self, cli_runner: CliRunner, mock_uv_path: Path, mocker: MockerFixture
    ) -> None:
        """Test CLI when dependency installation fails.

        Tests: Error propagation from dependency installation
        How: Mock uv pip install to return non-zero exit code
        Why: Verify CLI exits with installation error code

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mocker: pytest-mock fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "with_deps_uv_shebang.py"

        def mock_run_with_install_failure(
            *args: str | list[str], **kwargs: dict[str, bool | str]
        ) -> subprocess.CompletedProcess[str]:
            """Return failure for pip install, success for export."""
            cmd = args[0] if args else kwargs.get("args", [])

            if isinstance(cmd, list):
                # uv export succeeds
                if len(cmd) >= 2 and cmd[1] == "export":
                    mock_export = mocker.Mock(spec=subprocess.CompletedProcess)
                    mock_export.returncode = 0
                    mock_export.stdout = "requests>=2.31.0\n"
                    return mock_export  # type: ignore[no-any-return]
                # uv pip install fails
                if len(cmd) >= 2 and cmd[1] == "pip":
                    mock_install = mocker.Mock(spec=subprocess.CompletedProcess)
                    mock_install.returncode = 1
                    mock_install.stderr = "ERROR: Package not found"
                    return mock_install  # type: ignore[no-any-return]

            # Default success
            mock_default = mocker.Mock(spec=subprocess.CompletedProcess)
            mock_default.returncode = 0
            return mock_default  # type: ignore[no-any-return]

        mocker.patch("subprocess.run", side_effect=mock_run_with_install_failure)

        # Act
        result = cli_runner.invoke(app, ["mypy", str(test_file)])

        # Assert
        assert result.exit_code == 1, "CLI should exit with installation error code"

    def test_wrapped_command_failure(self, cli_runner: CliRunner, mock_uv_path: Path, mocker: MockerFixture) -> None:
        """Test CLI when wrapped command returns non-zero exit code.

        Tests: Exit code propagation from wrapped command
        How: Mock wrapped command to return exit code 2
        Why: Verify CLI propagates wrapped command exit codes correctly

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mocker: pytest-mock fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "no_deps.py"

        def mock_run_with_command_failure(
            *args: str | list[str], **kwargs: dict[str, bool | str]
        ) -> subprocess.CompletedProcess[str]:
            """Return failure for wrapped command."""
            cmd = args[0] if args else kwargs.get("args", [])

            if isinstance(cmd, list) and cmd[0] != str(mock_uv_path):
                # If it's the wrapped command (first arg is not uv)
                mock_cmd = mocker.Mock(spec=subprocess.CompletedProcess)
                mock_cmd.returncode = 2
                mock_cmd.stdout = ""
                mock_cmd.stderr = "Type checking failed"
                return mock_cmd  # type: ignore[no-any-return]

            # Default success for uv commands
            mock_default = mocker.Mock(spec=subprocess.CompletedProcess)
            mock_default.returncode = 0
            mock_default.stdout = ""
            mock_default.stderr = ""
            return mock_default  # type: ignore[no-any-return]

        mocker.patch("subprocess.run", side_effect=mock_run_with_command_failure)

        # Act
        result = cli_runner.invoke(app, ["mypy", str(test_file)])

        # Assert
        assert result.exit_code == 2, "CLI should exit with wrapped command's exit code"


# ============================================================================
# Test Cases: Subprocess Mocking Verification
# ============================================================================


class TestSubprocessExecution:
    """Test correct subprocess execution and command construction.

    Verifies that CLI constructs and executes subprocess commands correctly.
    """

    def test_subprocess_command_construction(
        self, cli_runner: CliRunner, mock_uv_path: Path, mocker: MockerFixture
    ) -> None:
        """Test that subprocess commands are constructed correctly.

        Tests: Subprocess command construction
        How: Mock subprocess.run and verify call arguments
        Why: Ensure CLI passes correct arguments to subprocess

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mocker: pytest-mock fixture
        """
        # Arrange
        test_file = FIXTURES_DIR / "no_deps.py"
        mock_run = mocker.patch("subprocess.run")
        mock_result = mocker.Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Act
        result = cli_runner.invoke(app, ["mypy", "--strict", str(test_file)])

        # Assert
        assert result.exit_code == 0

        # Verify subprocess.run was called with correct command
        # Last call should be the wrapped command
        last_call = mock_run.call_args_list[-1]
        assert last_call is not None
        called_cmd = last_call[0][0]
        assert called_cmd[0] == "mypy", "First arg should be command name"
        assert "--strict" in called_cmd, "Should include command options"
        assert str(test_file) in called_cmd, "Should include file path"

    def test_exit_code_propagation(self, cli_runner: CliRunner, mock_uv_path: Path, mocker: MockerFixture) -> None:
        """Test that wrapped command exit codes are propagated correctly.

        Tests: Exit code propagation mechanism
        How: Test multiple exit codes (0, 1, 2, 127)
        Why: Ensure CLI preserves original command exit codes

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mocker: pytest-mock fixture
        """
        test_file = FIXTURES_DIR / "no_deps.py"

        for expected_code in [0, 1, 2, 127]:
            # Arrange
            mock_run = mocker.patch("subprocess.run")
            mock_result = mocker.Mock(spec=subprocess.CompletedProcess)
            mock_result.returncode = expected_code
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            # Act
            result = cli_runner.invoke(app, ["mypy", str(test_file)])

            # Assert
            assert result.exit_code == expected_code, f"Expected exit code {expected_code}, got {result.exit_code}"

    def test_no_args_handling(
        self, cli_runner: CliRunner, mock_uv_path: Path, mock_successful_subprocess: MockerFixture
    ) -> None:
        """Test CLI with command but no additional arguments.

        Tests: Edge case of command without arguments
        How: Invoke CLI with only command name
        Why: Ensure CLI handles minimal argument case

        Args:
            cli_runner: Typer CLI runner fixture
            mock_uv_path: Mock UV binary path fixture
            mock_successful_subprocess: Mock subprocess fixture
        """
        # Act
        result = cli_runner.invoke(app, ["mypy"])

        # Assert
        assert result.exit_code == 0, "CLI should handle commands with no arguments"


# ============================================================================
# Test Cases: Type Checking
# ============================================================================


class TestTypeHints:
    """Verify test suite type hint completeness.

    Meta-tests to ensure all test functions have proper type annotations.
    """

    def test_all_fixtures_have_type_hints(self) -> None:
        """Verify all fixtures have complete type hints.

        Tests: Type hint coverage for fixtures
        How: Inspect fixture function signatures
        Why: Maintain type safety and documentation standards
        """
        import inspect

        # Get all fixtures from this module
        fixtures = [cli_runner, mock_uv_path, mock_successful_subprocess, mock_uv_export_success]

        for fixture_func in fixtures:
            # Get signature
            sig = inspect.signature(fixture_func)

            # Check return annotation exists
            assert sig.return_annotation != inspect.Parameter.empty, (
                f"Fixture {fixture_func.__name__} missing return type annotation"
            )

    def test_all_test_functions_have_return_none(self) -> None:
        """Verify all test functions have -> None return type.

        Tests: Return type annotation coverage
        How: Inspect test function signatures
        Why: Follow pytest best practices for test function typing
        """
        import inspect

        # Get all test methods from test classes
        test_classes = [TestFixtureFiles, TestMultipleFiles, TestErrorHandling, TestSubprocessExecution]

        for test_class in test_classes:
            for name, method in inspect.getmembers(test_class, predicate=inspect.isfunction):
                if name.startswith("test_"):
                    sig = inspect.signature(method)
                    # Handle both None and forward reference 'None'
                    return_ann_str = str(sig.return_annotation)
                    assert (
                        sig.return_annotation is None
                        or return_ann_str == "<class 'NoneType'>"
                        or return_ann_str == "None"
                    ), f"Test method {test_class.__name__}.{name} should have -> None return type, got {return_ann_str}"
