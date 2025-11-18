"""
UI and display management using curses.
"""

import curses

class UI:
    """Manages the terminal UI using curses."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.text_height = self.height - 3  # Reserve space for status and help
        
        # Initialize colors
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        # Disable cursor blinking if possible
        curses.curs_set(1)
    
    def refresh_size(self):
        """Update terminal size."""
        self.height, self.width = self.stdscr.getmaxyx()
        self.text_height = self.height - 3
    
    def draw_text(self, buffer):
        """Draw the text buffer."""
        # Adjust scroll offset
        if buffer.cursor_y < buffer.offset_y:
            buffer.offset_y = buffer.cursor_y
        elif buffer.cursor_y >= buffer.offset_y + self.text_height:
            buffer.offset_y = buffer.cursor_y - self.text_height + 1
        
        # Draw lines
        for i in range(self.text_height):
            line_idx = i + buffer.offset_y
            self.stdscr.move(i, 0)
            self.stdscr.clrtoeol()
            
            if line_idx < len(buffer.lines):
                line = buffer.lines[line_idx]
                # Truncate line if too long
                display_line = line[:self.width]
                self.stdscr.addstr(i, 0, display_line)
    
    def draw_status_bar(self, buffer, message=""):
        """Draw the status bar."""
        status_y = self.height - 2
        
        # Create status text
        modified = " [Modified]" if buffer.modified else ""
        filename = buffer.filename or "[New File]"
        position = f"Ln {buffer.cursor_y + 1}, Col {buffer.cursor_x + 1}"
        
        status = f" {filename}{modified}"
        
        # Draw status bar
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.move(status_y, 0)
        self.stdscr.clrtoeol()
        
        # Left side - filename and modified status
        self.stdscr.addstr(status_y, 0, status[:self.width - len(position) - 1])
        
        # Right side - cursor position
        if len(status) < self.width - len(position):
            self.stdscr.addstr(status_y, self.width - len(position), position)
        
        self.stdscr.attroff(curses.color_pair(1))
        
        # Message line
        self.stdscr.move(status_y + 1, 0)
        self.stdscr.clrtoeol()
        if message:
            self.stdscr.addstr(status_y + 1, 0, message[:self.width - 1])
    
    def draw_help_bar(self):
        """Draw the help bar at the bottom."""
        help_y = self.height - 1
        help_text = "^X Exit  ^O Save  ^W Where Is  ^K Cut  ^U Paste  ^G Help"
        
        self.stdscr.move(help_y, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(help_y, 0, help_text[:self.width - 1])
    
    def move_cursor(self, buffer):
        """Move the terminal cursor to buffer cursor position."""
        screen_y = buffer.cursor_y - buffer.offset_y
        self.stdscr.move(screen_y, buffer.cursor_x)
    
    def get_input(self, prompt):
        """Get user input for commands."""
        status_y = self.height - 2
        
        # Draw prompt
        self.stdscr.move(status_y + 1, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(status_y + 1, 0, prompt)
        
        # Enable echo and get input
        curses.echo()
        curses.curs_set(1)
        
        self.stdscr.move(status_y + 1, len(prompt))
        input_str = self.stdscr.getstr(status_y + 1, len(prompt), self.width - len(prompt) - 1)
        
        curses.noecho()
        
        return input_str.decode('utf-8')
    
    def show_message(self, message):
        """Show a message on the message line."""
        status_y = self.height - 2
        self.stdscr.move(status_y + 1, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(status_y + 1, 0, message[:self.width - 1])
        self.stdscr.refresh()
    
    def confirm(self, prompt):
        """Ask for yes/no confirmation."""
        response = self.get_input(f"{prompt} (y/n): ").lower()
        return response.startswith('y')