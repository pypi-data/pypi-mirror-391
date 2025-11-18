"""
Main editor class using prompt_toolkit.
"""

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.dimension import Dimension

from .buffer import Buffer


class Editor:
    """Main Vuno editor class."""
    
    def __init__(self, filename=None):
        self.buffer = Buffer(filename)
        self.message = ""
        
        # Create the text area with its own key bindings
        self.text_area = TextArea(
            text=self.buffer.get_text(),
            multiline=True,
            scrollbar=True,
            line_numbers=False,
            wrap_lines=False,
        )
        
        # Create custom key bindings
        self.kb = self._create_key_bindings()
        
        # Create status bar
        self.status_bar = Window(
            content=FormattedTextControl(self._get_status_text),
            height=Dimension.exact(1),
            style='reverse',
        )
        
        # Create message bar
        self.message_bar = Window(
            content=FormattedTextControl(self._get_message_text),
            height=Dimension.exact(1),
        )
        
        # Create help bar
        self.help_bar = Window(
            content=FormattedTextControl(self._get_help_text),
            height=Dimension.exact(1),
        )
        
        # Create main layout
        self.root_container = HSplit([
            self.text_area,
            self.status_bar,
            self.message_bar,
            self.help_bar,
        ])
        
        self.layout = Layout(self.root_container)
        
        # Create application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True,
        )
    
    def _create_key_bindings(self):
        """Create key bindings for the editor."""
        kb = KeyBindings()
        
        @kb.add('c-x')
        def exit_editor(event):
            """Exit editor (Ctrl+X)."""
            self._handle_exit()
        
        @kb.add('c-o')
        def save_file(event):
            """Save file (Ctrl+O)."""
            self._handle_save()
        
        @kb.add('c-w')
        def search_text(event):
            """Search (Ctrl+W)."""
            self._handle_search()
        
        @kb.add('c-g')
        def show_help(event):
            """Show help (Ctrl+G)."""
            self._show_help()
        
        return kb
    
    def _get_status_text(self):
        """Get status bar text."""
        # Sync from text area
        self._sync_from_textarea()
        
        modified = " [Modified]" if self.buffer.modified else ""
        filename = self.buffer.filename or "[New File]"
        
        # Get cursor position from text area
        doc = self.text_area.document
        line = doc.cursor_position_row + 1
        col = doc.cursor_position_col + 1
        
        return f" {filename}{modified} | Ln {line}, Col {col}"
    
    def _get_message_text(self):
        """Get message bar text."""
        return f" {self.message}" if self.message else ""
    
    def _get_help_text(self):
        """Get help bar text."""
        return " ^X Exit  ^O Save  ^W Search  ^G Help | Vuno v0.0.1a"
    
    def _sync_from_textarea(self):
        """Sync buffer from text area."""
        text = self.text_area.text
        self.buffer.lines = text.splitlines() if text else ['']
        if not self.buffer.lines:
            self.buffer.lines = ['']
        
        # Mark as modified if changed
        if text != self.buffer.get_text():
            self.buffer.modified = True
    
    def _sync_to_textarea(self):
        """Sync text area from buffer."""
        text = self.buffer.get_text()
        
        # Calculate cursor position
        cursor_pos = 0
        for i in range(min(self.buffer.cursor_y, len(self.buffer.lines))):
            if i < len(self.buffer.lines):
                cursor_pos += len(self.buffer.lines[i]) + 1
        
        if self.buffer.cursor_y < len(self.buffer.lines):
            cursor_pos += min(self.buffer.cursor_x, len(self.buffer.lines[self.buffer.cursor_y]))
        
        self.text_area.document = Document(
            text=text,
            cursor_position=min(cursor_pos, len(text))
        )
    
    def _handle_save(self):
        """Handle save command."""
        self._sync_from_textarea()
        
        if not self.buffer.filename:
            # Need to ask for filename
            self._prompt_for_filename()
        else:
            self._do_save()
    
    def _do_save(self):
        """Actually save the file."""
        try:
            self.buffer.save_file()
            lines = len(self.buffer.lines)
            self.message = f"[ Wrote {lines} line(s) ]"
        except Exception as e:
            self.message = f"Error: {e}"
    
    def _prompt_for_filename(self):
        """Prompt user for filename."""
        from prompt_toolkit.shortcuts import input_dialog
        
        # Create a simple input area
        input_area = TextArea(
            prompt="File Name to Write: ",
            multiline=False,
        )
        
        # Create input key bindings
        input_kb = KeyBindings()
        
        @input_kb.add('enter')
        def accept(event):
            filename = input_area.text.strip()
            if filename:
                self.buffer.filename = filename
                self._do_save()
            else:
                self.message = "Cancelled"
            self._restore_main_layout()
        
        @input_kb.add('c-c')
        @input_kb.add('c-g')
        def cancel(event):
            self.message = "Cancelled"
            self._restore_main_layout()
        
        # Save current layout
        self._saved_layout = self.root_container
        self._saved_kb = self.app.key_bindings
        
        # Create new layout with input
        self.root_container = HSplit([
            self.text_area,
            self.status_bar,
            input_area,
            self.help_bar,
        ])
        
        self.layout.container = self.root_container
        self.app.key_bindings = input_kb
        self.app.layout.focus(input_area)
    
    def _handle_search(self):
        """Handle search command."""
        self._sync_from_textarea()
        
        # Create search input
        input_area = TextArea(
            prompt="Search: ",
            multiline=False,
        )
        
        # Create input key bindings
        input_kb = KeyBindings()
        
        @input_kb.add('enter')
        def accept(event):
            query = input_area.text.strip()
            if query:
                result = self.buffer.search(query)
                self.message = result or "Not found"
                self._sync_to_textarea()
            else:
                self.message = "Cancelled"
            self._restore_main_layout()
        
        @input_kb.add('c-c')
        @input_kb.add('c-g')
        def cancel(event):
            self.message = "Cancelled"
            self._restore_main_layout()
        
        # Save current layout
        self._saved_layout = self.root_container
        self._saved_kb = self.app.key_bindings
        
        # Create new layout with input
        self.root_container = HSplit([
            self.text_area,
            self.status_bar,
            input_area,
            self.help_bar,
        ])
        
        self.layout.container = self.root_container
        self.app.key_bindings = input_kb
        self.app.layout.focus(input_area)
    
    def _handle_exit(self):
        """Handle exit command."""
        self._sync_from_textarea()
        
        if self.buffer.modified:
            # Ask to save
            self._prompt_save_on_exit()
        else:
            self.app.exit()
    
    def _prompt_save_on_exit(self):
        """Prompt to save on exit."""
        input_area = TextArea(
            prompt="Save modified buffer? (y/n): ",
            multiline=False,
        )
        
        # Create input key bindings
        input_kb = KeyBindings()
        
        @input_kb.add('enter')
        def accept(event):
            response = input_area.text.strip().lower()
            if response.startswith('y'):
                if self.buffer.filename:
                    self._do_save()
                    self.app.exit()
                else:
                    self._restore_main_layout()
                    self._prompt_for_filename_and_exit()
            elif response.startswith('n'):
                self.app.exit()
            else:
                self.message = "Cancelled"
                self._restore_main_layout()
        
        @input_kb.add('c-c')
        @input_kb.add('c-g')
        def cancel(event):
            self.message = "Cancelled"
            self._restore_main_layout()
        
        # Save current layout
        self._saved_layout = self.root_container
        self._saved_kb = self.app.key_bindings
        
        # Create new layout with input
        self.root_container = HSplit([
            self.text_area,
            self.status_bar,
            input_area,
            self.help_bar,
        ])
        
        self.layout.container = self.root_container
        self.app.key_bindings = input_kb
        self.app.layout.focus(input_area)
    
    def _prompt_for_filename_and_exit(self):
        """Prompt for filename then exit."""
        input_area = TextArea(
            prompt="File Name to Write: ",
            multiline=False,
        )
        
        # Create input key bindings
        input_kb = KeyBindings()
        
        @input_kb.add('enter')
        def accept(event):
            filename = input_area.text.strip()
            if filename:
                self.buffer.filename = filename
                self._do_save()
                self.app.exit()
            else:
                self.message = "Cancelled"
                self._restore_main_layout()
        
        @input_kb.add('c-c')
        @input_kb.add('c-g')
        def cancel(event):
            self.message = "Cancelled"
            self._restore_main_layout()
        
        # Create new layout with input
        self.root_container = HSplit([
            self.text_area,
            self.status_bar,
            input_area,
            self.help_bar,
        ])
        
        self.layout.container = self.root_container
        self.app.key_bindings = input_kb
        self.app.layout.focus(input_area)
    
    def _restore_main_layout(self):
        """Restore the main layout."""
        if hasattr(self, '_saved_layout'):
            self.root_container = self._saved_layout
            self.layout.container = self.root_container
        
        if hasattr(self, '_saved_kb'):
            self.app.key_bindings = self._saved_kb
        
        self.app.layout.focus(self.text_area)
    
    def _show_help(self):
        """Show help message."""
        self.message = "^X=Exit ^O=Save ^W=Search | Arrow keys=Navigate | Vuno Text Editor"
    
    def run(self):
        """Run the editor."""
        try:
            self.app.run()
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()