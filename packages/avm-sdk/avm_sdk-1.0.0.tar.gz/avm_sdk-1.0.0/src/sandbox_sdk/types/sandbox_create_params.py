# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["SandboxCreateParams", "Resources", "Volume"]


class SandboxCreateParams(TypedDict, total=False):
    env_vars: Dict[str, str]
    """Environment variables"""

    image: str
    """Docker image name (e.g., avmcodes/avm-default-sandbox)"""

    name: str
    """Sandbox name"""

    resources: Resources

    volumes: Iterable[Volume]
    """Volumes to attach to the sandbox"""


class Resources(TypedDict, total=False):
    cpus: int
    """Number of vCPUs"""

    memory: int
    """Memory size in MiB"""


class Volume(TypedDict, total=False):
    mount_path: Required[str]
    """Mount path in the container"""

    volume_id: Required[str]
    """Volume ID or Snapshot ID.

    If a snapshot ID is provided, a new volume will be created from the snapshot.
    """
