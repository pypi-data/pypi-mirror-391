import os
from typing import Optional


def walk_files_of_dir(root: str, exts: Optional[list[str]] = None):
    """Walk through all files in a directory

    Args:
        root (str): root directory to start from
        exts (list[str], optional): extension names to filter. Defaults to None.

    Returns:
        dict: directory (relative path) -> list of files
    """
    files = {}

    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(root):
        # Add directory path to the dictionary
        relative_path = os.path.relpath(dirpath, root)
        filenames = sorted(filenames)
        # Filter files by extension
        if exts:
            filenames = [f for f in filenames if str(f).lower().endswith(tuple(exts))]
        files[relative_path] = filenames

    return files
