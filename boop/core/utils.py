"""
Utility Functions - Common utility functions for the application
"""

import sys
import subprocess
import json
from typing import Any, Dict, Optional
from pathlib import Path

def run_script_in_subprocess_worker(script_path: Path, input_text: str, python_path: str = "") -> Dict[str, Any]:
    """Run a script in a subprocess (worker function)."""
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
            wrapper_script = os.path.join(sys._MEIPASS, 'boop', 'core', 'script_wrapper.py')
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
        stdout, stderr = process.communicate(input=input_data, timeout=30)  # 30 second timeout
        
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

def run_script_in_subprocess(script_path: Path, input_text: str, python_path: str = "") -> Dict[str, Any]:
    """Run a script in a subprocess.
    
    Args:
        script_path: Path to the script file
        input_text: Input text for the script
        python_path: Path to Python interpreter (optional)
        
    Returns:
        Dictionary with execution results
    """
    # Use direct execution
    return run_script_in_subprocess_worker(script_path, input_text, python_path)


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
