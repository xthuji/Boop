"""
Configuration Settings - Manage application configuration
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


# Get default shortcuts based on platform
def _get_default_shortcuts():
    """Get default shortcuts based on platform."""
    import sys
    is_mac = sys.platform == 'darwin'
    
    if is_mac:
        return {
            'new_file': ['Command+n'],
            'open_file': ['Command+o'],
            'save_file': ['Command+s'],
            'quit': ['Command+q'],
            'run_script': ['Command+b'],
            'preferences': ['Command+,'],
            'undo': ['Command+z'],
            'redo': ['Command+Shift+Z', 'Command+y'],
            'cut': ['Command+x'],
            'copy': ['Command+c'],
            'paste': ['Command+v'],
            'select_all': ['Command+a'],
            'navigate_previous': ['Command+Left'],
            'navigate_next': ['Command+Right']
        }
    else:
        return {
            'new_file': ['Control+n'],
            'open_file': ['Control+o'],
            'save_file': ['Control+s'],
            'quit': ['Control+q'],
            'run_script': ['Control+b'],
            'preferences': ['Control+,'],
            'undo': ['Control+z'],
            'redo': ['Control+Shift+Z', 'Control+y'],
            'cut': ['Control+x'],
            'copy': ['Control+c'],
            'paste': ['Control+v'],
            'select_all': ['Control+a'],
            'navigate_previous': ['Control+Left'],
            'navigate_next': ['Control+Right']
        }

@dataclass
class BoopConfig:
    """Application configuration class."""
    
    script_directories: List[str] = field(default_factory=lambda: ["scripts"])
    python_path: str = ""
    default_encoding: str = "utf-8"
    window_width: int = 800
    window_height: int = 600
    font_family: str = "Menlo"
    font_size: int = 14
    theme: str = "system"
    script_timeout: int = 30
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
                print(f"Error loading config: {e}")
        return cls()
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
