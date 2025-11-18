"""
Vuno Text Editor - Python Implementation (Cross-Platform)
Version: 0.0.2
"""

__version__ = '0.0.2'
__author__ = 'codewithzaqar'
__description__ = 'A lightweight terminal text editor'

from .editor import Editor

__all__ = ['Editor', '__version__', '__description__']

# Allow running as: python -m vuno
def main():
    """Entry point for the vuno command."""
    from .__main__ import main as _main
    _main()