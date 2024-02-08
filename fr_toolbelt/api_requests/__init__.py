"""
Making requests from the Federal Register API.
"""

__all__ = [
    "identify_duplicates", 
    "remove_duplicates",
    "DateFormatter", 
    "DateFormatError", 
    "get_documents_by_date", 
    "get_documents_by_number", 
    "QueryError",
    ]


from .duplicates import identify_duplicates, remove_duplicates

from .format_dates import DateFormatter, DateFormatError

from .get_documents import get_documents_by_date, get_documents_by_number, QueryError
