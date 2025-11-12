"""PEP 723 loader package for wrapping linting tools with dependency management.

This package provides utilities to parse PEP 723 inline script metadata and
execute linting tools with proper dependency resolution via uv.
"""

from .pep723_checker import Pep723Checker
from .version import __version__

__all__ = ["Pep723Checker", "__version__"]
