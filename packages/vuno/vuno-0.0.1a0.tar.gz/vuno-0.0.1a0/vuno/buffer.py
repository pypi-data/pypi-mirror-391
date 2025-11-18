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
    
    def search(self, query, from_current=True):
        """Search for text and move cursor to match."""
        if not query:
            return None
        
        start_y = self.cursor_y if from_current else 0
        start_x = self.cursor_x + 1 if from_current else 0
        
        # Search from current position
        for y in range(start_y, len(self.lines)):
            x = start_x if y == start_y else 0
            pos = self.lines[y].find(query, x)
            
            if pos != -1:
                self.cursor_y = y
                self.cursor_x = pos
                return f"Found: {query}"
        
        # Wrap search from beginning
        for y in range(0, start_y + 1):
            end_x = start_x if y == start_y else len(self.lines[y])
            pos = self.lines[y].find(query, 0, end_x)
            
            if pos != -1:
                self.cursor_y = y
                self.cursor_x = pos
                return f"Found: {query} (wrapped)"
        
        return f"Not found: {query}"