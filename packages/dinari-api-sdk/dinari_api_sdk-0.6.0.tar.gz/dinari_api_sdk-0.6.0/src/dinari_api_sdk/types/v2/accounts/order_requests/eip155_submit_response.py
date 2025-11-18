# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..order_tif import OrderTif
from ....._models import BaseModel
from ..order_side import OrderSide
from ..order_type import OrderType

__all__ = ["Eip155SubmitResponse"]


class Eip155SubmitResponse(BaseModel):
    id: str
    """ID of `EIP155OrderRequest`.

    This is the primary identifier for the `/order_requests` routes.
    """

    account_id: str
    """ID of `Account` placing the `EIP155OrderRequest`."""

    created_dt: datetime
    """Datetime at which the `EIP155OrderRequest` was created. ISO 8601 timestamp."""

    order_side: OrderSide
    """Indicates whether `Order` is a buy or sell."""

    order_tif: OrderTif
    """Indicates how long `Order` is valid for."""

    order_type: OrderType
    """Type of `Order`."""

    status: Literal["QUOTED", "PENDING", "PENDING_BRIDGE", "SUBMITTED", "ERROR", "CANCELLED", "EXPIRED"]
    """Status of `EIP155OrderRequest`."""

    order_id: Optional[str] = None
    """ID of `Order` created from the `EIP155OrderRequest`.

    This is the primary identifier for the `/orders` routes.
    """

    recipient_account_id: Optional[str] = None
    """ID of recipient `Account`."""
