# This file makes `src/emotify` a Python package.
# It also "exports" the main function so users can import it easily.

# Import the main function from your translator.py file
from .emotify_text import emojify

# __all__ tells Python what functions to export when someone does `from emotify import *`
__all__ = [
    'emojify'
]

# You can also define your package version here
__version__ = "0.0.1"