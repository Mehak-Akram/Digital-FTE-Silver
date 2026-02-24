"""
Logging configuration for Silver Tier AI Employee.

Provides centralized logging setup with file rotation and retention.
"""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

# Log directory
LOG_DIR = Path(r"E:\AI_Employee_Vault\mcp_server\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Optional specific log file name. If None, uses default naming.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with daily rotation
    if log_file is None:
        log_file = f"{name.replace('.', '_')}.log"

    file_path = LOG_DIR / log_file
    file_handler = TimedRotatingFileHandler(
        file_path,
        when='midnight',
        interval=1,
        backupCount=LOG_RETENTION_DAYS,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def cleanup_old_logs():
    """Remove log files older than LOG_RETENTION_DAYS."""
    if not LOG_DIR.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)

    for log_file in LOG_DIR.glob("*.log*"):
        try:
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                log_file.unlink()
                print(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            print(f"Error deleting log file {log_file.name}: {e}")


if __name__ == "__main__":
    # Test logging configuration
    test_logger = get_logger("test_logger")
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")
    print(f"Logging configured. Log level: {LOG_LEVEL}, Retention: {LOG_RETENTION_DAYS} days")
    print(f"Log directory: {LOG_DIR}")
