#!/usr/bin/env python3
"""
Script Wrapper - Executes scripts with proper context
"""

import sys
import json
import os

# Read script path from stdin
script_path = sys.stdin.readline().strip()
# Read input text
input_text = sys.stdin.read()

# Add script directory to path
sys.path.insert(0, os.path.dirname(script_path))

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
    with open(script_path, 'r') as f:
        script_code = f.read()
    
    # Create a namespace for the script
    script_namespace = {
        '__file__': script_path,
        '__name__': 'script_module'
    }
    
    # Execute the script
    exec(script_code, script_namespace)
    
    # Get the main function
    main_func = script_namespace.get('main')
    if not main_func:
        raise Exception('No main function found in script')
    
    # Run the script
    state = ScriptExecution(input_text)
    main_func(state)
    result = {
        'success': True,
        'output': state.text,
        'error': ''
    }
except Exception as e:
    import traceback
    result = {
        'success': False,
        'output': input_text,
        'error': str(e) + '\n' + traceback.format_exc()
    }

# Output result as JSON
print(json.dumps(result))
