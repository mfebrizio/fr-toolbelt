"""
Preprocessing Federal Register API results.
"""

__all__ = [
    "agencies", 
    "dockets", 
    "documents", 
    "duplicates", 
    "presidents", 
    "rin", 
    "utils", 
    ]

from .agencies import AgencyMetadata, AgencyData

from .dockets import RegsDotGovData, Dockets

from .documents import process_documents

from .duplicates import *

from .presidents import Presidents

from .rin import RegInfoData

from .utils import *
