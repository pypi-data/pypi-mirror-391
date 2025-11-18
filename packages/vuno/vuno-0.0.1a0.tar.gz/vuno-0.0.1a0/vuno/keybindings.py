"""
Key bindings for the editor.
"""

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys


def create_key_bindings(editor):
    """Create key bindings for the editor."""
    kb = KeyBindings()
    
    # Exit (Ctrl+X)
    @kb.add('c-x')
    def _(event):
        editor.handle_exit()
    
    # Save (Ctrl+O)
    @kb.add('c-o')
    def _(event):
        editor.handle_save()
    
    # Search (Ctrl+W)
    @kb.add('c-w')
    def _(event):
        editor.handle_search()
    
    # Help (Ctrl+G)
    @kb.add('c-g')
    def _(event):
        editor.show_help()
    
    # Navigation
    @kb.add(Keys.Left)
    def _(event):
        editor.buffer.move_cursor_left()
    
    @kb.add(Keys.Right)
    def _(event):
        editor.buffer.move_cursor_right()
    
    @kb.add(Keys.Up)
    def _(event):
        editor.buffer.move_cursor_up()
    
    @kb.add(Keys.Down)
    def _(event):
        editor.buffer.move_cursor_down()
    
    @kb.add(Keys.Home)
    def _(event):
        editor.buffer.move_to_line_start()
    
    @kb.add(Keys.End)
    def _(event):
        editor.buffer.move_to_line_end()
    
    # Editing
    @kb.add(Keys.Backspace)
    def _(event):
        editor.buffer.delete_char()
    
    @kb.add(Keys.Delete)
    def _(event):
        editor.buffer.delete_char_forward()
    
    @kb.add(Keys.Enter)
    def _(event):
        editor.buffer.insert_newline()
    
    # Any character
    @kb.add(Keys.Any)
    def _(event):
        editor.buffer.insert_char(event.data)
    
    return kb