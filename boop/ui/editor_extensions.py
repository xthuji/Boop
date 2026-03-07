"""
Editor Extensions - Extensions for the editor component
"""

import tkinter as tk
import logging
import platform
from typing import List, Tuple, Optional

# Create a logger
logger = logging.getLogger(__name__)

# Define platform-specific modifier key codes
PLATFORM = platform.system()

if PLATFORM == 'Darwin':  # macOS
    MODIFIER_KEYS = {
        'command': 0x0008,  # Command key on macOS
        'control': 0x0004,  # Control key
        'shift': 0x0001,    # Shift key
        'alt': 0x0010       # Option key on macOS
    }
elif PLATFORM == 'Windows':  # Windows
    MODIFIER_KEYS = {
        'control': 0x0004,  # Control key
        'alt': 0x0008,      # Alt key
        'shift': 0x0001,    # Shift key
        'meta': 0x0010      # Windows key
    }
else:  # Linux and other platforms
    MODIFIER_KEYS = {
        'control': 0x0004,  # Control key
        'alt': 0x0008,      # Alt key
        'shift': 0x0001,    # Shift key
        'meta': 0x0010      # Meta key
    }

logger.debug(f"Platform detected: {PLATFORM}, using modifier keys: {MODIFIER_KEYS}")


class EditorExtensions:
    """Extensions for the editor component, providing multi-cursor editing functionality."""
    
    def __init__(self, text_widget, config=None):
        """Initialize the editor extensions.
        
        Args:
            text_widget: The text widget to extend
            config: Application configuration (optional)
        """
        self.text_widget = text_widget
        self.config = config
        self._selections = []
        self._selected_text = ""
        # Original text before multi-cursor editing
        self._original_text = ""
        # Original selected text
        self._original_selected_text = ""
        # New text being built during multi-cursor editing
        self._new_text = ""
        # Flag to track if hint has been shown
        self._hint_shown = False
        self._bind_events()
    
    def _bind_events(self):
        """Bind events for the extensions."""
        # Bind mouse click event to clear selections
        self.text_widget.bind('<Button-1>', self._on_mouse_click)
    
    def _is_shortcut_pressed(self, event, shortcut_name):
        """Check if a shortcut is pressed based on the event and shortcut name.
        
        Args:
            event: The keyboard event
            shortcut_name: The name of the shortcut in the config
            
        Returns:
            bool: True if the shortcut is pressed, False otherwise
        """
        if not self.config or not hasattr(self.config, 'shortcuts'):
            # Fallback to default behavior if no config
            return False
        
        # Get the shortcuts for the given name
        shortcuts = self.config.shortcuts.get(shortcut_name, [])
        
        # Check each shortcut
        for shortcut in shortcuts:
            # Split the shortcut into parts
            parts = shortcut.split('+')
            # Check if all modifier keys are pressed
            if len(parts) > 1:
                # Check modifier keys
                modifiers = parts[:-1]
                key = parts[-1]
                
                # Check if the key matches
                if event.keysym.lower() != key.lower():
                    continue
                
                # Check modifier keys
                modifier_pressed = True
                for modifier in modifiers:
                    modifier_key = modifier.lower()
                    if modifier_key in MODIFIER_KEYS:
                        if not (event.state & MODIFIER_KEYS[modifier_key]):
                            modifier_pressed = False
                            break
                    else:
                        # Unknown modifier, treat as not pressed
                        modifier_pressed = False
                        break
                
                if modifier_pressed:
                    return True
            else:
                # No modifiers, just check the key
                if event.keysym.lower() == shortcut.lower():
                    return True
        
        return False
    
    def _on_mouse_click(self, event):
        """Handle mouse click events to clear multi-selection."""
        # Clear selections list and selected text
        self._selections = []
        self._selected_text = ""
        # Clear selection display
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
        # Let the default behavior handle the click
        return None
    
    def _update_selections_display(self):
        """Update the display of selections based on self._selections."""
        # Clear existing selections
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
        
        # Add all selections from the list
        for start, end in self._selections:
            self.text_widget.tag_add(tk.SEL, start, end)
    
    def select_next_occurrence(self, event):
        """Select the next occurrence of the currently selected text."""
        # First time: get selected text or current word
        if not self._selected_text:
            try:
                # Get currently selected text
                self._selected_text = self.text_widget.selection_get()
                # Get the selection range
                start = self.text_widget.index(tk.SEL_FIRST)
                end = self.text_widget.index(tk.SEL_LAST)
                # Clear existing selections and add the first selection
                self._selections = [(start, end)]
                # Record original text and selected text
                self._original_text = self.text_widget.get('1.0', 'end-1c')
                self._original_selected_text = self._selected_text
                # Reset new text
                self._new_text = ""
            except tk.TclError:
                # No selection, use current word
                start = self.text_widget.index('insert wordstart')
                end = self.text_widget.index('insert wordend')
                self._selected_text = self.text_widget.get(start, end)
                # Clear existing selections and add the current word
                self._selections = [(start, end)]
                # Record original text and selected text
                self._original_text = self.text_widget.get('1.0', 'end-1c')
                self._original_selected_text = self._selected_text
                # Reset new text
                self._new_text = ""
        
        if not self._selected_text:
            return 'break'
        
        # Determine search start position
        if self._selections:
            # Start from the end of the last selection
            last_sel_end = self._selections[-1][1]
            # Make sure we're not at the end of the text
            if last_sel_end != self.text_widget.index(tk.END):
                search_start = self.text_widget.index(f'{last_sel_end}+1c')
            else:
                # Already at the end, no more occurrences
                # Still update display to show current selections
                self._update_selections_display()
                return 'break'
        else:
            # No selections yet, start from beginning
            search_start = '1.0'
        
        # Search for the next occurrence
        next_pos = self.text_widget.search(self._selected_text, search_start, stopindex=tk.END, nocase=True)
        
        if next_pos:
            # Calculate the end of the next occurrence
            next_end = f'{next_pos}+{len(self._selected_text)}c'
            # Add to selections list
            self._selections.append((next_pos, next_end))
        
        # Always update display to show current selections
        self._update_selections_display()
        
        # Move cursor to the end of the last selection if we have selections
        if self._selections:
            last_sel_end = self._selections[-1][1]
            self.text_widget.mark_set(tk.INSERT, last_sel_end)
            # Scroll to make the new selection visible
            self.text_widget.see(last_sel_end)
        
        # Show multi-cursor mode hint if we have multiple selections and hint hasn't been shown
        if len(self._selections) > 1 and not self._hint_shown:
            self._show_multi_cursor_hint()
            self._hint_shown = True
        
        return 'break'
    
    def _show_multi_cursor_hint(self):
        """Show a hint about how to exit multi-cursor mode."""
        # Create a temporary toplevel window for the hint
        hint_window = tk.Toplevel(self.text_widget)
        hint_window.transient(self.text_widget)
        hint_window.overrideredirect(True)  # Remove window decorations
        hint_window.attributes('-topmost', True)  # Keep on top
        hint_window.attributes('-alpha', 0.9)  # Semi-transparent
        
        # Calculate position at the top right corner of the window
        # Get the top-level window
        top_level = self.text_widget.winfo_toplevel()
        window_width = top_level.winfo_width()
        window_x = top_level.winfo_rootx()
        window_y = top_level.winfo_rooty()
        
        # Create label with hint text to calculate its size
        hint_label = tk.Label(
            hint_window,
            text="多光标编辑模式\n按 Escape、方向键、Enter、点击鼠标 或全选文本 可退出",
            bg="#f8f9fa", fg="#343a40",
            padx=16, pady=12, font=('SF Pro Display', 12), relief=tk.FLAT, borderwidth=1,
            highlightbackground="#dee2e6", highlightthickness=1
        )
        hint_label.pack()
        
        # Update the window to get its size
        hint_window.update_idletasks()
        hint_width = hint_window.winfo_width()
        
        # Position the window at the top right corner
        hint_x = window_x + window_width - hint_width - 20
        hint_y = window_y + 20
        hint_window.geometry(f"+{hint_x}+{hint_y}")
        
        # Add some modern styling
        hint_window.configure(bg="#f8f9fa")
        
        # Schedule window to close after 3 seconds
        self.text_widget.after(3000, hint_window.destroy)
    
    def on_key_press(self, event):
        """Handle key press events for multi-cursor editing."""
        # Only log key presses that are relevant to multi-cursor functionality
        if event.keysym in ['BackSpace', 'Escape'] or event.char.isprintable():
            logger.debug(f"Key pressed: keysym={event.keysym}, char={event.char}")
        
        # Check for shortcuts
        paste_pressed = self._is_shortcut_pressed(event, 'paste')
        select_all_pressed = self._is_shortcut_pressed(event, 'select_all')
        
        # Handle select all shortcut - always exit multi-cursor mode
        if select_all_pressed:
            self._clear_multi_cursor_state()
            logger.debug("Exited multi-cursor mode with select all shortcut")
            return None
        
        # Handle paste operation outside of multi-cursor mode
        if paste_pressed and len(self._selections) <= 1:
            return self._handle_paste(event)
        
        # Check if we're in multi-cursor mode
        if len(self._selections) > 1:
            return self._handle_multi_cursor_mode(event, paste_pressed)
        
        return None
    
    def _clear_multi_cursor_state(self):
        """Clear multi-cursor state."""
        self._selections = []
        self._selected_text = ""
        self._original_text = ""
        self._original_selected_text = ""
        self._new_text = ""
        # Reset hint shown flag
        self._hint_shown = False
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
    
    def _handle_paste(self, event):
        """Handle paste operation."""
        try:
            # Get clipboard content
            clipboard_content = self.text_widget.clipboard_get()
            
            # Check if there is a selection
            try:
                # Get selection range
                sel_start = self.text_widget.index(tk.SEL_FIRST)
                sel_end = self.text_widget.index(tk.SEL_LAST)
                # Delete selected text
                self.text_widget.delete(sel_start, sel_end)
                # Insert at the start of the selection
                self.text_widget.insert(sel_start, clipboard_content)
                # Move cursor to the end of the pasted content
                self.text_widget.mark_set(tk.INSERT, f'{sel_start}+{len(clipboard_content)}c')
            except tk.TclError:
                # No selection, insert at current cursor position
                insert_pos = self.text_widget.index(tk.INSERT)
                self.text_widget.insert(insert_pos, clipboard_content)
                # Move cursor to the end of the pasted content
                self.text_widget.mark_set(tk.INSERT, f'{insert_pos}+{len(clipboard_content)}c')
            
            self.text_widget.see(tk.INSERT)
            
            # Clear any existing selections
            self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            
            # Clear multi-cursor state if any
            self._clear_multi_cursor_state()
            
            return 'break'  # Prevent default behavior
        except Exception as e:
            # If anything goes wrong, let the default behavior handle it
            logger.error(f"Error in paste operation: {e}")
            pass
    
    def _handle_multi_cursor_mode(self, event, paste_pressed):
        """Handle events in multi-cursor mode."""
        # Handle exit keys - exit multi-cursor mode
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Home', 'End', 'PageUp', 'PageDown', 'Escape', 'Return', 'KP_Enter']:
            self._clear_multi_cursor_state()
            return None
        
        # Handle delete operations
        if event.keysym in ['BackSpace']:
            return self._handle_delete()
        
        # Handle paste operation in multi-cursor mode
        if paste_pressed:
            return self._handle_multi_cursor_paste()
        
        # Handle printable characters
        if event.char and event.char.isprintable():
            return self._handle_printable_character(event.char)
        
        return None
    
    def _replace_selected_occurrences(self):
        """Replace selected occurrences and track new positions."""
        # Use the original text as the base
        result = self._original_text
        
        # Sort selections in natural order (from top to bottom, left to right)
        sorted_selections = sorted(self._selections, key=lambda x: (int(x[0].split('.')[0]), int(x[0].split('.')[1])))
        
        # Track the new positions of the selections
        new_positions = []
        
        # Calculate the original line positions
        original_line_positions = []
        orig_pos = 0
        for line in self._original_text.split('\n'):
            original_line_positions.append(orig_pos)
            orig_pos += len(line) + 1  # +1 for newline
        
        # Calculate the offset caused by each replacement
        total_offset = 0
        
        # Process each selection in natural order
        for i, (start, end) in enumerate(sorted_selections):
            start_line, start_col = map(int, start.split('.'))
            
            # Calculate the original absolute start position
            original_absolute_start = original_line_positions[start_line - 1] + start_col
            
            # Calculate the absolute start position with offset
            absolute_start = original_absolute_start + total_offset
            
            # Get the absolute end position
            absolute_end = absolute_start + len(self._original_selected_text)
            
            # Replace the selected text
            result = result[:absolute_start] + self._new_text + result[absolute_end:]
            
            # Calculate the offset change
            offset_change = len(self._new_text) - len(self._original_selected_text)
            total_offset += offset_change
            
            # Calculate the new position of this selection
            # Find the line and column in the new content
            current_pos = 0
            current_line = 0
            new_col = 0
            
            for j, line in enumerate(result.split('\n')):
                line_end = current_pos + len(line)
                if current_pos <= absolute_start <= line_end:
                    # Found the line, calculate the column
                    new_col = absolute_start - current_pos
                    current_line = j + 1  # Convert to 1-based line number
                    break
                current_pos = line_end + 1  # +1 for newline
            
            # Add the new position to the list
            new_positions.append((f"{current_line}.{new_col}", f"{current_line}.{new_col + len(self._new_text)}"))
        
        return result, new_positions
    
    def _update_text_and_selections(self, new_content, new_selections):
        """Update text and selections."""
        # Set the new content
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', new_content)
        
        # Update selections list
        self._selections = new_selections
        # Update display
        self._update_selections_display()
        
        # Update original text to the new content
        self._original_text = new_content
        # Update original selected text to the new text
        self._original_selected_text = self._new_text
        
        # Reset cursor position to the end of the last selection
        if new_selections:
            self.text_widget.mark_set(tk.INSERT, new_selections[-1][1])
            self.text_widget.see(new_selections[-1][1])
    
    def _handle_delete(self):
        """Handle delete operation in multi-cursor mode."""
        try:
            # Remove last character from new text
            if self._new_text:
                self._new_text = self._new_text[:-1]
            
            # Replace only selected occurrences and get new positions
            new_content, new_selections = self._replace_selected_occurrences()
            
            # Update text and selections
            self._update_text_and_selections(new_content, new_selections)
            
            return 'break'  # Prevent default behavior
        except Exception as e:
            # If anything goes wrong, let the default behavior handle it
            logger.error(f"Error in delete operation: {e}")
            pass
    
    def _handle_multi_cursor_paste(self):
        """Handle paste operation in multi-cursor mode."""
        try:
            # Get clipboard content
            clipboard_content = self.text_widget.clipboard_get()
            
            # Add clipboard content to new text
            self._new_text = clipboard_content  # Replace existing new text with clipboard content
            
            # Replace only selected occurrences and get new positions
            new_content, new_selections = self._replace_selected_occurrences()
            
            # Update text and selections
            self._update_text_and_selections(new_content, new_selections)
            
            return 'break'  # Prevent default behavior
        except Exception as e:
            # If anything goes wrong, let the default behavior handle it
            logger.error(f"Error in multi-cursor paste operation: {e}")
            pass
    
    def _handle_printable_character(self, char):
        """Handle printable character in multi-cursor mode."""
        try:
            # Add the character to new text
            self._new_text += char
            
            # Replace only selected occurrences and get new positions
            new_content, new_selections = self._replace_selected_occurrences()
            
            # Update text and selections
            self._update_text_and_selections(new_content, new_selections)
            
            return 'break'  # Prevent default behavior
        except Exception as e:
            # If anything goes wrong, let the default behavior handle it
            logger.error(f"Error in printable character handling: {e}")
            pass
    
    def get_selections(self) -> List[Tuple[str, str]]:
        """Get the current selections.
        
        Returns:
            List of (start, end) tuples representing the selections
        """
        return self._selections
    
    def clear_selections(self):
        """Clear all selections."""
        self._selections = []
        self._selected_text = ""
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
