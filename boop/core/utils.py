"""
Utility Functions - Common utility functions for the application
"""

import sys
import subprocess
import json
from typing import Any, Dict, Optional
from pathlib import Path


def run_script_in_subprocess(script_path: Path, input_text: str, python_path: str = "") -> Dict[str, Any]:
    """Run a script in a subprocess.
    
    Args:
        script_path: Path to the script file
        input_text: Input text for the script
        python_path: Path to Python interpreter (optional)
        
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
        
        # Create a wrapper to execute the script
        script_path_str = str(script_path)
        wrapper_code = """
import sys
import json
import os

# Add script directory to path
sys.path.insert(0, os.path.dirname('{0}'))

# Read input from stdin
input_text = sys.stdin.read()

class ScriptExecution:
    def __init__(self, text):
        self.text = text
        self.full_text = text
        self.selection = text
    
    def insert(self, text):
        self.text = text
    
    def post_info(self, msg):
        print("INFO: " + msg, file=sys.stderr)
    
    def post_error(self, msg):
        print("ERROR: " + msg, file=sys.stderr)

# Load and run the script
try:
    # Read the script file
    with open('{0}', 'r') as f:
        script_code = f.read()
    
    # Create a namespace for the script
    script_namespace = {{
        '__file__': '{0}',
        '__name__': 'script_module'
    }}
    
    # Execute the script
    exec(script_code, script_namespace)
    
    # Get the main function
    main_func = script_namespace.get('main')
    if not main_func:
        raise Exception('No main function found in script')
    
    # Run the script
    state = ScriptExecution(input_text)
    main_func(state)
    result = {{
        'success': True,
        'output': state.text,
        'error': ''
    }}
except Exception as e:
    import traceback
    result = {{
        'success': False,
        'output': input_text,
        'error': str(e) + '\\n' + traceback.format_exc()
    }}

# Output result as JSON
print(json.dumps(result))
""".format(script_path_str)
        
        # Run the wrapper in a subprocess
        process = subprocess.Popen(
            [python_exe, '-c', wrapper_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=input_text, timeout=30)  # 30 second timeout
        
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


def get_icon_path(icon_name: str) -> Optional[Path]:
    """Get the path to an icon file.
    
    Args:
        icon_name: Name of the icon
        
    Returns:
        Path to the icon file or None if not found
    """
    icon_dir = Path(__file__).parent.parent / "ui" / "icons"
    icon_path = icon_dir / f"{icon_name}.png"
    
    if icon_path.exists():
        return icon_path
    
    # Fallback to unknown icon
    unknown_icon = icon_dir / "unknown.png"
    if unknown_icon.exists():
        return unknown_icon
    
    return None
