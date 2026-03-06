"""
Main Window - Application main window and entry point
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from boop.config.settings import BoopConfig
from boop.core.script import ScriptManager
from boop.core.utils import run_script_in_subprocess, center_window, binding_hotkey_action
from boop.core.event import event_system
from boop.core.logging import logger
from boop.ui.editor import Editor
from boop.ui.script_picker import ScriptPickerPopup


class MainWindow:
    """Main application window."""
    
    def __init__(self, config: BoopConfig):
        """Initialize the main window.
        
        Args:
            config: Application configuration
        """
        import time
        self.init_start_time = time.time()
        logger.info(f"Initializing MainWindow at {time.strftime('%H:%M:%S.%f')}")
        self.config = config
        self.root = tk.Tk()
        self.root.title("Boop Python")
        
        # Maximize window if configured
        if hasattr(config, 'maximize_window') and config.maximize_window:
            import sys
            platform = sys.platform
            
            try:
                # Try platform-specific maximize
                if platform == 'win32':  # Windows
                    self.root.state('zoomed')
                    logger.info("Window maximized (Windows)")
                elif platform == 'linux':  # Linux
                    try:
                        self.root.attributes('-zoomed', True)
                        logger.info("Window maximized (Linux)")
                    except Exception:
                        # Fallback to setting full screen size
                        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
                        logger.info("Using fallback maximize for Linux")
                else:  # macOS and other platforms
                    # For macOS, set window to full screen size
                    self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
                    logger.info("Window maximized (macOS)")
            except Exception as e:
                # If maximizing fails, just log the error and continue
                logger.error(f"Failed to maximize window: {e}")
                # Fallback to centered window with user-specified size
                center_window(self.root, config.window_width, config.window_height)
                self.root.state('normal')
        else:
            # Center window with user-specified size
            center_window(self.root, config.window_width, config.window_height)
            logger.info(f"Window created with size: {config.window_width}x{config.window_height}, centered")
        
        logger.info(f"Window created in {time.time() - self.init_start_time:.3f}s")
        
        self.script_manager = ScriptManager(config)
        logger.info(f"ScriptManager created in {time.time() - self.init_start_time:.3f}s")
        
        self.status_var = tk.StringVar(value="Ready")
        
        self._create_ui()
        logger.info(f"UI created in {time.time() - self.init_start_time:.3f}s")
        
        self._bind_events()
        logger.info(f"Events bound in {time.time() - self.init_start_time:.3f}s")
        
        # Don't load scripts at startup - load on demand
        logger.info(f"Startup completed in {time.time() - self.init_start_time:.3f}s")
        
        # Load script metadata in background after startup
        self.root.after(1000, self._load_script_metadata)
    
    def _create_ui(self):
        """Create the main window UI."""        
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: self.editor._undo(None), accelerator=self._get_accelerator("undo"))
        edit_menu.add_command(label="Redo", command=lambda: self.editor._redo(None), accelerator=self._get_accelerator("redo"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.editor._cut(None), accelerator=self._get_accelerator("cut"))
        edit_menu.add_command(label="Copy", command=lambda: self.editor._copy(None), accelerator=self._get_accelerator("copy"))
        edit_menu.add_command(label="Paste", command=lambda: self.editor._paste(None), accelerator=self._get_accelerator("paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Move to Start", command=lambda: self.editor._move_to_start(None), accelerator=self._get_accelerator("move_to_start"))
        edit_menu.add_command(label="Move to End", command=lambda: self.editor._move_to_end(None), accelerator=self._get_accelerator("move_to_end"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=lambda: self.editor._select_all(None), accelerator=self._get_accelerator("select_all"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select Next Occurrence For MultiEdit", command=lambda: self.editor.select_next_occurrence(None), accelerator=self._get_accelerator("select_next_occurrence"))
        edit_menu.add_command(label="Stop MultiEdit", command=lambda: self.editor.extensions._clear_multi_cursor_state(), accelerator=self._get_accelerator("stop_multi_edit"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Script menu
        script_menu = tk.Menu(menubar, tearoff=0)
        script_menu.add_command(label="Run Script", command=self._open_script_picker, accelerator=self._get_accelerator("run_script"))
        script_menu.add_separator()
        script_menu.add_command(label="Refresh Script Metadata Cache", command=self._refresh_script_metadata_cache)
        menubar.add_cascade(label="Script", menu=script_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About Boop", command=self._show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Preferences", command=self._open_preferences, accelerator=self._get_accelerator("preferences"))
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Editor
        self.editor = Editor(main_frame, self.config)
        # Set focus to editor
        self.editor.focus()
        
        # Status bar
        status_bar = tk.Frame(self.root, height=20, relief=tk.SUNKEN, bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status label
        status_label = tk.Label(status_bar, textvariable=self.status_var, font=('TkDefaultFont', 9), anchor=tk.W)
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Cursor position
        self.cursor_var = tk.StringVar(value="Ln 1, Col 1")
        cursor_label = tk.Label(status_bar, textvariable=self.cursor_var, font=('TkDefaultFont', 9), anchor=tk.E)
        cursor_label.pack(side=tk.RIGHT, padx=10)
        
        # Character count
        self.char_count_var = tk.StringVar(value="0 chars")
        char_count_label = tk.Label(status_bar, textvariable=self.char_count_var, font=('TkDefaultFont', 9), anchor=tk.E)
        char_count_label.pack(side=tk.RIGHT, padx=10)
    
    def _get_accelerator(self, shortcut_name):
        """Get accelerator string for a shortcut.
        
        Args:
            shortcut_name: Name of the shortcut
            
        Returns:
            Accelerator string
        """
        # Get shortcut from config
        shortcut = self.config.shortcuts.get(shortcut_name, '')
        
        # Handle case where shortcut is a list
        if isinstance(shortcut, list) and shortcut:
            shortcut = shortcut[0]
        
        return shortcut
    
    def _bind_events(self):
        """Bind keyboard and mouse events."""
        
        # Bind shortcuts
        binding_hotkey_action(self.root, self.config.shortcuts.get('quit', ['Ctrl+q']), lambda e: self._quit())
        binding_hotkey_action(self.root, self.config.shortcuts.get('run_script', ['Ctrl+b']), lambda e: self._open_script_picker())
        binding_hotkey_action(self.root, self.config.shortcuts.get('preferences', ['Ctrl+,']), lambda e: self._open_preferences())
        binding_hotkey_action(self.root, self.config.shortcuts.get('move_to_start', ['Ctrl+Home']), lambda e: self.editor._move_to_start(None))
        binding_hotkey_action(self.root, self.config.shortcuts.get('move_to_end', ['Ctrl+End']), lambda e: self.editor._move_to_end(None))
        binding_hotkey_action(self.root, self.config.shortcuts.get('undo', ['Ctrl+z']), lambda e: self.editor._undo(None))
        binding_hotkey_action(self.root, self.config.shortcuts.get('redo', ['Ctrl+Shift+Z']), lambda e: self.editor._redo(None))
        # 系统自带的复制/粘贴/剪切等快捷键不用绑定，可能会冲突导致不可预期的行为
        
        # Editor events
        self.editor._text_widget.bind('<KeyRelease>', self._update_status)
        self.editor._text_widget.bind('<ButtonRelease>', self._update_status)
        
        # Event system subscriptions
        event_system.subscribe('script_execution_started', self._on_script_execution_started)
        event_system.subscribe('script_execution_completed', self._on_script_execution_completed)
    
    def _update_status(self, event=None):
        """Update status bar information."""
        line, col = self.editor.get_cursor_position()
        self.cursor_var.set(f"Ln {line}, Col {col}")
        self.char_count_var.set(f"{self.editor.get_char_count()} chars")
    

    
    def _load_script_metadata(self):
        """Load script metadata in background after startup."""
        import time
        start_time = time.time()
        logger.info(f"Starting to load script metadata at {time.strftime('%H:%M:%S.%f')}")
        
        try:
            # Use ScriptManager's load_metadata method
            total_scripts = self.script_manager.load_metadata()
            
            logger.info(f"Loaded metadata for {total_scripts} scripts in {time.time() - start_time:.3f}s")
            self.status_var.set(f"Loaded metadata for {total_scripts} scripts")
        except Exception as e:
            logger.error(f"Error loading script metadata: {e}")
            self.status_var.set("Error loading script metadata")
    
    def _open_script_picker(self):
        """Open script picker popup."""
        # Open script picker directly - no need to load scripts
        ScriptPickerPopup(
            self.root,
            self.script_manager,
            self._execute_script,
            self.editor._text_widget,
            self.config
        )
    
    def _execute_script(self, script_tuple: Optional[tuple]):
        """Execute a script on the current text.
        
        Args:
            script_tuple: Tuple of (ScriptMetadata, Path) to execute
        """
        if not script_tuple:
            return
        
        metadata, file_path = script_tuple
        
        # Check for help mode
        content = self.editor.get_content()
        if content.startswith('-h'):
            # Show help information
            self._show_script_help(metadata, file_path)
            return
        
        # Record script execution start
        self.editor.record_script_execution(metadata.name)
        
        # Execute script
        logger.info(f"Executing script: {metadata.name}")
        self.status_var.set(f"Executing script: {metadata.name}")
        event_system.publish('script_execution_started', script_name=metadata.name)
        
        # Run script in subprocess
        result = run_script_in_subprocess(
            file_path,
            content,
            self.config.python_path
        )
        
        if result['success']:
            # Update content using set_content
            # This will trigger <<Modified>> event, which will call _on_modified
            # _on_modified will then call _save_state to add the new state to history
            self.editor.set_content(result['output'])
            # Update script execution result in history
            self.editor.update_script_execution_result(result['output'])
            self.status_var.set(f"Script executed successfully: {metadata.name}")
            logger.info(f"Script executed successfully: {metadata.name}")
        else:
            error_msg = result['error'] or 'Unknown error'
            messagebox.showerror("Script Error", f"Error executing script: {error_msg}")
            self.status_var.set(f"Script execution failed: {metadata.name}")
            logger.error(f"Script execution failed: {metadata.name}, error: {error_msg}")
        
        event_system.publish(
            'script_execution_completed',
            script_name=metadata.name,
            success=result['success'],
            error=result['error']
        )
    
    def _show_script_help(self, metadata, file_path):
        """Show script help information.
        
        Args:
            metadata: Script metadata
            file_path: Path to the script file
        """
        content = self.editor.get_content()
        lines = content.split('\n')
        
        # Extract the part after -h
        if len(lines) > 1:
            body = '\n'.join(lines[1:])
        else:
            body = ''
        
        # Create help content
        help_content = f"-h\n\n{metadata.help}\n\n{body}"
        self.editor.set_content(help_content)
        self.status_var.set(f"Showing help for: {metadata.name}")
    
    
    def _show_about(self):
        """Show about dialog."""
        # Read version from version.txt file
        import re
        import sys
        version = "1.0.0"  # Default version
        
        # Try to find version.txt file in different locations
        # 1. In PyInstaller packaged app
        if hasattr(sys, '_MEIPASS'):
            version_file = Path(sys._MEIPASS) / "version.txt"
        # 2. In development environment
        else:
            version_file = Path(__file__).parent.parent.parent / "version.txt"
        
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    content = f.read()
                    version_match = re.search(r'VERSION = ([\d.]+)', content)
                    if version_match:
                        version = version_match.group(1)
            except Exception:
                pass
        
        messagebox.showinfo(
            "About Boop Python",
            f"Boop Python\nVersion {version}\n\nA text processing tool inspired by Boop macOS app."
        )
    
    def _open_preferences(self):
        """Open preferences panel."""
        logger.info("Opening preferences panel")
        from boop.ui.preferences import PreferencesPanel
        PreferencesPanel(self.root, self.config)

    def _refresh_script_metadata_cache(self):
        """Refresh script metadata cache."""
        logger.info("Refreshing script metadata cache")
        
        try:
            # Use the new refresh_metadata_cache method
            script_count = self.script_manager.refresh_metadata_cache()
            messagebox.showinfo("Success", f"Metadata cache refreshed successfully.\nLoaded {script_count} scripts.")
            self.status_var.set(f"Loaded metadata for {script_count} scripts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh metadata cache: {e}")
            logger.error(f"Failed to refresh metadata cache: {e}")
    
    def _quit(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()
    

    
    def _on_script_execution_started(self, script_name: str):
        """Handle script execution started event."""
        self.status_var.set(f"Executing script: {script_name}")
    
    def _on_script_execution_completed(self, script_name: str, success: bool, error: str):
        """Handle script execution completed event."""
        if success:
            self.status_var.set(f"Script executed successfully: {script_name}")
        else:
            self.status_var.set(f"Script execution failed: {script_name}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
