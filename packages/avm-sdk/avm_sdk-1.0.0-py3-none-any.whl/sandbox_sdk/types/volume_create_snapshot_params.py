# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VolumeCreateSnapshotParams"]


class VolumeCreateSnapshotParams(TypedDict, total=False):
    name: Required[str]
    """Snapshot name"""

    quick: bool
    """Quick mode: Only fsfreeze (crash-consistent).

    Default: Full sync + freeze (application-consistent)
    """
