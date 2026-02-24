"""
File utilities for Silver Tier AI Employee.

Provides file locking and frontmatter parsing functions for safe concurrent access.
"""
import sys
import time
import frontmatter
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Platform-specific file locking
if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl


@contextmanager
def lock_file(file_handle, timeout: int = 5):
    """
    Context manager for file locking with timeout.

    Args:
        file_handle: Open file handle
        timeout: Maximum seconds to wait for lock (default: 5)

    Raises:
        TimeoutError: If lock cannot be acquired within timeout
    """
    start_time = time.time()
    locked = False

    try:
        while time.time() - start_time < timeout:
            try:
                if sys.platform == 'win32':
                    msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except (IOError, OSError):
                time.sleep(0.1)

        if not locked:
            raise TimeoutError(f"Could not acquire file lock within {timeout} seconds")

        yield file_handle

    finally:
        if locked:
            try:
                if sys.platform == 'win32':
                    msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
            except (IOError, OSError):
                pass


def read_task_file(file_path: Path) -> Dict[str, Any]:
    """
    Read a task file with YAML frontmatter.

    Args:
        file_path: Path to task file

    Returns:
        Dictionary with 'metadata' and 'content' keys

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If frontmatter is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Task file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        with lock_file(f):
            post = frontmatter.load(f)

    return {
        'metadata': dict(post.metadata),
        'content': post.content
    }


def write_task_file(file_path: Path, metadata: Dict[str, Any], content: str):
    """
    Write a task file with YAML frontmatter.

    Args:
        file_path: Path to task file
        metadata: Dictionary of frontmatter fields
        content: Markdown content body

    Raises:
        IOError: If file cannot be written
    """
    post = frontmatter.Post(content, **metadata)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        with lock_file(f):
            f.write(frontmatter.dumps(post))


def read_plan_file(file_path: Path) -> Dict[str, Any]:
    """
    Read a plan file with YAML frontmatter.

    Args:
        file_path: Path to plan file

    Returns:
        Dictionary with 'metadata' and 'content' keys

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If frontmatter is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Plan file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        with lock_file(f):
            post = frontmatter.load(f)

    return {
        'metadata': dict(post.metadata),
        'content': post.content
    }


def write_plan_file(file_path: Path, metadata: Dict[str, Any], content: str):
    """
    Write a plan file with YAML frontmatter.

    Args:
        file_path: Path to plan file
        metadata: Dictionary of frontmatter fields
        content: Markdown content body

    Raises:
        IOError: If file cannot be written
    """
    post = frontmatter.Post(content, **metadata)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        with lock_file(f):
            f.write(frontmatter.dumps(post))


def update_task_metadata(file_path: Path, updates: Dict[str, Any]):
    """
    Update specific metadata fields in a task file without modifying content.

    Args:
        file_path: Path to task file
        updates: Dictionary of metadata fields to update

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    task_data = read_task_file(file_path)
    task_data['metadata'].update(updates)
    write_task_file(file_path, task_data['metadata'], task_data['content'])


def update_plan_metadata(file_path: Path, updates: Dict[str, Any]):
    """
    Update specific metadata fields in a plan file without modifying content.

    Args:
        file_path: Path to plan file
        updates: Dictionary of metadata fields to update

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    plan_data = read_plan_file(file_path)
    plan_data['metadata'].update(updates)
    write_plan_file(file_path, plan_data['metadata'], plan_data['content'])


if __name__ == "__main__":
    # Test file utilities
    from datetime import datetime

    test_file = Path("test_task.md")

    # Test write
    metadata = {
        'id': 'test-001',
        'title': 'Test Task',
        'status': 'new',
        'created_at': datetime.now().isoformat(),
        'priority': 'P3'
    }
    content = "# Test Task\n\nThis is a test task."

    write_task_file(test_file, metadata, content)
    print(f"Created test file: {test_file}")

    # Test read
    task_data = read_task_file(test_file)
    print(f"Read task: {task_data['metadata']['title']}")

    # Test update
    update_task_metadata(test_file, {'status': 'completed'})
    updated_data = read_task_file(test_file)
    print(f"Updated status: {updated_data['metadata']['status']}")

    # Cleanup
    test_file.unlink()
    print("Test completed successfully")
