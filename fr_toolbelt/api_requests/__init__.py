"""
Making requests from the Federal Register API.
"""

__all__ = [
    "duplicates", 
    "format_dates", 
    "get_documents", 
    ]


from .duplicates import *

from .format_dates import DateFormatter, DateFormatError

from .get_documents import *
