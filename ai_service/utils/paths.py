"""
Path resolution utilities for AI service.

Provides centralized path resolution from project root for consistency
across the application.
"""

from pathlib import Path
from typing import Union


def get_project_root() -> Path:
    """
    Get the project root directory (parent of ai_service/).

    Returns:
        Path: Absolute path to project root directory
    """
    # This file is at ai_service/utils/paths.py
    # Go up two levels to get project root
    return Path(__file__).parent.parent.parent


def resolve_from_project_root(path: Union[str, Path]) -> Path:
    """
    Resolve a path from the project root directory.

    If the path is absolute, it's returned as-is.
    If the path is relative, it's resolved from the project root.

    Args:
        path: Path to resolve (can be string or Path object)

    Returns:
        Path: Absolute resolved path

    Examples:
        >>> resolve_from_project_root("db.sqlite3")
        Path("/home/user/project/db.sqlite3")

        >>> resolve_from_project_root("/absolute/path/to/file")
        Path("/absolute/path/to/file")
    """
    path_obj = Path(path)

    if path_obj.is_absolute():
        return path_obj

    project_root = get_project_root()
    return (project_root / path_obj).resolve()


def get_database_path(db_path: Union[str, Path, None] = None) -> Path:
    """
    Get the resolved database path.

    If db_path is None, defaults to project_root/db.sqlite3.
    If db_path is provided, resolves it from project root (if relative).

    Args:
        db_path: Optional database path (defaults to db.sqlite3 in project root)

    Returns:
        Path: Absolute path to database file
    """
    if db_path is None:
        return get_project_root() / "db.sqlite3"

    return resolve_from_project_root(db_path)
