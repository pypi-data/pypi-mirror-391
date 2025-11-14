# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .sandbox import Sandbox

__all__ = ["SandboxCreateResponse"]


class SandboxCreateResponse(Sandbox):
    id: Optional[str] = None  # type: ignore
    """Sandbox ID"""

    cpu: Optional[float] = None  # type: ignore
    """CPU count"""

    created_at: Optional[str] = None  # type: ignore
    """Creation timestamp"""

    memory: Optional[float] = None  # type: ignore
    """Memory size in MB"""

    name: Optional[str] = None  # type: ignore
    """Sandbox name"""

    status: Optional[str] = None  # type: ignore
    """Sandbox status"""
