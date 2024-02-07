"""
Preprocessing Federal Register API results.
"""

__all__ = [
    "agencies", 
    "dockets", 
    "documents", 
    "fields", 
    "presidents", 
    "rin", 
    "utils", 
    ]

from .agencies import AgencyMetadata, AgencyData

from .dockets import RegsDotGovData, Dockets

from .documents import process_documents

from .fields import FieldData

from .presidents import Presidents

from .rin import RegInfoData

from .utils import *
