"""
Configuration Settings - Manage application configuration
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from boop.core.logging import logger


# Get default shortcuts based on platform
def _get_default_shortcuts():
    """Get default shortcuts based on platform."""
    import sys
    is_mac = sys.platform == 'darwin'
    
    if is_mac:
        return {
            'quit': ['Command+q'],
            'run_script': ['Command+b'],
            'preferences': ['Command+,'],
            'undo': ['Command+z'],
            'redo': ['Command+Shift+Z', 'Command+y'],
            'cut': ['Command+x'],
            'copy': ['Command+c'],
            'paste': ['Command+v'],
            'select_all': ['Command+a'],
            'select_next_occurrence': ['Command+d'],
            'stop_multi_edit': ['Escape'],
            'move_to_start': ['Command+Up'],
            'move_to_end': ['Command+Down']
        }
    else:
        return {
            'quit': ['Control+q'],
            'run_script': ['Control+b'],
            'preferences': ['Control+,'],
            'undo': ['Control+z'],
            'redo': ['Control+Shift+Z', 'Control+y'],
            'cut': ['Control+x'],
            'copy': ['Control+c'],
            'paste': ['Control+v'],
            'select_all': ['Control+a'],
            'select_next_occurrence': ['Control+d'],
            'stop_multi_edit': ['Escape'],
            'move_to_start': ['Control+Home'],
            'move_to_end': ['Control+End']
        }

@dataclass
class BoopConfig:
    """Application configuration class."""
    
    script_directories: List[str] = field(default_factory=list)
    python_path: str = ""
    default_encoding: str = "utf-8"
    window_width: int = 800
    window_height: int = 600
    maximize_window: bool = False
    font_family: str = "Menlo"
    font_size: int = 14
    theme: str = "system"
    script_timeout: int = 5
    filter_delay: int = 200
    shortcuts: dict = field(default_factory=_get_default_shortcuts)
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'BoopConfig':
        """Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            BoopConfig object
        """
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                logger.error(f"Error loading config: {e}", exc_info=True)
        return cls()
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file.

        Args:
            config_path: Path to configuration file
        """
        try:
            # Create a copy of the dict and remove shortcuts
            config_data = self.__dict__.copy()
            if 'shortcuts' in config_data:
                del config_data['shortcuts']

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}", exc_info=True)
