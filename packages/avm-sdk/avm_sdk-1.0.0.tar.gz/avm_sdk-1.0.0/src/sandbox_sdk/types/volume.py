# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Volume"]


class Volume(BaseModel):
    id: str
    """Volume ID"""

    created_at: str
    """Creation timestamp"""

    name: str
    """Volume name"""

    size: str
    """Volume size"""

    status: str
    """Volume status (Pending/Bound/Lost)"""
