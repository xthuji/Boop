"""
Editor Component - Text editor with line numbers and syntax highlighting
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from boop.core.utils import binding_hotkey_action
from boop.ui.editor_extensions import EditorExtensions


class Editor:
    """Text editor component with line numbers and syntax highlighting."""
    
    def __init__(self, parent: tk.Widget, config):
        """Initialize the editor.
        
        Args:
            parent: Parent widget
            config: Application configuration
        """
        self.parent = parent
        self.config = config
        self._text_widget: Optional[tk.Text] = None
        self._line_numbers: Optional[tk.Text] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None
        
        # History for undo/redo
        self._history = []
        self._history_index = -1
        
        # Script execution history
        self._script_history = []
        self._current_script_history_index = -1
        
        self._create_ui()
        # Initialize editor extensions
        self.extensions = EditorExtensions(self._text_widget, self.config)
        self._bind_events()
        # Initialize history with empty state
        self._save_state()
    
    def _create_ui(self):
        """Create the editor UI."""
        # Main frame
        frame = tk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self._scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Line numbers
        self._line_numbers = tk.Text(
            frame,
            width=4,
            padx=5,
            pady=2,
            bg='#f0f0f0',
            fg='#666666',
            font=(self.config.font_family, self.config.font_size),
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        self._line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text widget
        self._text_widget = tk.Text(
            frame,
            font=(self.config.font_family, self.config.font_size),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0
        )
        self._text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Link scrollbar
        self._scrollbar.config(command=self._scroll)
        self._text_widget.config(yscrollcommand=self._scrollbar.set)
        self._line_numbers.config(yscrollcommand=self._scrollbar.set)
    
    def _bind_events(self):
        """Bind keyboard and mouse events."""
        # Text change events
        self._text_widget.bind('<<Modified>>', self._on_modified)
        
        # Bind shortcuts that are only relevant in the editor
        binding_hotkey_action(self._text_widget, self.config.shortcuts.get('select_next_occurrence', ['Ctrl+d']), self.extensions.select_next_occurrence)
        
        # Bind key press event for multi-cursor editing
        self._text_widget.bind('<Key>', self.extensions.on_key_press)
        
        # Mouse wheel
        self._text_widget.bind('<MouseWheel>', self._on_mousewheel)
        self._line_numbers.bind('<MouseWheel>', self._on_mousewheel)
    
    def _scroll(self, *args):
        """Sync scrollbar between text and line numbers."""
        self._text_widget.yview(*args)
        self._line_numbers.yview(*args)
        self._update_line_numbers()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel event."""
        self._text_widget.yview_scroll(-1 * (event.delta // 120), 'units')
        self._line_numbers.yview_scroll(-1 * (event.delta // 120), 'units')
        self._update_line_numbers()
    
    def _on_modified(self, event):
        """Handle text modification event."""
        # Save state only if content has changed
        self._update_line_numbers()
        self._save_state()
        # Reset the modified flag
        self._text_widget.edit_modified(False)
    
    def _update_line_numbers(self):
        """Update line numbers."""
        lines = self._text_widget.get('1.0', 'end-1c').count('\n') + 1
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self._line_numbers.config(state=tk.NORMAL)
        self._line_numbers.delete('1.0', tk.END)
        self._line_numbers.insert('1.0', line_numbers)
        self._line_numbers.config(state=tk.DISABLED)
    
    def _save_state(self):
        """Save current state for undo/redo."""
        current_text = self.get_content()
        # Only save state if content has actually changed
        # This prevents duplicate entries in the history
        if not self._history or current_text != self._history[self._history_index]:
            # Remove any future history entries if we're not at the end
            if self._history_index < len(self._history) - 1:
                self._history = self._history[:self._history_index + 1]
            # Add new state to history
            self._history.append(current_text)
            self._history_index = len(self._history) - 1
    
    def _undo(self, event):
        """Handle undo operation."""
        if self._history_index > 0:
            # Move to previous state in history
            self._history_index -= 1
            previous_state = self._history[self._history_index]
            # Update text without triggering new state save
            self._text_widget.delete('1.0', tk.END)
            self._text_widget.insert('1.0', previous_state)
            self._update_line_numbers()
        return 'break'
    
    def _redo(self, event):
        """Handle redo operation."""
        if self._history_index < len(self._history) - 1:
            # Move to next state in history
            self._history_index += 1
            next_state = self._history[self._history_index]
            # Update text without triggering new state save
            self._text_widget.delete('1.0', tk.END)
            self._text_widget.insert('1.0', next_state)
            self._update_line_numbers()
        return 'break'
    
    def _cut(self, event):
        """Handle cut operation."""
        self._text_widget.event_generate('<<Cut>>')
        return 'break'
    
    def _copy(self, event):
        """Handle copy operation."""
        self._text_widget.event_generate('<<Copy>>')
        return 'break'
    
    def _paste(self, event):
        """Handle paste operation."""
        self._text_widget.event_generate('<<Paste>>')
        return 'break'
    
    def _select_all(self, event):
        """Select all text."""
        self._text_widget.tag_add(tk.SEL, '1.0', tk.END)
        return 'break'
    
    def _move_to_start(self, event):
        """Move cursor to the start of the editor."""
        self._text_widget.mark_set(tk.INSERT, '1.0')
        self._text_widget.see(tk.INSERT)
        return 'break'
    
    def _move_to_end(self, event):
        """Move cursor to the end of the editor."""
        self._text_widget.mark_set(tk.INSERT, 'end-1c')
        self._text_widget.see(tk.INSERT)
        return 'break'
    
    def get_content(self) -> str:
        """Get the editor content."""
        return self._text_widget.get('1.0', 'end-1c')
    
    def set_content(self, text: str):
        """Set the editor content."""
        # Update the content
        self._text_widget.delete('1.0', tk.END)
        self._text_widget.insert('1.0', text)
        self._update_line_numbers()
        # Trigger the modified event to save the state
        self._text_widget.event_generate('<<Modified>>')
    

    
    def get_cursor_position(self) -> tuple:
        """Get the cursor position (line, column)."""
        index = self._text_widget.index(tk.INSERT)
        line, col = map(int, index.split('.'))
        return line, col
    
    def get_char_count(self) -> int:
        """Get the character count."""
        return len(self.get_content())
    
    def focus(self):
        """Focus the editor."""
        self._text_widget.focus_set()
    
    def clear(self):
        """Clear the editor."""
        self.set_content("")
    

    
    def record_script_execution(self, script_name: str):
        """Record script execution for history."""
        # Save current state before execution
        before_state = self.get_content()
        
        # Create history entry
        history_entry = {
            'script_name': script_name,
            'before': before_state,
            'after': None  # Will be filled after execution
        }
        
        # Remove any future history entries if we're not at the end
        if self._current_script_history_index < len(self._script_history) - 1:
            self._script_history = self._script_history[:self._current_script_history_index + 1]
        
        # Add new history entry
        self._script_history.append(history_entry)
        self._current_script_history_index = len(self._script_history) - 1
        
        # Save current state to undo/redo history
        # This ensures the state before script execution is always saved
        self._save_state()
    
    def update_script_execution_result(self, after_state: str):
        """Update the after state for the last script execution."""
        if self._script_history and self._current_script_history_index >= 0:
            self._script_history[self._current_script_history_index]['after'] = after_state
    

