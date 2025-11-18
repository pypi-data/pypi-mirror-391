"""Sound track extraction CLI."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sound-track-extract")
except PackageNotFoundError:  # pragma: no cover - fallback for editable installs
    __version__ = "0.0.0"


__all__ = ["__version__"]
