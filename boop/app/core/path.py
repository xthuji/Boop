"""Path Utilities - Path-related utility functions for the application"""

import sys
from pathlib import Path
from typing import Optional


def get_user_data_dir() -> Path:
    """Get the user data directory for the application.
    
    Returns:
        Path to the user data directory
    """
    import platform
    import os
    import tempfile
    
    # Check if we're in a PyInstaller bundled environment
    if hasattr(sys, '_MEIPASS'):
        # In bundled app, use platform-specific user data directory
        user_data_dir = Path(sys._MEIPASS) / "data"
    else:
        # In development mode, use project root directory
        project_dir = Path(os.path.dirname(__file__)).parent.parent
        user_data_dir = project_dir / "data"
    
    # Try to create directory if it doesn't exist
    try:
        user_data_dir.mkdir(parents=True, exist_ok=True)
        return user_data_dir
    except (PermissionError, OSError):
        # If we can't create the directory (e.g., sandboxed environment), use temp directory
        temp_dir = Path(tempfile.gettempdir()) / "Boop"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir


def get_log_path() -> Path:
    """Get the log directory path for the application.
    
    Returns:
        Path to the log directory
    """
    log_dir = get_user_data_dir().parent / "logs"
    
    # Create directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir


def get_default_script_dir() -> Optional[Path]:
    """Get the default script directory path for the application.
    
    Returns:
        Path to the default script directory, or None if not found
    """
    # Check if we're in a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        # We're in a PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        # Check direct scripts directory (for macOS Contents/Resources)
        direct_script_dir = bundle_dir / "scripts"
        if direct_script_dir.exists():
            # Resolve symbolic links to get the actual path
            resolved_path = direct_script_dir.resolve()
            return resolved_path
    else:
        # In development mode, use the scripts directory in the same folder as __main__.py
        current_dir = Path(__file__).parent.parent  # boop directory
        dev_script_dir = current_dir / "scripts"
        if dev_script_dir.exists():
            return dev_script_dir
    
    return None

def update_script_directories(script_directories: list) -> list:
    """Update script directories with default directory and remove duplicates.
    
    Args:
        script_directories: Current list of script directories
        
    Returns:
        Updated list of script directories with default directory added and duplicates removed
    """
    # Get default script directory
    default_script_dir = get_default_script_dir()
    
    # Add default script directory if not present
    if default_script_dir:
        script_directories.append(str(default_script_dir))
    
    if len(script_directories) <= 1:
        return script_directories

    # Remove duplicate script directories
    unique_dirs = []
    seen = set()
    for script_dir in script_directories:
        # Resolve the path to check for duplicates
        resolved_dir = Path(script_dir).resolve()
        resolved_dir_str = str(resolved_dir)
        if resolved_dir_str not in seen:
            seen.add(resolved_dir_str)
            unique_dirs.append(script_dir)
    
    return unique_dirs
