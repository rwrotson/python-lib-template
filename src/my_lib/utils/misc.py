from pathlib import Path


def find_project_root(marker: str = "pyproject.toml", start: Path | None = None) -> Path:
    """Find the nearest directory at or above `start` (the working directory) with a marker."""
    origin = (start or Path.cwd()).resolve()
    for directory in (origin, *origin.parents):
        if (directory / marker).exists():
            return directory
    raise FileNotFoundError(f"no {marker} found at or above {origin}")
