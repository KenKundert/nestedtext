"""
Udif: human readable, writable, and editable data interchange format
"""

__version__ = "0.0.2"
__released__ = "2020-08-26"

from .load import loads
from .dump import dumps, BASIC_RENDERERS
from inform import Error
