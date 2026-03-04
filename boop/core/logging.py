"""Logging configuration for Boop application."""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from boop.core.path import get_log_path


def setup_logging():
    """Set up logging configuration with rotating file handler."""
    # Use centralized log path
    log_dir = get_log_path()

    # Log file path
    log_file = log_dir / "boop.log"

    # Configure logging with abbreviated package paths
    class AbbreviatedPathFormatter(logging.Formatter):
        def format(self, record):
            # Abbreviate package path: boop.core.logging -> b.c.logging
            if record.name.startswith('boop.'):
                parts = record.name.split('.')
                if len(parts) > 1:
                    abbreviated = '.'.join([p[0] for p in parts[:-1]] + [parts[-1]])
                    record.name = abbreviated
            return super().format(record)

    # Create formatter
    formatter = AbbreviatedPathFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create rotating file handler (5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8',
        delay=True  # Delay file creation until first log message
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Create stream handler (only for errors in production)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # Configure root logging
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            file_handler,
            stream_handler
        ],
        force=True  # Override any existing handlers
    )

    return logging.getLogger(__name__)


# Create a default logger
logger = setup_logging()
