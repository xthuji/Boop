"""
Global Hotkey Manager - Handle global system-wide hotkeys
"""

import threading
from pynput import keyboard
from typing import Optional, Callable
from boop.core.log import logger
from boop.core.shortcut_manager import shortcut_manager


class GlobalHotkeyManager:
    """Manage global system-wide hotkeys."""
    
    def __init__(self):
        """Initialize the global hotkey manager."""
        self.listener = None
        self.hotkey_map = {}
        self.is_running = False
        self.listener_thread = None
        self.main_window = None
    
    def set_main_window(self, main_window):
        """Set the main window reference.
        
        Args:
            main_window: Reference to the main application window
        """
        self.main_window = main_window
    
    def register_hotkey(self, hotkey: str, callback: Callable):
        """Register a global hotkey.
        
        Args:
            hotkey: Hotkey string (e.g., 'Control+b')
            callback: Function to call when hotkey is pressed
        """
        # Convert hotkey string to pynput format
        key_combo = shortcut_manager.parse_hotkey_for_pynput(hotkey)
        if key_combo:
            self.hotkey_map[hotkey] = (key_combo, callback)
            logger.info(f"Registered global hotkey: {hotkey}")
    
    def unregister_hotkey(self, hotkey: str):
        """Unregister a global hotkey.
        
        Args:
            hotkey: Hotkey string to unregister
        """
        if hotkey in self.hotkey_map:
            del self.hotkey_map[hotkey]
            logger.info(f"Unregistered global hotkey: {hotkey}")
    
    def start(self):
        """Start the global hotkey listener."""
        if not self.is_running:
            self.is_running = True
            self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
            self.listener_thread.start()
            logger.info("Global hotkey listener started")
    
    def stop(self):
        """Stop the global hotkey listener."""
        if self.is_running:
            self.is_running = False
            if self.listener:
                self.listener.stop()
            if self.listener_thread:
                self.listener_thread.join(timeout=1.0)
            logger.info("Global hotkey listener stopped")
    
    def _run_listener(self):
        """Run the hotkey listener in a separate thread."""
        current_keys = set()
        
        def on_press(key):
            """Handle key press events."""
            try:
                # Add key to current keys
                if hasattr(key, 'char') and key.char:
                    current_keys.add(key.char.lower())
                else:
                    current_keys.add(key)
                
                # Check if any hotkey combination is matched
                for hotkey, (key_combo, callback) in self.hotkey_map.items():
                    if key_combo.issubset(current_keys):
                        # Execute callback in the main thread
                        if self.main_window and hasattr(self.main_window, 'root'):
                            self.main_window.root.after(0, callback)
                        else:
                            callback()
                        # Clear current keys to prevent repeated triggers
                        current_keys.clear()
            except Exception as e:
                logger.error(f"Error in key press handler: {e}")
        
        def on_release(key):
            """Handle key release events."""
            try:
                # Remove key from current keys
                if hasattr(key, 'char') and key.char:
                    if key.char.lower() in current_keys:
                        current_keys.remove(key.char.lower())
                else:
                    if key in current_keys:
                        current_keys.remove(key)
            except Exception as e:
                logger.error(f"Error in key release handler: {e}")
        
        # Start the listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self.listener = listener
            listener.join()


# Create a global instance
global_hotkey_manager = GlobalHotkeyManager()