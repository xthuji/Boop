"""
Main Window - Application main window and entry point
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from boop.config.settings import BoopConfig
from boop.core.script import ScriptManager, LoadedScript
from boop.core.utils import run_script_in_subprocess
from boop.core.event import event_system
from boop.ui.editor import Editor
from boop.ui.script_picker import ScriptPickerPopup


class MainWindow:
    """Main application window."""
    
    def __init__(self, config: BoopConfig):
        """Initialize the main window.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.root = tk.Tk()
        self.root.title("Boop Python")
        self.root.geometry(f"{config.window_width}x{config.window_height}")
        
        self.script_manager = ScriptManager(config)
        self.editor: Optional[Editor] = None
        self.status_var = tk.StringVar(value="Ready")
        
        self._create_ui()
        self._bind_events()
        self._load_scripts()
    
    def _create_ui(self):
        """Create the main window UI."""
        # Determine platform-specific modifiers
        import sys
        is_mac = sys.platform == 'darwin'
        
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self._new_file, accelerator=self._get_accelerator("new_file"))
        file_menu.add_command(label="Open...", command=self._open_file, accelerator=self._get_accelerator("open_file"))
        file_menu.add_command(label="Save", command=self._save_file, accelerator=self._get_accelerator("save_file"))
        file_menu.add_command(label="Save As...", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._quit, accelerator=self._get_accelerator("quit"))
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator=self._get_accelerator("undo"))
        edit_menu.add_command(label="Redo", command=self._redo, accelerator=self._get_accelerator("redo"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._cut, accelerator=self._get_accelerator("cut"))
        edit_menu.add_command(label="Copy", command=self._copy, accelerator=self._get_accelerator("copy"))
        edit_menu.add_command(label="Paste", command=self._paste, accelerator=self._get_accelerator("paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self._select_all, accelerator=self._get_accelerator("select_all"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Previous Script Result", command=self._navigate_history_previous, accelerator=self._get_accelerator("navigate_previous"))
        edit_menu.add_command(label="Next Script Result", command=self._navigate_history_next, accelerator=self._get_accelerator("navigate_next"))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Scripts menu
        scripts_menu = tk.Menu(menubar, tearoff=0)
        scripts_menu.add_command(label="Run Script...", command=self._open_script_picker, accelerator=self._get_accelerator("run_script"))
        scripts_menu.add_command(label="Reload Scripts", command=self._load_scripts)
        menubar.add_cascade(label="Scripts", menu=scripts_menu)
        
        # Preferences menu
        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_command(label="Preferences...", command=self._open_preferences, accelerator=self._get_accelerator("preferences"))
        menubar.add_cascade(label="Preferences", menu=preferences_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Editor
        self.editor = Editor(main_frame, self.config)
        
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
        
        # Convert Command to Cmd for display purposes on macOS
        import sys
        is_mac = sys.platform == 'darwin'
        if is_mac:
            return shortcut.replace('Command+', 'Cmd+')
        return shortcut
    
    def _bind_events(self):
        """Bind keyboard and mouse events."""

        def binding_hotkey_action(shortcuts, action):
            """Bind hotkey action to multiple shortcuts."""
            for shortcut in shortcuts:
                # Convert shortcut strings to Tkinter binding format
                self.root.bind(f'<{shortcut.replace("+", "-")}>', action)
        
        # Bind shortcuts
        binding_hotkey_action(self.config.shortcuts.get('new_file', ['Ctrl+n']), lambda e: self._new_file())
        binding_hotkey_action(self.config.shortcuts.get('open_file', ['Ctrl+o']), lambda e: self._open_file())
        binding_hotkey_action(self.config.shortcuts.get('save_file', ['Ctrl+s']), lambda e: self._save_file())
        binding_hotkey_action(self.config.shortcuts.get('quit', ['Ctrl+q']), lambda e: self._quit())
        binding_hotkey_action(self.config.shortcuts.get('run_script', ['Ctrl+b']), lambda e: self._open_script_picker())
        binding_hotkey_action(self.config.shortcuts.get('preferences', ['Ctrl+,']), lambda e: self._open_preferences())
        binding_hotkey_action(self.config.shortcuts.get('navigate_previous', ['Ctrl+Left']), lambda e: self._navigate_history_previous())
        binding_hotkey_action(self.config.shortcuts.get('navigate_next', ['Ctrl+Right']), lambda e: self._navigate_history_next())
        
        # Editor events
        if self.editor:
            self.editor._text_widget.bind('<KeyRelease>', self._update_status)
            self.editor._text_widget.bind('<ButtonRelease>', self._update_status)
        
        # Event system subscriptions
        event_system.subscribe('scripts_loaded', self._on_scripts_loaded)
        event_system.subscribe('script_execution_started', self._on_script_execution_started)
        event_system.subscribe('script_execution_completed', self._on_script_execution_completed)
    
    def _update_status(self, event=None):
        """Update status bar information."""
        if self.editor:
            line, col = self.editor.get_cursor_position()
            self.cursor_var.set(f"Ln {line}, Col {col}")
            self.char_count_var.set(f"{self.editor.get_char_count()} chars")
    
    def _load_scripts(self):
        """Load scripts from configured directories."""
        self.status_var.set("Loading scripts...")
        count = self.script_manager.load_scripts()
        self.status_var.set(f"Loaded {count} scripts")
    
    def _open_script_picker(self):
        """Open script picker popup."""
        if self.editor:
            ScriptPickerPopup(
                self.root,
                self.script_manager,
                self._execute_script,
                self.editor._text_widget
            )
    
    def _execute_script(self, script: Optional[LoadedScript]):
        """Execute a script on the current text.
        
        Args:
            script: Script to execute
        """
        if not script:
            return
        
        if not self.editor:
            return
        
        # Check for help mode
        content = self.editor.get_content()
        if content.startswith('-h'):
            # Show help information
            self._show_script_help(script)
            return
        
        # Record script execution start
        self.editor.record_script_execution(script.metadata.name)
        
        # Execute script
        self.status_var.set(f"Executing script: {script.metadata.name}")
        event_system.publish('script_execution_started', script_name=script.metadata.name)
        
        # Run script in subprocess
        result = run_script_in_subprocess(
            script.file_path,
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
            self.status_var.set(f"Script executed successfully: {script.metadata.name}")
        else:
            error_msg = result['error'] or 'Unknown error'
            messagebox.showerror("Script Error", f"Error executing script: {error_msg}")
            self.status_var.set(f"Script execution failed: {script.metadata.name}")
        
        event_system.publish(
            'script_execution_completed',
            script_name=script.metadata.name,
            success=result['success'],
            error=result['error']
        )
    
    def _show_script_help(self, script: LoadedScript):
        """Show script help information.
        
        Args:
            script: Script to show help for
        """
        if not self.editor:
            return
        
        content = self.editor.get_content()
        lines = content.split('\n')
        
        # Extract the part after -h
        if len(lines) > 1:
            body = '\n'.join(lines[1:])
        else:
            body = ''
        
        # Create help content
        help_content = f"-h\n\n{script.metadata.help}\n\n{body}"
        self.editor.set_content(help_content)
        self.status_var.set(f"Showing help for: {script.metadata.name}")
    
    def _new_file(self):
        """Create a new file."""
        if self.editor:
            if messagebox.askyesno("New File", "Are you sure you want to create a new file? Unsaved changes will be lost."):
                self.editor.clear()
                self.status_var.set("Ready")
    
    def _open_file(self):
        """Open a file."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if self.editor:
                    self.editor.set_content(content)
                self.status_var.set(f"Opened: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def _save_file(self):
        """Save the current file."""
        # For now, just show a message
        messagebox.showinfo("Save", "Save functionality not yet implemented")
    
    def _save_as_file(self):
        """Save the current file as a new file."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                if self.editor:
                    content = self.editor.get_content()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                self.status_var.set(f"Saved: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def _undo(self):
        """Undo last action."""
        if self.editor:
            self.editor._text_widget.event_generate('<<Undo>>')
    
    def _redo(self):
        """Redo last action."""
        if self.editor:
            self.editor._text_widget.event_generate('<<Redo>>')
    
    def _cut(self):
        """Cut selected text."""
        if self.editor:
            self.editor._text_widget.event_generate('<<Cut>>')
    
    def _copy(self):
        """Copy selected text."""
        if self.editor:
            self.editor._text_widget.event_generate('<<Copy>>')
    
    def _paste(self):
        """Paste text from clipboard."""
        if self.editor:
            self.editor._text_widget.event_generate('<<Paste>>')
    
    def _select_all(self):
        """Select all text."""
        if self.editor:
            self.editor._text_widget.tag_add(tk.SEL, '1.0', tk.END)
    
    def _navigate_history_previous(self):
        """Navigate to previous script execution result."""
        if self.editor:
            if self.editor.navigate_history(-1):
                self.status_var.set("Navigated to previous script result")
            else:
                self.status_var.set("No previous script result")
    
    def _navigate_history_next(self):
        """Navigate to next script execution result."""
        if self.editor:
            if self.editor.navigate_history(1):
                self.status_var.set("Navigated to next script result")
            else:
                self.status_var.set("No next script result")
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Boop Python",
            "Boop Python\nVersion 1.0.0\n\nA text processing tool inspired by Boop macOS app."
        )
    
    def _open_preferences(self):
        """Open preferences panel."""
        from boop.ui.preferences import PreferencesPanel
        PreferencesPanel(self.root, self.config)
    
    def _quit(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()
    
    def _on_scripts_loaded(self, count: int):
        """Handle scripts loaded event."""
        self.status_var.set(f"Loaded {count} scripts")
    
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
