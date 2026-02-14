"""Dashboard update functionality for Bronze Tier AI Employee.

Scans vault folders and regenerates Dashboard.md with current state.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def count_markdown_files(directory: Path) -> int:
    """
    Count .md files in a directory.

    Args:
        directory: Path to directory to scan

    Returns:
        Number of .md files found (0 if directory doesn't exist)
    """
    if not directory.exists() or not directory.is_dir():
        return 0

    return len(list(directory.glob("*.md")))


def get_folder_counts(vault_path: Path) -> Dict[str, int]:
    """
    Get task counts for all workflow folders.

    Args:
        vault_path: Root path of the vault

    Returns:
        Dictionary mapping folder names to file counts
    """
    folders = {
        "Inbox": vault_path / "Inbox",
        "Needs_Action": vault_path / "Needs_Action",
        "Plans": vault_path / "Plans",
        "Done": vault_path / "Done"
    }

    return {name: count_markdown_files(path) for name, path in folders.items()}


def get_recent_activity(log_file: Path, max_entries: int = 10) -> List[str]:
    """
    Extract recent activity from watcher log.

    Args:
        log_file: Path to watcher log file
        max_entries: Maximum number of entries to return

    Returns:
        List of recent activity entries (empty if log doesn't exist)
    """
    if not log_file.exists():
        return []

    try:
        lines = log_file.read_text().strip().split('\n')
        # Return last N non-empty lines
        recent = [line for line in lines if line.strip()][-max_entries:]
        return recent
    except Exception:
        return []


def generate_dashboard_content(
    vault_path: Path,
    log_file: Path = None
) -> str:
    """
    Generate complete Dashboard.md content.

    Args:
        vault_path: Root path of the vault
        log_file: Optional path to watcher log file

    Returns:
        Formatted dashboard content as string
    """
    # Get current counts
    counts = get_folder_counts(vault_path)

    # Get timestamp
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    # Build dashboard content
    content = f"""# Dashboard

**Last Updated**: {timestamp}

## Task Counts

- **Inbox**: {counts['Inbox']} task{'s' if counts['Inbox'] != 1 else ''}
- **Needs Action**: {counts['Needs_Action']} task{'s' if counts['Needs_Action'] != 1 else ''}
- **Plans**: {counts['Plans']} plan{'s' if counts['Plans'] != 1 else ''}
- **Done**: {counts['Done']} completed

## Recent Activity

"""

    # Add recent activity
    if log_file and log_file.exists():
        activity = get_recent_activity(log_file)
        if activity:
            for entry in activity:
                content += f"- {entry}\n"
        else:
            content += "No recent activity.\n"
    else:
        content += "No recent activity.\n"

    content += f"""
## System Status

- **Watcher**: not started
- **Last Watcher Event**: N/A
- **Vault Path**: {vault_path}
"""

    return content


def update_dashboard(vault_path: Path, log_file: Path = None) -> None:
    """
    Update Dashboard.md with current vault state.

    Args:
        vault_path: Root path of the vault
        log_file: Optional path to watcher log file
    """
    dashboard_path = vault_path / "Dashboard.md"
    content = generate_dashboard_content(vault_path, log_file)
    dashboard_path.write_text(content, encoding='utf-8')
    print(f"Dashboard updated: {dashboard_path}")


if __name__ == "__main__":
    # Default vault path
    vault = Path("E:/AI_Employee_Vault")
    log = vault / ".watcher" / "watcher.log"

    update_dashboard(vault, log)
