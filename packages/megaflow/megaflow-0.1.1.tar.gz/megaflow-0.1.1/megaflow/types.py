"""
Type aliases for Megaflow function data model.

All inter-function communication flows as arrays of objects (Items).
Each object is a plain JSON-like dictionary (Item).
"""

from typing import Any, Dict, List, TypeAlias

Item: TypeAlias = Dict[str, Any]
Items: TypeAlias = List[Item]

