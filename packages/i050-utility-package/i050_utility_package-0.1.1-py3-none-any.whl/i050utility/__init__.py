# Version of the package 
__version__ = "0.1.1" # <--- MUST BE 0.1.1 or higher

# Expose the main cleaning function directly under the package name
from .cleaner import sanitize_dataframe
