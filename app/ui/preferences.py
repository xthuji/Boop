"""
PreferencesPanel - Preferences configuration panel

This module implements a panel for configuring application preferences.
Uses tk.Toplevel for proper window management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from app.config.settings import BoopConfig
from app.core.log import logger
from app.core.utils import center_window
from app.core.path import get_log_path, get_user_data_dir


class PreferencesPanel:
    """Preferences configuration panel using Toplevel window."""

    def __init__(self, parent: tk.Tk, config: BoopConfig, editor=None):
        """Initialize the preferences panel.

        Args:
            parent: Parent window
            config: Application configuration
            editor: Editor instance for font updates (optional)
        """
        self.parent = parent
        self.config = config
        self.editor = editor
        self.dialog: Optional[tk.Toplevel] = None

        self._create_dialog()

    def _create_dialog(self):
        """Create the preferences dialog."""
        # Create Toplevel window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Preferences")
        self.dialog.transient(self.parent)
        self.dialog.resizable(True, True)

        # Set modern minimalist style
        style = ttk.Style()

        # Base colors for minimalist design
        bg_color = '#ffffff'
        fg_color = '#333333'
        accent_color = '#007aff'  # macOS blue for primary buttons
        cancel_color = '#f0f0f0'  # Light gray for cancel buttons
        hover_color = '#f5f5f5'

        # Configure styles
        style.configure('TNotebook', padding=0, background=bg_color)
        style.configure('TNotebook.Tab', padding=(16, 8), font=('SF Pro Text', 12),
                       background=bg_color, foreground=fg_color)
        style.map('TNotebook.Tab',
                  background=[('selected', bg_color), ('!selected', bg_color), ('active', hover_color)],
                  foreground=[('selected', accent_color), ('!selected', fg_color)])
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('SF Pro Text', 12), foreground=fg_color)

        # Cancel button style (gray)
        style.configure('Cancel.TButton', padding=(12, 6), font=('SF Pro Text', 12))
        style.map('Cancel.TButton',
                  background=[('!disabled', cancel_color), ('active', '#e0e0e0')],
                  foreground=[('!disabled', fg_color)])

        # Save button style - blue text, bold to highlight
        style.configure('Save.TButton', padding=(12, 6), font=('SF Pro Text', 12, 'bold'))
        style.map('Save.TButton',
                  foreground=[('!disabled', accent_color)])

        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', font=('SF Pro Text', 12, 'semibold'),
                       background=bg_color, foreground=fg_color)
        style.configure('TEntry', padding=(8, 6), font=('SF Pro Text', 12),
                       fieldbackground=bg_color, foreground=fg_color)
        
        # Center the dialog
        center_window(self.dialog, 700, 580)
        
        # Make dialog modal-like
        self.dialog.grab_set()
        self.dialog.focus_set()

        self._create_ui()
        self._bind_events()

    def _create_ui(self):
        """Create the preferences UI."""
        # Main container with minimalist background
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Notebook for different preference sections with minimalist styling
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # General settings tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        self._create_general_tab(general_frame)

        # Scripts tab
        scripts_frame = ttk.Frame(notebook)
        notebook.add(scripts_frame, text="Scripts")
        self._create_scripts_tab(scripts_frame)

        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        self._create_logs_tab(logs_frame)

        # Buttons with minimalist styling
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 0))

        # Cancel button (Esc key)
        cancel_btn = ttk.Button(button_frame, text="Cancel (Esc)", command=self._close, style='Cancel.TButton')
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Save button (Enter key) - same style as Cancel but with blue text
        save_btn = ttk.Button(button_frame, text="Save (Enter)", command=self._save, style='Save.TButton')
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def _create_general_tab(self, parent):
        """Create the general settings tab."""
        # Window settings with minimalist styling
        window_frame = ttk.LabelFrame(parent, text="Window", padding=(10, 5))
        window_frame.pack(fill=tk.X, padx=10, pady=5)

        # Global hotkeys option
        hotkeys_frame = ttk.Frame(window_frame)
        hotkeys_frame.pack(fill=tk.X, pady=5)
        self.enable_global_hotkeys_var = tk.BooleanVar(value=getattr(self.config, 'enable_global_hotkeys', False))
        hotkeys_checkbox = ttk.Checkbutton(
            hotkeys_frame, text="Enable Global Hotkeys Back To App",
            variable=self.enable_global_hotkeys_var
        )
        hotkeys_checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Maximize window option
        maximize_frame = ttk.Frame(window_frame)
        maximize_frame.pack(fill=tk.X, pady=5)
        self.maximize_var = tk.BooleanVar(value=getattr(self.config, 'maximize_window', False))
        maximize_checkbox = ttk.Checkbutton(
            maximize_frame, text="Maximize Window",
            variable=self.maximize_var, command=self._toggle_maximize
        )
        maximize_checkbox.pack(side=tk.LEFT, padx=(0, 10))

        # Window width
        width_frame = ttk.Frame(window_frame)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text="Window Width:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.width_var = tk.StringVar(value=str(self.config.window_width))
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var)
        self.width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Window height
        height_frame = ttk.Frame(window_frame)
        height_frame.pack(fill=tk.X, pady=5)
        ttk.Label(height_frame, text="Window Height:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.height_var = tk.StringVar(value=str(self.config.window_height))
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var)
        self.height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Initial toggle based on current value
        self._toggle_maximize()

        # Font settings with minimalist styling
        font_frame = ttk.LabelFrame(parent, text="Font", padding=(10, 5))
        font_frame.pack(fill=tk.X, padx=10, pady=5)

        # Font family
        font_family_frame = ttk.Frame(font_frame)
        font_family_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_family_frame, text="Font Family:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.font_family_var = tk.StringVar(value=self.config.font_family)
        font_family_entry = ttk.Entry(font_family_frame, textvariable=self.font_family_var)
        font_family_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Font size
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_size_frame, text="Font Size:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.font_size_var = tk.StringVar(value=str(self.config.font_size))
        font_size_entry = ttk.Entry(font_size_frame, textvariable=self.font_size_var)
        font_size_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _create_scripts_tab(self, parent):
        """Create the scripts settings tab."""
        # Script directories with minimalist styling
        dirs_frame = ttk.LabelFrame(parent, text="Script Directories", padding=(10, 5))
        dirs_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create a frame for listbox and scrollbar
        list_frame = ttk.Frame(dirs_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Listbox for script directories with minimalist styling
        self.dirs_listbox = tk.Listbox(list_frame, height=2, relief=tk.FLAT, borderwidth=1, bg='white', font=('SF Pro Text', 12))
        self.dirs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.dirs_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dirs_listbox.configure(yscrollcommand=scrollbar.set)

        # Add existing directories
        for directory in self.config.script_directories:
            self.dirs_listbox.insert(tk.END, directory)

        # Buttons with minimalist styling
        button_frame = ttk.Frame(dirs_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        add_button = ttk.Button( button_frame, text="Add", command=self._add_directory )
        add_button.pack(fill=tk.X, pady=3)

        remove_button = ttk.Button( button_frame, text="Remove", command=self._remove_directory )
        remove_button.pack(fill=tk.X, pady=3)

        # Python interpreter with minimalist styling
        python_frame = ttk.LabelFrame(parent, text="Python", padding=(10, 5))
        python_frame.pack(fill=tk.X, padx=10, pady=5)

        python_frame_row = ttk.Frame(python_frame)
        python_frame_row.pack(fill=tk.X, pady=5)
        ttk.Label(python_frame_row, text="Python Interpreter:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.python_var = tk.StringVar(value=self.config.python_path)
        python_entry = ttk.Entry(python_frame_row, textvariable=self.python_var)
        python_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Add browse button for Python interpreter
        browse_button = ttk.Button( python_frame_row, text="Browse", command=self._browse_python )
        browse_button.pack(side=tk.LEFT, padx=0)

        # Script timeout
        timeout_frame = ttk.Frame(python_frame)
        timeout_frame.pack(fill=tk.X, pady=5)
        ttk.Label(timeout_frame, text="Script Timeout (s):", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.timeout_var = tk.StringVar(value=str(self.config.script_timeout))
        timeout_entry = ttk.Entry(timeout_frame, textvariable=self.timeout_var)
        timeout_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Filter delay
        filter_delay_frame = ttk.Frame(python_frame)
        filter_delay_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_delay_frame, text="Filter Delay (ms):", width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.filter_delay_var = tk.StringVar(value=str(getattr(self.config, 'filter_delay', 200)))
        filter_delay_entry = ttk.Entry(filter_delay_frame, textvariable=self.filter_delay_var)
        filter_delay_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Dependencies management with minimalist styling
        dependencies_frame = ttk.LabelFrame(parent, text="Dependencies", padding=(10, 5))
        dependencies_frame.pack(fill=tk.X, padx=10, pady=5)

        # Dependencies list with dropdown
        dep_list_frame = ttk.Frame(dependencies_frame)
        dep_list_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dep_list_frame, text="Script Dependencies:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # Create a dropdown list for dependencies
        self.dep_var = tk.StringVar(value="Click to view dependencies")
        dep_dropdown = ttk.Combobox( dep_list_frame, textvariable=self.dep_var, state="readonly" )
        dep_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        # Install dependencies button
        install_button = ttk.Button( dep_list_frame, text="Install", command=self._install_dependencies )
        install_button.pack(side=tk.LEFT, padx=0)
        
        # Load dependencies into dropdown
        self._load_dependencies(dep_dropdown)

        # Clear metadata cache button
        cache_frame = ttk.Frame(dependencies_frame)
        cache_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cache_frame, text="Metadata Cache:", width=15).pack(side=tk.LEFT, padx=(0, 10))
        clear_cache_button = ttk.Button(
            cache_frame, text="Refresh Script Metadata Cache",
            command=self._refresh_metadata_cache, style='Cancel.TButton'
        )
        clear_cache_button.pack(side=tk.LEFT, padx=0)

    def _create_logs_tab(self, parent):
        """Create the logs tab."""
        # Log display
        log_frame = ttk.LabelFrame(parent, text="Recent Logs", padding=(10, 5))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Log file path with clear button
        log_path_frame = ttk.Frame(log_frame)
        log_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(log_path_frame, text="Log File Path:", width=15).pack(side=tk.LEFT, padx=(0, 10))

        # Use centralized log path
        log_dir = get_log_path()
        log_file = log_dir / "boop.log"
        self.log_path_var = tk.StringVar(value=str(log_file))
        log_path_entry = ttk.Entry(log_path_frame, textvariable=self.log_path_var)
        log_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Clear button
        clear_button = ttk.Button(
            log_path_frame, text="Clear Logs",
            command=self._clear_logs, style='Cancel.TButton'
        )
        clear_button.pack(side=tk.LEFT, padx=0)

        self.log_text = tk.Text(
            log_frame, font=('SF Pro Text', 11), bg='#f9f9f9', borderwidth=1,
            relief=tk.SUNKEN, wrap=tk.WORD
        )

        # Add scrollbar for log text
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        # Load logs
        self._load_logs()

    def _bind_events(self):
        """Bind keyboard events."""
        # Bind Enter key to save button
        self.dialog.bind('<Return>', lambda e: self._save(show_message=False))
        # Bind Esc key to cancel button
        self.dialog.bind('<Escape>', lambda e: self._close())

    def _toggle_maximize(self):
        """Toggle the enable state of window size inputs based on maximize setting."""
        if self.maximize_var.get():
            # Disable size inputs when maximize is checked
            self.width_entry.config(state=tk.DISABLED)
            self.height_entry.config(state=tk.DISABLED)
        else:
            # Enable size inputs when maximize is unchecked
            self.width_entry.config(state=tk.NORMAL)
            self.height_entry.config(state=tk.NORMAL)

    def _add_directory(self):
        """Add a script directory."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Select Script Directory")
        if directory:
            if directory not in self.config.script_directories:
                self.dirs_listbox.insert(tk.END, directory)

    def _remove_directory(self):
        """Remove a script directory."""
        selection = self.dirs_listbox.curselection()
        if selection:
            self.dirs_listbox.delete(selection[0])

    def _browse_python(self):
        """Browse for Python interpreter."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Python Interpreter",
            filetypes=[("Python Executable", "python*"), ("All Files", "*")]
        )
        if file_path:
            self.python_var.set(file_path)
    
    def _load_dependencies(self, dropdown):
        """Load dependencies into the dropdown list."""
        from app.core.script import ScriptManager
        
        try:
            # Create script manager and load metadata
            script_manager = ScriptManager(self.config)
            script_manager.load_metadata()
            
            # Get all cached metadata
            all_cached_metadata = script_manager.get_all_metadata()
            
            # Collect all dependencies from scripts
            dependencies = set()
            for file_path_str, metadata_dict in all_cached_metadata.items():
                if 'dependencies' in metadata_dict and metadata_dict['dependencies']:
                    dependencies.update(metadata_dict['dependencies'])
            
            # Add dependencies to dropdown
            if dependencies:
                dep_list = sorted(list(dependencies))
                dropdown['values'] = dep_list
                if dep_list:
                    self.dep_var.set(f"{len(dep_list)} dependencies found")
            else:
                dropdown['values'] = ["No dependencies found"]
                self.dep_var.set("No dependencies found")
        except Exception as e:
            dropdown['values'] = ["Error loading dependencies"]
            self.dep_var.set("Error loading dependencies")

    def _load_logs(self):
        """Load log files."""
        # Use centralized log path
        log_dir = get_log_path()
        log_file = log_dir / "boop.log"

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.read()
                self.log_text.insert(tk.END, logs)
            except Exception as e:
                self.log_text.insert(tk.END, f"Error reading log file: {e}")
        else:
            self.log_text.insert(tk.END, "No log file found.")

        self.log_text.configure(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def _clear_logs(self):
        """Clear log files."""
        # Use centralized log path
        log_dir = get_log_path()
        log_file = log_dir / "boop.log"

        if log_file.exists():
            if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
                try:
                    log_file.unlink()
                    self._load_logs()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear logs: {e}")

    def _open_log_in_editor(self):
        """Open log file in default text editor."""
        import subprocess
        import platform
        from boop.core.utils import get_user_data_dir

        # Use centralized log path
        log_dir = get_log_path()
        log_file = log_dir / "boop.log"

        if log_file.exists():
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(log_file)])
                elif platform.system() == "Windows":  # Windows
                    subprocess.run(["start", str(log_file)], shell=True)
                else:  # Linux
                    subprocess.run(["xdg-open", str(log_file)])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open log file: {e}")
        else:
            messagebox.showinfo("Info", "Log file does not exist.")

    def _save(self, show_message=False):
        """Save preferences.
        
        Args:
            show_message: Whether to show success messages
        """
        logger.info("Saving preferences")
        try:
            # Check if Python path has changed
            old_python_path = self.config.python_path
            
            # Update window settings
            self.config.window_width = int(self.width_var.get())
            self.config.window_height = int(self.height_var.get())
            self.config.maximize_window = self.maximize_var.get()
            self.config.enable_global_hotkeys = self.enable_global_hotkeys_var.get()
            self.config.font_family = self.font_family_var.get()
            self.config.font_size = int(self.font_size_var.get())

            import os
            # Update script settings
            # Expand ~ in script directories
            script_dirs = list(self.dirs_listbox.get(0, tk.END))
            self.config.script_directories = [os.path.expanduser(d) for d in script_dirs]
            
            # Expand ~ in Python path
            python_path = self.python_var.get()
            self.config.python_path = os.path.expanduser(python_path)
            self.config.script_timeout = int(self.timeout_var.get())
            self.config.filter_delay = int(self.filter_delay_var.get())

            # Save to file - use user data directory
            # Get user data directory
            user_data_dir = get_user_data_dir()

            # Config path in user data directory
            config_path = user_data_dir / "config.json"
            self.config.save(config_path)
            logger.info(f"Preferences saved to: {config_path}")

            # Update editor font if editor is available
            if self.editor:
                self.editor.update_font(
                    self.config.font_family,
                    self.config.font_size
                )
                logger.info(f"Editor font updated: {self.config.font_family}, {self.config.font_size}")

            # Show restart prompt if Python path changed and show_message is True
            if old_python_path != self.config.python_path:
                logger.info(f"Python path changed from {old_python_path} to {self.config.python_path}")
                messagebox.showinfo("Restart Required", "Python path has been changed. Please restart the application for changes to take effect.")
            elif show_message:
                messagebox.showinfo("Success", "Preferences saved successfully.")

            self._close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
            logger.error(f"Failed to save preferences: {e}")

    def _install_dependencies(self):
        """Install dependencies defined in script metadata."""
        logger.info("Installing dependencies")
        import subprocess
        import sys
        from pathlib import Path
        from app.core.script import ScriptManager
        
        # Create script manager and load metadata
        script_manager = ScriptManager(self.config)
        script_manager.load_metadata()
        
        # Get all cached metadata
        all_cached_metadata = script_manager.get_all_metadata()
        
        # Collect all dependencies from scripts
        dependencies = set()
        for file_path_str, metadata_dict in all_cached_metadata.items():
            if 'dependencies' in metadata_dict and metadata_dict['dependencies']:
                dependencies.update(metadata_dict['dependencies'])
        
        if not dependencies:
            messagebox.showinfo("Info", "No dependencies found in scripts.")
            logger.info("No dependencies found in scripts")
            return
        
        # Get Python interpreter path
        python_exe = self.config.python_path
        
        if not python_exe:
            messagebox.showerror("Error", "No Python interpreter found. Please set Python path in preferences.")
            logger.error("No Python interpreter found for dependency installation")
            return
        
        logger.info(f"Found {len(dependencies)} dependencies to install: {dependencies}")
        # Create a progress window
        progress_window = tk.Toplevel(self.dialog)
        progress_window.title("Installing Dependencies")
        progress_window.transient(self.dialog)
        progress_window.geometry("400x200")
        progress_window.grab_set()
        
        # Progress label
        progress_label = tk.Label(progress_window, text="Installing dependencies...", pady=20)
        progress_label.pack(fill=tk.X)
        
        # Progress bar
        progress_bar = ttk.Progressbar(progress_window, length=350, mode='determinate', maximum=len(dependencies))
        progress_bar.pack(pady=10)
        
        # Status text
        status_text = tk.Text(progress_window, height=5, wrap=tk.WORD)
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        status_text.insert(tk.END, f"Found {len(dependencies)} dependencies to install:\n")
        for dep in dependencies:
            status_text.insert(tk.END, f"- {dep}\n")
        status_text.insert(tk.END, "\nInstalling...\n")
        status_text.see(tk.END)
        
        # Update the window
        progress_window.update()
        
        try:
            # Install dependencies
            for i, dep in enumerate(dependencies):
                status_text.insert(tk.END, f"Installing {dep}...\n")
                status_text.see(tk.END)
                progress_window.update()
                
                # Update progress bar
                progress_bar['value'] = i
                progress_window.update()
                
                # Run pip install
                logger.info(f"Installing dependency: {dep}")
                result = subprocess.run(
                    [python_exe, "-m", "pip", "install", dep],
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    status_text.insert(tk.END, f"✓ Successfully installed {dep}\n")
                    logger.info(f"Successfully installed dependency: {dep}")
                else:
                    status_text.insert(tk.END, f"✗ Failed to install {dep}: {result.stderr}\n")
                    logger.error(f"Failed to install dependency: {dep}, error: {result.stderr}")
                status_text.see(tk.END)
                progress_window.update()
            
            # Update progress bar to 100%
            progress_bar['value'] = len(dependencies)
            
            status_text.insert(tk.END, "\nDependency installation completed!\n")
            status_text.see(tk.END)
            logger.info("Dependency installation completed")
            
            # Add a close button
            close_button = tk.Button(progress_window, text="Close", command=progress_window.destroy)
            close_button.pack(pady=10)
            
        except Exception as e:
            status_text.insert(tk.END, f"Error: {str(e)}\n")
            status_text.see(tk.END)
            progress_bar.stop()
            logger.error(f"Error during dependency installation: {e}")
            
            # Add a close button
            close_button = tk.Button(progress_window, text="Close", command=progress_window.destroy)
            close_button.pack(pady=10)
    
    def _refresh_metadata_cache(self):
        """Refresh metadata cache."""
        logger.info("Refreshing metadata cache")
        from app.core.script import ScriptManager
        
        try:
            # Create a script manager and use the new refresh_metadata_cache method
            script_manager = ScriptManager(self.config)
            script_count = script_manager.refresh_metadata_cache()
            messagebox.showinfo("Success", f"Metadata cache refreshed successfully.\nLoaded {script_count} scripts.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh metadata cache: {e}")
            logger.error(f"Failed to refresh metadata cache: {e}")

    def _close(self):
        """Close the preferences panel."""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
            self.dialog = None
