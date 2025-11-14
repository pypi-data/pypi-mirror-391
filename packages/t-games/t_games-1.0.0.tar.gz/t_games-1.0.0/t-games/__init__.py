"""
Games Collection
A collection of classic games playable in your terminal.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from . import main
from . import tictactoe
from . import chess
from . import sudoku
from . import adventure

__all__ = [
    "main",
    "tictactoe",
    "chess",
    "sudoku",
    "adventure",
]
