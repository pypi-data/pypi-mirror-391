__version__ = '0.0.1'
__author__ = 'codewithzaqar'

from .editor import Editor

__all__ = ['Editor']

# Allow running as: python -m vuno
def main():
    """Entry point for the vuno command."""
    from .__main__ import main as _main
    _main()