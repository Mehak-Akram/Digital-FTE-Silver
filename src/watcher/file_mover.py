"""File movement utilities with collision handling."""
import shutil
from pathlib import Path
from datetime import datetime


def safe_move(source: Path, dest_dir: Path) -> Path:
    """
    Move a file to destination directory with collision handling.

    If a file with the same name exists in the destination, appends
    an ISO 8601 timestamp to the filename to prevent overwrite.

    Args:
        source: Source file path
        dest_dir: Destination directory path

    Returns:
        Path to the moved file in destination directory

    Raises:
        FileNotFoundError: If source file doesn't exist
        NotADirectoryError: If dest_dir is not a directory
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    if not dest_dir.is_dir():
        raise NotADirectoryError(f"Destination is not a directory: {dest_dir}")

    # Construct destination path
    dest = dest_dir / source.name

    # Handle collision by appending timestamp
    if dest.exists():
        timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
        stem = source.stem
        suffix = source.suffix
        dest = dest_dir / f"{stem}-{timestamp}{suffix}"

    # Move file
    shutil.move(str(source), str(dest))

    return dest
