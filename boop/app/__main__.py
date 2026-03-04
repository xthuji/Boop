"""
Boop Python - Application entry point
"""

import sys
from pathlib import Path

from app.config.settings import BoopConfig
from app.ui.main import MainWindow
from app.core.log import logger
from app.core.path import get_user_data_dir, get_default_script_dir, update_script_directories


def main():
    """Main function to start the application."""
    import time
    start_time = time.time()
    logger.info(f"Starting Boop application at {time.strftime('%H:%M:%S.%f')}")
    
    # Get config path - use user data directory for saved config
    # Get user data directory
    user_data_dir = get_user_data_dir()
    logger.info(f"Got user data directory in {time.time() - start_time:.3f}s")
    
    # Config path in user data directory
    config_path = user_data_dir / "config.json"
    logger.info(f"Config path: {config_path}")
    
    # Load configuration
    config = BoopConfig.from_file(config_path)
    logger.info(f"Configuration loaded: {config} in {time.time() - start_time:.3f}s")
    
    # Update script directories with default directory and remove duplicates
    logger.info(f"Current script directories: {config.script_directories}")
    config.script_directories = update_script_directories(config.script_directories)
    logger.info(f"Updated script directories: {config.script_directories}")
    
    # Check if Python path is set and exists
    python_path_valid = False
    if config.python_path:
        import os
        python_path_valid = os.path.exists(config.python_path) and os.access(config.python_path, os.X_OK)
        logger.info(f"Python path: {config.python_path}, valid: {python_path_valid}")
    else:
        logger.warning("Python path is not set")
    
    if not config.python_path or not python_path_valid:
        import tkinter as tk
        from tkinter import messagebox
        
        # Create a temporary root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Show Python path prompt
        messagebox.showinfo(
            "Python Environment Setup",
            "Python interpreter path is not set or does not exist. Please go to Preferences > Scripts to set the Python path."
        )
        logger.info("Python path not set, showed setup prompt")
        
        # Destroy the temporary root
        root.destroy()
    
    # Save config if it doesn't exist
    if not config_path.exists():
        config.save(config_path)
        logger.info(f"Saved configuration to: {config_path}")
    
    # Start the application
    logger.info(f"Starting MainWindow in {time.time() - start_time:.3f}s")
    app = MainWindow(config)
    logger.info(f"MainWindow initialized in {time.time() - start_time:.3f}s")
    app.run()
    logger.info(f"Application exited in {time.time() - start_time:.3f}s")


if __name__ == "__main__":
    main()
