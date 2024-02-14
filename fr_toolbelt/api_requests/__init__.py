"""
Making requests from the Federal Register API.
"""

from .duplicates import identify_duplicates, remove_duplicates, process_duplicates, DuplicateError

from .format_dates import DateFormatter, DateFormatError

from .get_documents import (
    BASE_URL,
    BASE_PARAMS,
    DEFAULT_FIELDS, 
    QueryError,
    get_documents_by_date, 
    get_documents_by_number, 
    parse_document_numbers, 
    _retrieve_results_by_next_page
)

__all__ = [
    "identify_duplicates", 
    "remove_duplicates",
    "process_duplicates",
    "DuplicateError",
    "DateFormatter", 
    "DateFormatError", 
    "BASE_URL",
    "BASE_PARAMS",
    "DEFAULT_FIELDS",
    "QueryError",
    "get_documents_by_date", 
    "get_documents_by_number", 
    "parse_document_numbers", 
    ]
