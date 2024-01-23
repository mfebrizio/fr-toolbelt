"""
Preprocessing Federal Register API results.
"""

__all__ = [
    "agencies", 
    "dates", 
    "dockets", 
    "duplicates", 
    "presidents", 
    "rin", 
    "utils", 
    ]

from .agencies import *

from .dates import *

from .dockets import *

from .duplicates import *

from .presidents import *

from .rin import *

from .utils import *
