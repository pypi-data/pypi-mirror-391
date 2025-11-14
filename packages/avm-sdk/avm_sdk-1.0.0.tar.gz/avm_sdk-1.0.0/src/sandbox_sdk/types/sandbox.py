# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Sandbox", "Volume"]


class Volume(BaseModel):
    mount_path: str
    """Mount path in the container"""

    volume_id: str
    """Volume ID"""

    volume_name: str
    """Volume name"""


class Sandbox(BaseModel):
    id: str
    """Sandbox ID"""

    cpu: float
    """CPU count"""

    created_at: str
    """Creation timestamp"""

    memory: float
    """Memory size in MB"""

    name: str
    """Sandbox name"""

    status: str
    """Sandbox status"""

    volumes: Optional[List[Volume]] = None
    """Volumes mounted on this sandbox"""
