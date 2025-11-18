"""
Text buffer management for the nano editor.
"""

class Buffer:
    """Manages the text content and cursor position."""
    
    def __init__(self, filename=None):
        self.filename = filename
        self.lines = ['']
        self.cursor_x = 0
        self.cursor_y = 0
        self.modified = False

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 100

        # Clipboard
        self.clipboard = []

        # Last search
        self.last_search = ""
        self.last_search_pos = (0, 0)
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        """Load content from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self.lines = content.splitlines() if content else ['']
                if not self.lines:
                    self.lines = ['']
            self.filename = filename
            self.modified = False
            return True
        except FileNotFoundError:
            self.lines = ['']
            self.filename = filename
            return False
        except Exception as e:
            raise Exception(f"Error loading file: {e}")
    
    def save_file(self, filename=None):
        """Save content to a file."""
        if filename:
            self.filename = filename
        
        if not self.filename:
            raise ValueError("No filename specified")
        
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            return True
        except Exception as e:
            raise Exception(f"Error saving file: {e}")
    
    def insert_char(self, char):
        """Insert a character at cursor position."""
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = (
            line[:self.cursor_x] + char + line[self.cursor_x:]
        )
        self.cursor_x += 1
        self.modified = True
    
    def delete_char(self):
        """Delete character before cursor (backspace)."""
        if self.cursor_x > 0:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = (
                line[:self.cursor_x - 1] + line[self.cursor_x:]
            )
            self.cursor_x -= 1
            self.modified = True
        elif self.cursor_y > 0:
            # Merge with previous line
            self.cursor_x = len(self.lines[self.cursor_y - 1])
            self.lines[self.cursor_y - 1] += self.lines[self.cursor_y]
            self.lines.pop(self.cursor_y)
            self.cursor_y -= 1
            self.modified = True
    
    def delete_char_forward(self):
        """Delete character at cursor (delete key)."""
        line = self.lines[self.cursor_y]
        if self.cursor_x < len(line):
            self.lines[self.cursor_y] = (
                line[:self.cursor_x] + line[self.cursor_x + 1:]
            )
            self.modified = True
        elif self.cursor_y < len(self.lines) - 1:
            # Merge with next line
            self.lines[self.cursor_y] += self.lines[self.cursor_y + 1]
            self.lines.pop(self.cursor_y + 1)
            self.modified = True
    
    def insert_newline(self):
        """Insert a new line at cursor position."""
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[:self.cursor_x]
        self.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
        self.cursor_y += 1
        self.cursor_x = 0
        self.modified = True
    
    def move_cursor_left(self):
        """Move cursor left."""
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = len(self.lines[self.cursor_y])
    
    def move_cursor_right(self):
        """Move cursor right."""
        if self.cursor_x < len(self.lines[self.cursor_y]):
            self.cursor_x += 1
        elif self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            self.cursor_x = 0
    
    def move_cursor_up(self):
        """Move cursor up."""
        if self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
    
    def move_cursor_down(self):
        """Move cursor down."""
        if self.cursor_y < len(self.lines) - 1:
            self.cursor_y += 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
    
    def move_to_line_start(self):
        """Move cursor to start of line."""
        self.cursor_x = 0
    
    def move_to_line_end(self):
        """Move cursor to end of line."""
        self.cursor_x = len(self.lines[self.cursor_y])
    
    def get_text(self):
        """Get all text content."""
        return '\n'.join(self.lines)
    
    def search(self, query, from_current=True, next_match=False):
        """Search for text and move cursor to match."""
        if not query:
            return None

        self.last_search = query
        
        if next_match and self.last_search_pos:
            start_y, start_x = self.last_search_pos
            # Move to next character
            start_x += 1
        elif from_current:
            start_y = self.cursor_y
            start_x = self.cursor_x + 1
        else:
            start_y = 0
            start_x = 0
        
        # Search from current position
        for y in range(start_y, len(self.lines)):
            x = start_x if y == start_y else 0
            pos = self.lines[y].find(query, x)
            
            if pos != -1:
                self.cursor_y = y
                self.cursor_x = pos
                self.last_search_pos = (y, pos)
                return f"Found: {query}"
        
        # Wrap search from beginning
        for y in range(0, start_y + 1):
            end_x = start_x if y == start_y else len(self.lines[y])
            pos = self.lines[y].find(query, 0, end_x)
            
            if pos != -1:
                self.cursor_y = y
                self.cursor_x = pos
                self.last_search_pos = (y, pos)
                return f"Found: {query} (wrapped)"
        
        return f"Not found: {query}"
    
    def search_next(self):
        """Find next occurrence of last search."""
        if self.last_search:
            return self.search(self.last_search, from_current=True, next_match=True)
        return "No previous search"
    
    def cut_line(self):
        """Cut current line to clipboard."""
        if self.cursor_y < len(self.lines):
            self.save_state()
            self.clipboard = [self.lines[self.cursor_y]]
            self.lines.pop(self.cursor_y)

            if not self.lines:
                self.lines = ['']

            if self.cursor_y >= len(self.lines):
                self.cursor_y = len(self.lines) - 1

            self.cursor_x = 0
            self.modified = True
            return True
        return False
    
    def copy_line(self):
        """Copy current line to clipboard."""
        if self.cursor_y < len(self.lines):
            self.clipboard = [self.lines[self.cursor_y]]
            return True
        return False
    
    def paste(self):
        """Paste clipboard content."""
        if not self.clipboard:
            return False
        
        self.save_state()

        for i, line in enumerate(self.clipboard):
            self.lines.insert(self.cursor_y + i + 1, line)

        self.cursor_y += len(self.clipboard)
        self.cursor_x = 0
        self.modified = True
        return True
    
    def save_state(self):
        """Save current state for undo."""
        state = {
            'lines': [line for line in self.lines],
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
        }
        self.undo_stack.append(state)

        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

        # Clear redo stack on new action
        self.redo_stack.clear()

    def undo(self):
        """Undo last action."""
        if not self.undo_stack:
            return False
        
        # Save current state to redo
        current_state = {
            'lines': [line for line in self.lines],
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
        }
        self.redo_stack.append(current_state)

        # Restore previous state
        state = self.undo_stack.pop()
        self.lines = state['lines']
        self.cursor_x = state['cursor_x']
        self.cursor_y = state['cursor_y']

        return True
    
    def redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            return False
        
        # Save current state to undo
        current_state = {
            'lines': [line for line in self.lines],
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
        }
        self.undo_stack.append(current_state)

        # Restore redo state
        state = self.redo_stack.pop()
        self.lines = state['lines']
        self.cursor_x = state['cursor_x']
        self.cursor_y = state['cursor_y']

        return True
    
    def goto_line(self, line_number):
        """Go to specific line number."""
        if 1 <= line_number <= len(self.lines):
            self.cursor_y = line_number - 1
            self.cursor_x = 0
            return True
        return False
    
    def get_stats(self):
        """Get buffer statistics."""
        total_lines = len(self.lines)
        total_chars = sum(len(line) for line in self.lines)
        current_line = self.cursor_y + 1
        current_col = self.cursor_x + 1

        return {
            'lines': total_lines,
            'chars': total_chars,
            'current_line': current_line,
            'current_col': current_col,
        }