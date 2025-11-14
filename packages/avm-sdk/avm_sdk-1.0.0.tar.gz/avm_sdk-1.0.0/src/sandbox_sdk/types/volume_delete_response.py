# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["VolumeDeleteResponse"]


class VolumeDeleteResponse(BaseModel):
    id: str

    message: str

    type: Optional[Literal["volume", "snapshot"]] = None
