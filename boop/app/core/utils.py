"""
Utility Functions - Common utility functions for the application
"""

import sys
import subprocess
import json
from typing import Any, Dict, Optional
from pathlib import Path

def run_script_in_subprocess(script_path: Path, input_text: str, python_path: str = "", timeout: int = 5) -> Dict[str, Any]:
    """Run a script in a subprocess.
    
    Args:
        script_path: Path to the script file
        input_text: Input text for the script
        python_path: Path to Python interpreter (optional)
        timeout: Timeout in seconds (optional)
        
    Returns:
        Dictionary with execution results
    """
    try:
        # Use specified Python or default
        python_exe = python_path
        if not python_exe:
            # For PyInstaller bundled apps, use the internal Python environment first
            if hasattr(sys, '_MEIPASS'):
                import os
                # Check internal Python environment first
                internal_python = os.path.join(sys._MEIPASS, "python_env", "bin", "python3")
                if os.path.exists(internal_python):
                    python_exe = internal_python
                else:
                    # Try to find Python in common locations
                    possible_pythons = [
                        '/usr/bin/python3',
                        '/usr/local/bin/python3',
                        os.path.expanduser('~/miniconda3/envs/python39/bin/python3'),
                        os.path.expanduser('~/miniconda3/bin/python3'),
                        os.path.expanduser('~/anaconda3/bin/python3'),
                    ]
                    for python in possible_pythons:
                        if os.path.exists(python):
                            python_exe = python
                            break
            # Fall back to sys.executable if no other options
            if not python_exe:
                python_exe = sys.executable
        
        # Get the path to the script wrapper
        import os
        # Handle PyInstaller bundled app
        if hasattr(sys, '_MEIPASS'):
            # In bundled app, the script_wrapper.py is in the same directory as the executable
            wrapper_script = os.path.join(sys._MEIPASS, 'app', 'core', 'script_wrapper.py')
        else:
            # In development mode, use relative path
            wrapper_script = os.path.join(os.path.dirname(__file__), 'script_wrapper.py')
        
        # Run the wrapper script
        process = subprocess.Popen(
            [python_exe, wrapper_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send script path followed by input text
        input_data = f"{str(script_path)}\n{input_text}"
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)  # Use provided timeout
        
        # Parse the result
        try:
            result = json.loads(stdout)
            result['stderr'] = stderr
        except json.JSONDecodeError:
            result = {
                'success': False,
                'output': input_text,
                'error': f"Script execution failed: {stderr}",
                'stderr': stderr
            }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'output': input_text,
            'error': str(e),
            'stderr': str(e)
        }


def center_window(window, width: int, height: int):
    """Center a Tkinter window on the screen.
    
    Args:
        window: Tkinter window object
        width: Window width
        height: Window height
    """
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def normalize_shortcut(shortcut):
    """Normalize shortcut string to standard format.
    
    Args:
        shortcut: Shortcut string (e.g., 'Control+b')
        
    Returns:
        Normalized shortcut string
    """
    # Convert to consistent format
    normalized = shortcut.strip()
    # Replace common variations
    normalized = normalized.replace('Ctrl', 'Control')
    normalized = normalized.replace('Cmd', 'Command')
    return normalized

def get_tk_shortcut(shortcut):
    """Convert shortcut string to Tkinter binding format.
    
    Args:
        shortcut: Shortcut string (e.g., 'Control+b')
        
    Returns:
        Tkinter-compatible shortcut string
    """
    normalized = normalize_shortcut(shortcut)
    return normalized.replace('+', '-')

def parse_hotkey_for_pynput(hotkey):
    """Parse hotkey string to pynput key set.
    
    Args:
        hotkey: Hotkey string (e.g., 'Control+b')
        
    Returns:
        Set of pynput key objects or None if parsing fails
    """
    try:
        from pynput import keyboard
        
        # Normalize the shortcut string first
        normalized_hotkey = normalize_shortcut(hotkey)
        parts = normalized_hotkey.split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            if part == 'Command':
                keys.add(keyboard.Key.cmd)
            elif part == 'Control':
                keys.add(keyboard.Key.ctrl)
            elif part == 'Shift':
                keys.add(keyboard.Key.shift)
            elif part == 'Alt':
                keys.add(keyboard.Key.alt)
            elif len(part) == 1:
                keys.add(part.lower())
            else:
                # Handle special keys
                key_map = {
                    'Enter': keyboard.Key.enter,
                    'Esc': keyboard.Key.esc,
                    'Tab': keyboard.Key.tab,
                    'Space': keyboard.Key.space,
                    'Up': keyboard.Key.up,
                    'Down': keyboard.Key.down,
                    'Left': keyboard.Key.left,
                    'Right': keyboard.Key.right,
                    'Home': keyboard.Key.home,
                    'End': keyboard.Key.end,
                    'PageUp': keyboard.Key.page_up,
                    'PageDown': keyboard.Key.page_down,
                }
                if part in key_map:
                    keys.add(key_map[part])
                else:
                    from app.core.log import logger
                    logger.warning(f"Unknown key: {part}")
                    return None
        
        return keys
    except Exception as e:
        from app.core.log import logger
        logger.error(f"Error parsing hotkey {hotkey}: {e}")
        return None

def binding_hotkey_action(widget, shortcuts, action):
    """Bind hotkey action to multiple shortcuts.
    
    Args:
        widget: Tkinter widget to bind the shortcuts to
        shortcuts: List of shortcut strings (e.g., ['Ctrl+z', 'Command+z'])
        action: Function to call when the shortcut is pressed
    """
    for shortcut in shortcuts:
        # Convert shortcut strings to Tkinter binding format
        tk_shortcut = get_tk_shortcut(shortcut)
        widget.bind(f'<{tk_shortcut}>', action)
        # Bind reverse order for three-part shortcuts (e.g. Ctrl+Shift+z)
        parts = shortcut.split('+')
        if parts and len(parts) == 3:
            # Convert each part for Tkinter compatibility
            part0 = normalize_shortcut(parts[0])
            part1 = normalize_shortcut(parts[1])
            part2 = normalize_shortcut(parts[2])
            widget.bind(f'<{part1}-{part0}-{part2}>', action)
        elif parts and len(parts) == 4:
            # Convert each part for Tkinter compatibility
            part0 = normalize_shortcut(parts[0])
            part1 = normalize_shortcut(parts[1])
            part2 = normalize_shortcut(parts[2])
            part3 = normalize_shortcut(parts[3])
            widget.bind(f'<{part0}-{part2}-{part1}-{part3}>', action)
            widget.bind(f'<{part1}-{part0}-{part2}-{part3}>', action)
            widget.bind(f'<{part2}-{part0}-{part1}-{part3}>', action)
            widget.bind(f'<{part2}-{part1}-{part0}-{part3}>', action)
            widget.bind(f'<{part1}-{part2}-{part0}-{part3}>', action)


def get_clipboard_content():
    """获取剪贴板内容。
    
    Returns:
        str: 剪贴板内容，如果无法获取或为空则返回空字符串
    """
    try:
        import pyperclip
        
        # 使用 pyperclip 库获取剪贴板内容
        clipboard_content = pyperclip.paste()
        
        # 检查内容是否为空或只包含空白字符
        if clipboard_content and clipboard_content.strip():
            return clipboard_content.strip()
        else:
            return ""
            
    except Exception as e:
        # 其他异常，记录错误
        from app.core.log import logger
        logger.warning("Error accessing clipboard content: %s" % e)
        return ""
