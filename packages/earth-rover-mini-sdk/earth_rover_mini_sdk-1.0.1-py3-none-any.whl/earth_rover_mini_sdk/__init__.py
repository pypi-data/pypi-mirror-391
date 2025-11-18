# empty file, created __init__.py so pip recognizes the directory as a package.
from .api import EarthRoverMini_API

# Define the package version (useful for users and packaging)
__version__ = "1.0.1"  # Use your actual version number

# Optionally, you can define __all__ to explicitly control
# what is imported when a user does 'from earth_rover_mini_sdk import *'
__all__ = [
    "EarthRoverMini_API"
]