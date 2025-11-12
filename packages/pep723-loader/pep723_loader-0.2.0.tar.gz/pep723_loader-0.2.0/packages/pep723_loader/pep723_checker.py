"""PEP 723 checker for Python scripts.

This module provides functionality to check Python scripts for PEP 723 inline metadata
and extract their requirements.
"""

import contextlib
import os
import subprocess
from collections.abc import Generator
from pathlib import Path
from shutil import which

from git import InvalidGitRepositoryError, Repo

PathStr = Path | str
PathStrList = list[PathStr] | list[str] | list[Path]
PathList = list[Path]
RequirementsSet = set[str]
SKIP_DIRS = [
    "__pycache__",
    ".git",
    ".venv",
    ".env",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
]


class Pep723Checker:
    """Check Python scripts for PEP 723 inline metadata and extract requirements.

    This class accepts flexible input (single path or list of paths) and processes them
    to extract PEP 723 requirements using `uv export --script`.

    Args:
        scripts_input: Single path or list of paths (as strings or Path objects)

    Attributes:
        max_depth: Maximum depth for recursive directory traversal (default: 4)
        requirements_set: Set of requirement strings from successful `uv export` executions
    """

    max_depth: int = 4

    def __init__(self, scripts_input: Path | str | list[Path | str] | list[str] | list[Path]) -> None:
        """Initialize the PEP 723 checker with script paths.

        Args:
            scripts_input: Single path or list of paths to Python scripts or directories
        """
        self._requirements_set: RequirementsSet = set()
        self._uv_path: Path | None = None
        self._process_scripts(scripts_input)

    @property
    def requirements_set(self) -> RequirementsSet:
        """Get the set of requirements extracted from scripts.

        Returns:
            Set of requirement strings from successful `uv export` executions
        """
        return self._requirements_set

    def _normalize_input(self, scripts_input: PathStr | PathStrList) -> PathList:
        """Normalize input to a deduplicated, sorted list of Path objects.

        Args:
            scripts_input: Single path or list of paths

        Returns:
            Deduplicated and sorted list of Path objects
        """
        # Convert single value to list
        scripts_list: PathStrList = [scripts_input] if isinstance(scripts_input, (Path, str)) else scripts_input
        # Convert to Path objects, filter existing, deduplicate and sort
        return sorted({Path(p) for p in scripts_list if Path(p).exists()})

    def _get_git_repository(self, path: Path) -> Repo | None:
        """Get the git repository for the current working directory.

        Returns:
            Git repository for the current working directory
        """
        try:
            # Try to find repo from the path
            return Repo(path, search_parent_directories=True)
        except (InvalidGitRepositoryError, Exception):
            return None

    def get_all_items(
        self, root: Path, match_pattern: str = "*.py", exclude: list[str] = SKIP_DIRS
    ) -> Generator[Path, None, None]:
        """Get all items matching the pattern from the root directory.

        Uses git ls-files if in a git repository, otherwise recursively traverses directories.

        Args:
            root: Root directory to search
            match_pattern: Glob pattern to match files (default: "*.py")
            exclude: List of directory names to skip (default: SKIP_DIRS)

        Yields:
            Path objects for files matching the pattern
        """
        if root.is_dir() and (repo := self._get_git_repository(root)):
            for item in map(Path, repo.git.ls_files().splitlines()):
                if item.match(match_pattern) and not set(item.parts).isdisjoint(SKIP_DIRS):
                    yield item
        else:
            for item in root.iterdir():
                if item.name in exclude:
                    continue
                if not item.is_dir() and item.match(match_pattern):
                    yield item
                if item.is_dir():
                    yield from self.get_all_items(item, match_pattern, exclude)

    def _expand_directories(self, paths: PathList) -> Generator[Path, None, None]:
        """Expand directories to Python files using glob

        Args:
            paths: List of paths (files or directories)

        Yields:
            Path objects for Python files from directories, or the files themselves
        """
        for path in paths:
            if path.is_file() and path.match("*.py"):
                yield path
            elif path.is_dir():
                yield from self.get_all_items(path)

    def _normalize_paths(self, paths: PathList) -> PathList:
        """Normalize paths by resolving symlinks and converting to relative paths.

        Args:
            paths: List of paths to normalize

        Returns:
            Deduplicated and sorted list of normalized paths
        """
        normalized: PathList = []
        cwd = Path.cwd()

        for path in paths:
            try:
                # Resolve symlinks
                resolved = path.resolve()
                # Convert to relative path
                relative = Path(os.path.relpath(resolved, cwd))
                normalized.append(relative)
            except (OSError, ValueError):
                # Silently skip paths we can't normalize
                pass

        # Deduplicate and sort
        return sorted(set(normalized))

    def resolve_uv(self) -> Path:
        """Resolve the uv path."""
        if not self._uv_path:
            import importlib.util
            import sys

            # Check if uv package is available
            if importlib.util.find_spec("uv") is not None:
                # uv package installed - look for binary in venv
                uv_bin = Path(sys.prefix) / "bin" / "uv"
                if uv_bin.exists():
                    self._uv_path = uv_bin
                else:
                    # Fallback to PATH if binary not in expected location
                    uv_path_str = which("uv")
                    if not uv_path_str:
                        msg = "uv binary not found in venv or PATH"
                        raise RuntimeError(msg)
                    self._uv_path = Path(uv_path_str)
            else:
                # uv package not installed - look in PATH
                uv_path_str = which("uv")
                if not uv_path_str:
                    msg = "uv not found - install with: pip install uv"
                    raise RuntimeError(msg)
                self._uv_path = Path(uv_path_str)
        return self._uv_path

    def _execute_uv_export(self, script_path: Path) -> str | None:
        """Execute `uv export --script` for a single script.

        Args:
            script_path: Path to the Python script

        Returns:
            Complete stdout string if successful, None if any error occurs
        """
        uv_path = self.resolve_uv()
        with contextlib.suppress(subprocess.TimeoutExpired):
            result = subprocess.run(
                [uv_path, "export", "--script", str(script_path)],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,  # Don't raise on non-zero exit
            )

            # Only return stdout if command succeeded
            if result.returncode == 0:
                return result.stdout

        return None

    def _process_scripts(self, scripts_input: Path | str | list[Path | str] | list[str] | list[Path]) -> None:
        """Process scripts to extract PEP 723 requirements.

        Args:
            scripts_input: Single path or list of paths to process
        """
        # Step 1: Normalize input to list
        paths = self._normalize_input(scripts_input)

        # Step 2: Filter existing paths (already done in _normalize_input)
        # Step 3: Expand directories
        expanded_paths: PathList = list(self._expand_directories(paths))

        # Step 4: Normalize all paths
        normalized_paths: PathList = self._normalize_paths(expanded_paths)

        # Step 5: Execute uv export for each file
        for script_path in normalized_paths:
            output = self._execute_uv_export(script_path)
            if output is not None:
                # Step 6: Store results
                self._requirements_set.add(output)
