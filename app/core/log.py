"""Logging configuration for Boop application."""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.core.path import get_log_path


def is_packaged_app():
    """Check if running in a packaged (PyInstaller) app."""
    return getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')


def setup_logging():
    """Set up logging configuration with rotating file handler."""
    # Use centralized log path
    log_dir = get_log_path()

    # Log file path
    log_file = log_dir / "boop.log"

    # Create formatter
    class AbbreviatedPathFormatter(logging.Formatter):
        def format(self, record):
            # Abbreviate package path: boop.core.logging -> b.c.logging
            if record.name.startswith('boop.'):
                parts = record.name.split('.')
                if len(parts) > 1:
                    abbreviated = '.'.join([p[0] for p in parts[:-1]] + [parts[-1]])
                    record.name = abbreviated
            return super().format(record)

    # Create rotating file handler (5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8',
        delay=True  # Delay file creation until first log message
    )
    formatter = AbbreviatedPathFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Set log level based on environment
    # In packaged app, use INFO level to reduce debug noise
    # In development, use DEBUG level for detailed logging
    log_level = logging.INFO if is_packaged_app() else logging.DEBUG
    file_handler.setLevel(log_level)

    # Create stream handler (only for errors in production)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # Configure root logging
    logging.basicConfig(
        level=log_level,
        handlers=[
            file_handler,
            stream_handler
        ],
        force=True  # Override any existing handlers
    )

    return logging.getLogger(__name__)


# Create a default logger
logger = setup_logging()
