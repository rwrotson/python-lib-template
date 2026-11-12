from pathlib import Path

import pytest

from my_lib.utils.misc import find_project_root


def test_find_project_root_searches_upwards_from_start(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_project_root(start=nested) == tmp_path.resolve()


def test_find_project_root_starts_from_working_directory(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    assert find_project_root() == tmp_path.resolve()


def test_find_project_root_raises_without_marker(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="_missing_marker_"):
        find_project_root(marker="_missing_marker_", start=tmp_path)
