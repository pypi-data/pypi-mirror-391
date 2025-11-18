"""
Configuration settings for Vuno editor.
"""

class Config:
    """Editor configuration."""

    def __init__(self):
        # Display settings
        self.show_line_numbers = False
        self.tab_width = 4
        self.wrap_lines = False

        # Editor behavior
        self.auto_indent = True
        self.trim_trailing_whitespace = False

        # UI settings
        self.show_status_bar = True
        self.show_help_bar = True

        # Search settings
        self.case_sensitive_search = False

        # Undo settings
        self.max_undo_levels = 100

    def toggle_line_numbers(self):
        """Toggle line numbers on/off."""
        self.show_line_numbers = not self.show_line_numbers
        return self.show_line_numbers