# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .volume import Volume
from .._models import BaseModel
from .pagination import Pagination

__all__ = ["VolumeListResponse", "Data", "DataMountedBy"]


class DataMountedBy(BaseModel):
    sandbox_id: str
    """Sandbox ID using this volume"""

    sandbox_name: str
    """Sandbox name using this volume"""


class Data(Volume):
    id: str  # type: ignore
    """Volume or Snapshot ID"""

    created_at: str  # type: ignore
    """Creation timestamp"""

    in_use: bool
    """
    Whether the volume is currently mounted by a sandbox (always false for
    snapshots)
    """

    name: str  # type: ignore
    """Volume or Snapshot name"""

    size: str  # type: ignore
    """Volume size (for volumes) or source volume size (for snapshots)"""

    status: str  # type: ignore
    """Volume status (Pending/Bound/Lost) or Snapshot status (Ready/Pending)"""

    type: Literal["volume", "snapshot"]
    """Type: 'volume' for persistent volumes, 'snapshot' for point-in-time snapshots"""

    mounted_by: Optional[DataMountedBy] = None
    """Sandbox information if volume is in use (only for volumes)"""

    source_volume_id: Optional[str] = None
    """Source volume ID for snapshots"""

    source_volume_name: Optional[str] = None
    """Source volume name for snapshots"""


class VolumeListResponse(BaseModel):
    data: List[Data]
    """Array of volumes"""

    pagination: Pagination
    """Pagination metadata"""
