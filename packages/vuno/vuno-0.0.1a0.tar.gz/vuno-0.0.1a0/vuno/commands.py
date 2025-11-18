"""
Command handlers for editor operations.
"""

class Commands:
    """Handles editor commands."""
    
    @staticmethod
    def save(editor):
        """Save the current file."""
        try:
            if not editor.buffer.filename:
                filename = editor.ui.get_input("File Name to Write: ")
                if not filename:
                    editor.message = "Cancelled"
                    return False
                editor.buffer.filename = filename
            
            editor.buffer.save_file()
            lines = len(editor.buffer.lines)
            editor.message = f"[ Wrote {lines} line(s) ]"
            return True
        except Exception as e:
            editor.message = f"Error: {e}"
            return False
    
    @staticmethod
    def exit(editor):
        """Exit the editor."""
        if editor.buffer.modified:
            if editor.ui.confirm("Save modified buffer?"):
                if Commands.save(editor):
                    return True
            else:
                return True
        else:
            return True
        return False
    
    @staticmethod
    def search(editor):
        """Search for text."""
        query = editor.ui.get_input("Search: ")
        if not query:
            editor.message = "Cancelled"
            return
        
        buffer = editor.buffer
        start_y = buffer.cursor_y
        start_x = buffer.cursor_x + 1
        
        # Search from current position
        for y in range(start_y, len(buffer.lines)):
            x = start_x if y == start_y else 0
            pos = buffer.lines[y].find(query, x)
            
            if pos != -1:
                buffer.cursor_y = y
                buffer.cursor_x = pos
                editor.message = f"Found: {query}"
                return
        
        # Wrap search from beginning
        for y in range(0, start_y + 1):
            end_x = start_x if y == start_y else len(buffer.lines[y])
            pos = buffer.lines[y].find(query, 0, end_x)
            
            if pos != -1:
                buffer.cursor_y = y
                buffer.cursor_x = pos
                editor.message = f"Found: {query} (wrapped)"
                return
        
        editor.message = f"Not found: {query}"
    
    @staticmethod
    def show_help(editor):
        """Show help information."""
        editor.message = "Help: ^X=Exit ^O=Save ^W=Search | Arrow keys to navigate"