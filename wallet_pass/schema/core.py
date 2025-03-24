"""Schema definitions for wallet passes."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, AnyHttpUrl, Field


class PassType(str, Enum):
    """Types of wallet passes."""
    
    # Apple Wallet pass types
    APPLE_GENERIC = "generic"
    APPLE_COUPON = "coupon"
    APPLE_EVENTTICKET = "eventTicket"
    APPLE_BOARDINGPASS = "boardingPass"
    APPLE_STORECARD = "storeCard"
    
    # Google Wallet pass types
    GOOGLE_OFFER = "offer"
    GOOGLE_LOYALTY = "loyalty"
    GOOGLE_GIFT_CARD = "giftCard"
    GOOGLE_EVENT_TICKET = "eventTicket"
    GOOGLE_FLIGHT = "flight"
    GOOGLE_TRANSIT = "transit"
    
    # Samsung Wallet pass types
    SAMSUNG_COUPON = "coupon"
    SAMSUNG_MEMBERSHIP = "membership"
    SAMSUNG_TICKET = "ticket"
    SAMSUNG_BOARDING = "boarding"
    SAMSUNG_VOUCHER = "voucher"


class Barcode(BaseModel):
    """Represents a barcode on a pass."""
    
    format: str = "PKBarcodeFormatQR"  # Default to QR
    message: str
    alt_text: Optional[str] = None
    encoding: str = "iso-8859-1"


class Location(BaseModel):
    """Represents a geographic location for triggering notifications."""
    
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    relevant_text: Optional[str] = None
    radius: float = 100  # meters


class PassField(BaseModel):
    """Represents a data field on a pass."""
    
    key: str
    label: str
    value: Any
    change_message: Optional[str] = None
    text_alignment: str = "left"  # left, center, right
    date_style: Optional[str] = None  # PKDateStyleNone, PKDateStyleShort, etc.
    time_style: Optional[str] = None
    is_relative: bool = False
    currency_code: Optional[str] = None
    number_format: Optional[str] = None


class PassStructure(BaseModel):
    """Represents the structure of fields on a pass."""
    
    header_fields: List[PassField] = []
    primary_fields: List[PassField] = []
    secondary_fields: List[PassField] = []
    auxiliary_fields: List[PassField] = []
    back_fields: List[PassField] = []


class PassStyle(BaseModel):
    """Style information for a pass."""
    
    background_color: Optional[str] = None
    foreground_color: Optional[str] = None
    label_color: Optional[str] = None
    logo_text: Optional[str] = None
    logo_text_color: Optional[str] = None


class PassImages(BaseModel):
    """Images used in a pass."""
    
    logo: Optional[str] = None
    icon: Optional[str] = None
    thumbnail: Optional[str] = None
    strip: Optional[str] = None
    background: Optional[str] = None
    footer: Optional[str] = None


class NFC(BaseModel):
    """NFC configuration for a pass."""
    
    message: str
    encryption_public_key: Optional[str] = None
    requires_authentication: bool = False


class PassTemplate(BaseModel):
    """Template for creating passes."""
    
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    organization_id: str
    pass_type: PassType
    structure: PassStructure
    style: PassStyle
    images: PassImages
    locations: List[Location] = []
    barcode_format: str = "PKBarcodeFormatQR"
    nfc_enabled: bool = False
    nfc_data: Optional[NFC] = None
    expiration_type: Optional[str] = None  # none, fixed, relative
    expiration_value: Optional[str] = None
    max_distance: Optional[int] = None
    web_service_url: Optional[AnyHttpUrl] = None
    authentication_token: Optional[str] = None
    created_by_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    is_archived: bool = False
    custom_data: Dict[str, Any] = Field(default_factory=dict)


class PassData(BaseModel):
    """Data for creating a pass instance."""
    
    template_id: str
    customer_id: str
    serial_number: Optional[str] = None
    barcode_message: Optional[str] = None
    barcode_alt_text: Optional[str] = None
    expiration_date: Optional[datetime] = None
    relevant_date: Optional[datetime] = None
    max_distance: Optional[int] = None
    voided: bool = False
    field_values: Dict[str, Any] = Field(default_factory=dict)


class PassResponse(BaseModel):
    """Response after creating a pass."""
    
    id: str
    template_id: str
    customer_id: str
    serial_number: str
    pass_type_identifier: str
    authentication_token: str
    organization_id: str
    barcode: Optional[Barcode] = None
    voided: bool = False
    expiration_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    apple_pass_url: Optional[str] = None
    google_pass_url: Optional[str] = None
    apple_pass_id: Optional[str] = None
    google_pass_id: Optional[str] = None