"""
Making requests from the Federal Register API.
"""

from .duplicates import identify_duplicates, remove_duplicates

from .format_dates import DateFormatter, DateFormatError

from .get_documents import (
    QueryError,
    get_documents_by_date, 
    get_documents_by_number, 
    parse_document_numbers, 
)

__all__ = [
    "identify_duplicates", 
    "remove_duplicates",
    "DateFormatter", 
    "DateFormatError", 
    "QueryError",
    "get_documents_by_date", 
    "get_documents_by_number", 
    "parse_document_numbers", 
    ]
