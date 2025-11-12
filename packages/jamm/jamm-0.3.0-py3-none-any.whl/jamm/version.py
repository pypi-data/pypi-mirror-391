"""Package version source of truth.

Attempts to read the installed distribution version via importlib.metadata so
runtime reflects the published package. Falls back to the pyproject.toml version
for local editable/source runs before installation.
"""

from importlib.metadata import version as _pkg_version, PackageNotFoundError

try:
    # Use installed package metadata if available
    VERSION = _pkg_version("jamm")
except PackageNotFoundError:
    # Fallback: keep in sync with [project].version in pyproject.toml
    VERSION = "0.3.0"

__all__ = ["VERSION"]
