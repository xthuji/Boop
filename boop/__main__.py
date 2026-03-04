"""
Boop Python - Application entry point
"""

import sys
from pathlib import Path

from boop.config.settings import BoopConfig
from boop.ui.main import MainWindow


def main():
    """Main function to start the application."""
    # Get config path
    config_path = Path(__file__).parent.parent / "config.json"
    
    # Load configuration
    config = BoopConfig.from_file(config_path)
    
    # Add default script directory if not present
    # Get the directory where the current file is located
    current_dir = Path(__file__).parent
    # The scripts directory should be in the same directory as this file
    default_script_dir = current_dir / "scripts"
    print(f"Current directory: {current_dir}")
    print(f"Default script directory: {default_script_dir}")
    print(f"Default script directory exists: {default_script_dir.exists()}")
    
    # Also check if we're in a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        # We're in a PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        print(f"PyInstaller bundle directory: {bundle_dir}")
        # Check for scripts directory in the bundle
        bundle_script_dir = bundle_dir / "boop" / "scripts"
        print(f"Bundle script directory: {bundle_script_dir}")
        print(f"Bundle script directory exists: {bundle_script_dir.exists()}")
        if bundle_script_dir.exists() and str(bundle_script_dir) not in config.script_directories:
            config.script_directories.append(str(bundle_script_dir))
        
        # Set internal Python environment path
        internal_python = bundle_dir / "python_env" / "bin" / "python3"
        if internal_python.exists():
            print(f"Found internal Python environment: {internal_python}")
            config.python_path = str(internal_python)
    
    if str(default_script_dir) not in config.script_directories:
        config.script_directories.append(str(default_script_dir))
    print(f"Script directories: {config.script_directories}")
    
    # Save config if it doesn't exist
    if not config_path.exists():
        config.save(config_path)
    
    # Start the application
    app = MainWindow(config)
    app.run()


if __name__ == "__main__":
    main()
