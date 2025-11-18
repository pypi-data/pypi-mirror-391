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
from .config import Config


class Editor:
    """Main Vuno editor class."""
    
    def __init__(self, filename=None):
        self.buffer = Buffer(filename)
        self.config = Config()
        self.message = ""
        self.show_stats = False
        
        # Create the text area
        self.text_area = TextArea(
            text=self.buffer.get_text(),
            multiline=True,
            scrollbar=True,
            line_numbers=self.config.show_line_numbers,
            wrap_lines=self.config.wrap_lines,
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
        
        # File operations
        @kb.add('c-x')
        def exit_editor(event):
            """Exit editor (Ctrl+X)."""
            self._handle_exit()
        
        @kb.add('c-o')
        def save_file(event):
            """Save file (Ctrl+O)."""
            self._handle_save()
        
        # Search
        @kb.add('c-w')
        def search_text(event):
            """Search (Ctrl+W)."""
            self._handle_search()
        
        @kb.add('c-n')
        def search_next(event):
            """Find next (Ctrl+N)."""
            self._handle_search_next()
        
        # Edit operations
        @kb.add('c-z')
        def undo_action(event):
            """Undo (Ctrl+Z)."""
            self._handle_undo()
        
        @kb.add('c-y')
        def redo_action(event):
            """Redo (Ctrl+Y)."""
            self._handle_redo()
        
        @kb.add('c-k')
        def cut_line(event):
            """Cut line (Ctrl+K)."""
            self._handle_cut()
        
        @kb.add('c-u')
        def paste_text(event):
            """Paste (Ctrl+U)."""
            self._handle_paste()
        
        # Navigation
        @kb.add('c-t')
        def goto_line(event):
            """Go to line (Ctrl+T)."""
            self._handle_goto_line()
        
        # View
        @kb.add('c-l')
        def toggle_line_numbers(event):
            """Toggle line numbers (Ctrl+L)."""
            self._toggle_line_numbers()
        
        # Help
        @kb.add('c-g')
        def show_help(event):
            """Show help (Ctrl+G)."""
            self._show_help()
        
        @kb.add('c-s')
        def show_statistics(event):
            """Show statistics (Ctrl+S)."""
            self._show_statistics()
        
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
        
        # Get stats
        stats = self.buffer.get_stats()
        
        return f" {filename}{modified} | Ln {line}/{stats['lines']}, Col {col} | {stats['chars']} chars"
    
    def _get_message_text(self):
        """Get message bar text."""
        return f" {self.message}" if self.message else ""
    
    def _get_help_text(self):
        """Get help bar text."""
        return " ^X Exit ^O Save ^W Search ^G Help ^L LineNum ^K Cut ^U Paste | Vuno v0.0.2a"
    
    def _sync_from_textarea(self):
        """Sync buffer from text area."""
        text = self.text_area.text
        old_text = '\n'.join(self.buffer.lines)
        
        self.buffer.lines = text.splitlines() if text else ['']
        if not self.buffer.lines:
            self.buffer.lines = ['']
        
        # Update cursor position
        doc = self.text_area.document
        text_before = text[:doc.cursor_position] if text else ''
        self.buffer.cursor_y = text_before.count('\n')
        lines_before = text_before.split('\n')
        self.buffer.cursor_x = len(lines_before[-1]) if lines_before else 0
        
        # Mark as modified if changed
        if text != old_text:
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
            self._prompt_for_filename()
        else:
            self._do_save()
    
    def _do_save(self):
        """Actually save the file."""
        try:
            self.buffer.save_file()
            stats = self.buffer.get_stats()
            self.message = f"[ Wrote {stats['lines']} line(s), {stats['chars']} chars ]"
        except Exception as e:
            self.message = f"Error: {e}"
    
    def _handle_undo(self):
        """Handle undo command."""
        if self.buffer.undo():
            self._sync_to_textarea()
            self.message = "Undo successful"
        else:
            self.message = "Nothing to undo"
    
    def _handle_redo(self):
        """Handle redo command."""
        if self.buffer.redo():
            self._sync_to_textarea()
            self.message = "Redo successful"
        else:
            self.message = "Nothing to redo"
    
    def _handle_cut(self):
        """Handle cut line command."""
        self._sync_from_textarea()
        if self.buffer.cut_line():
            self._sync_to_textarea()
            self.message = "Line cut to clipboard"
        else:
            self.message = "Nothing to cut"
    
    def _handle_paste(self):
        """Handle paste command."""
        self._sync_from_textarea()
        if self.buffer.paste():
            self._sync_to_textarea()
            self.message = "Pasted from clipboard"
        else:
            self.message = "Clipboard is empty"
    
    def _handle_search_next(self):
        """Handle search next command."""
        self._sync_from_textarea()
        result = self.buffer.search_next()
        self.message = result
        self._sync_to_textarea()
    
    def _toggle_line_numbers(self):
        """Toggle line numbers."""
        self.config.toggle_line_numbers()
        self.text_area.line_numbers = self.config.show_line_numbers
        status = "on" if self.config.show_line_numbers else "off"
        self.message = f"Line numbers: {status}"
    
    def _show_statistics(self):
        """Show buffer statistics."""
        stats = self.buffer.get_stats()
        self.message = f"Lines: {stats['lines']} | Chars: {stats['chars']} | Undo: {len(self.buffer.undo_stack)}"
    
    def _handle_goto_line(self):
        """Handle go to line command."""
        self._sync_from_textarea()
        
        input_area = TextArea(
            prompt="Go to line: ",
            multiline=False,
        )
        
        input_kb = KeyBindings()
        
        @input_kb.add('enter')
        def accept(event):
            try:
                line_num = int(input_area.text.strip())
                if self.buffer.goto_line(line_num):
                    self._sync_to_textarea()
                    self.message = f"Jumped to line {line_num}"
                else:
                    self.message = f"Invalid line number: {line_num}"
            except ValueError:
                self.message = "Invalid number"
            self._restore_main_layout()
        
        @input_kb.add('c-c')
        @input_kb.add('c-g')
        def cancel(event):
            self.message = "Cancelled"
            self._restore_main_layout()
        
        self._show_input_dialog(input_area, input_kb)
    
    def _prompt_for_filename(self):
        """Prompt user for filename."""
        input_area = TextArea(
            prompt="File Name to Write: ",
            multiline=False,
        )
        
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
        
        self._show_input_dialog(input_area, input_kb)
    
    def _handle_search(self):
        """Handle search command."""
        self._sync_from_textarea()
        
        input_area = TextArea(
            prompt="Search: ",
            multiline=False,
            text=self.buffer.last_search,
        )
        
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
        
        self._show_input_dialog(input_area, input_kb)
    
    def _handle_exit(self):
        """Handle exit command."""
        self._sync_from_textarea()
        
        if self.buffer.modified:
            self._prompt_save_on_exit()
        else:
            self.app.exit()
    
    def _prompt_save_on_exit(self):
        """Prompt to save on exit."""
        input_area = TextArea(
            prompt="Save modified buffer? (y/n): ",
            multiline=False,
        )
        
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
        
        self._show_input_dialog(input_area, input_kb)
    
    def _prompt_for_filename_and_exit(self):
        """Prompt for filename then exit."""
        input_area = TextArea(
            prompt="File Name to Write: ",
            multiline=False,
        )
        
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
        
        self._show_input_dialog(input_area, input_kb)
    
    def _show_input_dialog(self, input_area, input_kb):
        """Show an input dialog."""
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
        help_text = [
            "Vuno v0.0.2a - Keyboard Shortcuts:",
            "^X=Exit ^O=Save ^W=Search ^N=Next",
            "^Z=Undo ^Y=Redo ^K=Cut ^U=Paste",
            "^T=GoToLine ^L=LineNum ^S=Stats ^G=Help"
        ]
        self.message = " | ".join(help_text)
    
    def run(self):
        """Run the editor."""
        try:
            self.app.run()
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()