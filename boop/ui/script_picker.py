"""
ScriptPickerPopup - Script selection popup panel

This module implements a popup panel for selecting scripts.
Uses tk.Toplevel for proper window management.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Callable
from boop.core.script import LoadedScript, ScriptManager
from boop.core.utils import get_icon_path


class ScriptPickerPopup:
    """
    Script picker popup panel using Toplevel window.
    
    Usage:
        def on_selected(script):
            if script:
                execute_script(script)

        ScriptPickerPopup(parent, manager, on_selected, editor)
    """

    def __init__(
        self,
        parent: tk.Tk,
        manager: ScriptManager,
        on_script_selected: Callable[[Optional[LoadedScript]], None],
        editor_widget: tk.Text
    ):
        self.parent = parent
        self.manager = manager
        self.on_script_selected = on_script_selected
        self.editor = editor_widget
        self.dialog: Optional[tk.Toplevel] = None
        self.scripts: List[LoadedScript] = []
        self._debounce_timer = None
        self._script_name_map = {}
        self.result: Optional[LoadedScript] = None

        self._create_dialog()
        # _refresh_scripts is called at the end of _create_dialog

    def _create_dialog(self):
        """Create the dialog Toplevel window."""
        # Create Toplevel window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Script")
        self.dialog.transient(self.parent)  # Make it transient to parent
        self.dialog.resizable(False, False)

        # Center the dialog
        self.dialog.geometry("800x500")
        self.dialog.update_idletasks()

        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"800x500+{x}+{y}")

        # Make dialog modal-like
        self.dialog.grab_set()
        self.dialog.focus_set()

        self._create_ui()
        self._bind_events()
        self._refresh_scripts()
        
        # Set focus to search entry for immediate typing
        self.search_entry.focus_set()

    def _create_ui(self):
        """Create dialog UI components."""
        # Main container
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header = tk.Frame(main_frame, bg='white')
        header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header,
            text="📜 Select Script",
            bg='white',
            font=('TkDefaultFont', 12, 'bold')
        ).pack(side=tk.LEFT)

        # Search box
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍", bg='white').pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('TkDefaultFont', 11),
            relief=tk.FLAT,
            bg='#f5f5f5'
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.search_entry.focus_set()

        self.search_var.trace('w', lambda *args: self._filter_scripts())



        # Main content area with two columns
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left column: Script list
        list_frame = tk.Frame(content_frame, bg='white')
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        columns = ('name', 'description')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15,
            selectmode='browse'
        )

        self.tree.heading('name', text='Script Name')
        self.tree.heading('description', text='Description')
        self.tree.column('name', width=250, minwidth=200)
        self.tree.column('description', width=200, minwidth=150)
        
        # Store script name mapping for tree items
        self._script_name_map = {}

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right column: Script details
        details_frame = tk.Frame(content_frame, bg='white', relief='solid', borderwidth=1)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        details_frame.update_idletasks()
        details_frame.pack_propagate(False)  # Prevent frame from resizing to fit contents
        details_frame.configure(width=300)  # Set fixed width

        # Details header
        details_header = tk.Frame(details_frame, bg='#f5f5f5')
        details_header.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(
            details_header,
            text="📋 Script Details",
            bg='#f5f5f5',
            font=('TkDefaultFont', 10, 'bold')
        ).pack(side=tk.LEFT)

        # Script name
        name_frame = tk.Frame(details_frame, bg='white')
        name_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(
            name_frame,
            text="Name:",
            bg='white',
            font=('TkDefaultFont', 9, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.script_name_var = tk.StringVar(value="Select a script")
        tk.Label(
            name_frame,
            textvariable=self.script_name_var,
            bg='white',
            font=('TkDefaultFont', 9),
            anchor=tk.W,
            wraplength=250
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Script description
        desc_frame = tk.Frame(details_frame, bg='white')
        desc_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(
            desc_frame,
            text="Description:",
            bg='white',
            font=('TkDefaultFont', 9, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.script_desc_var = tk.StringVar(value="")
        tk.Label(
            desc_frame,
            textvariable=self.script_desc_var,
            bg='white',
            font=('TkDefaultFont', 9),
            anchor=tk.W,
            wraplength=250,
            justify=tk.LEFT
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Help information
        help_frame = tk.Frame(details_frame, bg='white')
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        tk.Label(
            help_frame,
            text="Help:",
            bg='white',
            font=('TkDefaultFont', 9, 'bold')
        ).pack(anchor=tk.NW, pady=(0, 5))

        self.help_text = tk.Text(
            help_frame,
            font=('TkDefaultFont', 8),
            bg='#f9f9f9',
            borderwidth=1,
            relief=tk.SUNKEN,
            wrap=tk.WORD,
            height=8
        )
        self.help_text.pack(fill=tk.BOTH, expand=True)
        self.help_text.insert(tk.END, "Select a script to see help information")
        self.help_text.configure(state=tk.DISABLED)

        # Bindings
        self.tree.bind('<Double-Button-1>', lambda e: self._on_select())
        self.tree.bind('<<TreeviewSelect>>', lambda e: self._on_script_select())

        # Status
        self.status_var = tk.StringVar(value="")
        tk.Label(
            main_frame,
            textvariable=self.status_var,
            bg='white',
            fg='gray',
            font=('TkDefaultFont', 9)
        ).pack(fill=tk.X, pady=(10, 0))

        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Cancel button (Esc key)
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancel (Esc)",
            command=self._close,
            bg='#f5f5f5',
            fg='#333333',
            activebackground='#e0e0e0',
            activeforeground='#000000',
            relief=tk.RAISED,
            borderwidth=1,
            padx=15,
            pady=5,
            font=('TkDefaultFont', 10)
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Run button (Enter key)
        self.run_btn = tk.Button(
            button_frame,
            text="Run (Enter)",
            command=self._on_select,
            bg='#0066cc',
            fg='#ffffff',
            activebackground='#0052a3',
            activeforeground='#ffffff',
            relief=tk.RAISED,
            borderwidth=1,
            padx=15,
            pady=5,
            font=('TkDefaultFont', 10, 'bold')
        )
        self.run_btn.pack(side=tk.RIGHT, padx=5)

    def _bind_events(self):
        """Bind keyboard events."""
        # Navigation keys for script list
        self.dialog.bind('<Up>', lambda e: self._navigate(-1))
        self.dialog.bind('<Down>', lambda e: self._navigate(1))
        self.dialog.bind('<Prior>', lambda e: self._navigate_page(-1))  # PageUp
        self.dialog.bind('<Next>', lambda e: self._navigate_page(1))    # PageDown
        self.dialog.bind('<Home>', lambda e: self._navigate_home())
        self.dialog.bind('<End>', lambda e: self._navigate_end())
        
        # Enter key to run selected script
        self.dialog.bind('<Return>', lambda e: self._on_select())
        self.dialog.bind('<KP_Enter>', lambda e: self._on_select())
        
        # Esc key to cancel
        self.dialog.bind('<Escape>', lambda e: self._close())

    def _refresh_scripts(self):
        """Load and display scripts."""
        if not self.dialog or not self.dialog.winfo_exists():
            return

        scripts_list = self.manager.list_scripts()
        self.scripts = scripts_list
        self._populate_list(self.scripts)
        self.status_var.set(f"{len(self.scripts)} scripts available")
        self._update_categories()

    def _update_categories(self):
        """Update categories (no-op since we removed category filtering)."""
        pass

    def _populate_list(self, scripts: List[LoadedScript]):
        """Populate the tree with scripts."""
        if not hasattr(self, 'tree') or self.tree is None:
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._script_name_map.clear()

        for script in scripts:
            icon = "📄"
            item_id = self.tree.insert(
                '',
                tk.END,
                values=(f"{icon} {script.metadata.name}", script.metadata.description)
            )
            self._script_name_map[item_id] = script.metadata.name

        self.tree.update_idletasks()

        if scripts:
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)
            self._on_script_select()

    def _filter_scripts(self):
        """Filter scripts based on search query."""
        if self._debounce_timer:
            self.parent.after_cancel(self._debounce_timer)

        self._debounce_timer = self.parent.after(150, self._do_filter)

    def _do_filter(self):
        """Perform the search."""
        query = self.search_var.get().lower()

        if query:
            filtered_scripts = [script for script in self.scripts
                              if query in script.metadata.name.lower() or
                                 any(query in tag.lower() for tag in script.metadata.tags)]
        else:
            filtered_scripts = self.scripts

        self._populate_list(filtered_scripts)

        if not query:
            self.status_var.set(f"{len(filtered_scripts)} scripts available")
        else:
            self.status_var.set(f"{len(filtered_scripts)} script(s) found")

        if filtered_scripts:
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)
            self._on_script_select()

    def _on_script_select(self):
        """Update script details when a script is selected."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        name = self._script_name_map.get(item)
        if not name:
            return
            
        script = self.manager.get_script(name)

        if script:
            self.script_name_var.set(script.metadata.name)
            self.script_desc_var.set(script.metadata.description)

            self.help_text.configure(state=tk.NORMAL)
            self.help_text.delete('1.0', tk.END)

            help_text = script.metadata.help
            if help_text:
                self.help_text.insert(tk.END, help_text)
            else:
                self.help_text.insert(tk.END, f"No help information available for {script.metadata.name}")

            self.help_text.configure(state=tk.DISABLED)

    def _on_select(self):
        """Handle script selection."""
        selection = self.tree.selection()
        script = None

        if selection:
            item = selection[0]
            name = self._script_name_map.get(item)
            if name:
                script = self.manager.get_script(name)

        self.result = script
        self._close()

        if self.on_script_selected:
            self.parent.after(50, lambda: self.on_script_selected(script))

    def _filter_by_category(self, category):
        """Filter scripts by category."""
        self.category_var.set(category)

        for category_id, btn in self.category_buttons:
            if category_id == category:
                btn.configure(bg='#e0e0e0')
            else:
                btn.configure(bg='#f0f0f0')

        self._do_filter()

    def _navigate(self, direction):
        """Navigate up or down in the script list with wrap-around."""
        items = self.tree.get_children()
        if not items:
            return

        current = self.tree.selection()
        if not current:
            # If no selection, select first item for down, last for up
            if direction > 0:
                selected_item = items[0]
            else:
                selected_item = items[-1]
        else:
            item = current[0]
            next_item = self.tree.next(item) if direction > 0 else self.tree.prev(item)
            if next_item:
                selected_item = next_item
            else:
                # Wrap around to the other end
                selected_item = items[0] if direction > 0 else items[-1]

        self.tree.selection_set(selected_item)
        self.tree.focus(selected_item)
        self.tree.see(selected_item)

    def _navigate_page(self, direction):
        """Navigate page up or down in the script list."""
        current = self.tree.selection()
        if not current:
            return

        item = current[0]
        items = self.tree.get_children()
        index = items.index(item)
        new_index = index + (5 * direction)
        new_index = max(0, min(len(items) - 1, new_index))

        new_item = items[new_index]
        self.tree.selection_set(new_item)
        self.tree.focus(new_item)
        self.tree.see(new_item)

    def _navigate_home(self):
        """Navigate to the first item."""
        items = self.tree.get_children()
        if items:
            self.tree.selection_set(items[0])
            self.tree.focus(items[0])
            self.tree.see(items[0])

    def _navigate_end(self):
        """Navigate to the last item."""
        items = self.tree.get_children()
        if items:
            self.tree.selection_set(items[-1])
            self.tree.focus(items[-1])
            self.tree.see(items[-1])

    def _close(self):
        """Close the dialog."""
        if self._debounce_timer:
            self.parent.after_cancel(self._debounce_timer)

        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
            self.dialog = None
