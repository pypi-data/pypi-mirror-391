# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["VolumeCreateSnapshotResponse"]


class VolumeCreateSnapshotResponse(BaseModel):
    id: str
    """Snapshot ID"""

    consistency: str
    """Snapshot consistency level (application-consistent or crash-consistent)"""

    created_at: str
    """Creation timestamp"""

    name: str
    """Snapshot name"""

    sandbox_id: str
    """Sandbox ID that was using the volume"""

    sandbox_name: str
    """Sandbox name that was using the volume"""

    status: str
    """Snapshot status"""

    volume_id: str
    """Source volume ID"""

    volume_name: str
    """Source volume name"""
