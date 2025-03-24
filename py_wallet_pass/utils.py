"""
Utility and Helper functions for the wallet pass SDK.
"""

import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from .schema.core import (
    PassType, 
    Barcode, 
    Location, 
    PassField, 
    PassStructure, 
    PassStyle, 
    PassImages, 
    PassTemplate, 
    PassData
)


def create_template(
    name: str,
    organization_id: str,
    pass_type: PassType,
    description: Optional[str] = None,
    **kwargs
) -> PassTemplate:
    """
    Create a new pass template with default values.
    
    Args:
        name: Name of the template
        organization_id: Organization identifier
        pass_type: Type of pass (from PassType enum)
        description: Optional description
        **kwargs: Additional template attributes
    
    Returns:
        A PassTemplate instance
    """
    # Create default structure
    structure = PassStructure()
    
    # Create default style with some sensible colors
    style = PassStyle(
        background_color="#FFFFFF",
        foreground_color="#000000",
        label_color="#999999",
        logo_text=name
    )
    
    # Create default images (empty)
    images = PassImages()
    
    # Create the template
    template = PassTemplate(
        id=str(uuid.uuid4()),
        name=name,
        description=description or f"{name} Pass",
        organization_id=organization_id,
        pass_type=pass_type,
        structure=structure,
        style=style,
        images=images,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True
    )
    
    # Update with any additional attributes
    for key, value in kwargs.items():
        if hasattr(template, key):
            setattr(template, key, value)
    
    return template


def add_field_to_template(
    template: PassTemplate,
    field_type: str,
    key: str,
    label: str,
    value: Any,
    **kwargs
) -> PassTemplate:
    """
    Add a field to a template.
    
    Args:
        template: The pass template
        field_type: Type of field ('header', 'primary', 'secondary', 'auxiliary', 'back')
        key: Field key
        label: Field label
        value: Default field value
        **kwargs: Additional field attributes
    
    Returns:
        Updated PassTemplate
    """
    # Create the field
    field = PassField(
        key=key,
        label=label,
        value=value,
        **kwargs
    )
    
    # Add the field to the appropriate section of the template
    if field_type == 'header':
        template.structure.header_fields.append(field)
    elif field_type == 'primary':
        template.structure.primary_fields.append(field)
    elif field_type == 'secondary':
        template.structure.secondary_fields.append(field)
    elif field_type == 'auxiliary':
        template.structure.auxiliary_fields.append(field)
    elif field_type == 'back':
        template.structure.back_fields.append(field)
    else:
        raise ValueError(f"Unknown field type: {field_type}")
    
    # Update the template
    template.updated_at = datetime.now()
    
    return template


def create_pass_data(
    template_id: str,
    customer_id: str,
    serial_number: Optional[str] = None,
    barcode_message: Optional[str] = None,
    barcode_alt_text: Optional[str] = None,
    expiration_date: Optional[datetime] = None,
    relevant_date: Optional[datetime] = None,
    field_values: Optional[Dict[str, Union[str, int, float, bool, datetime]]] = None,
    **kwargs
) -> PassData:
    """
    Create pass data for a template.
    
    This function creates a PassData object that contains all the necessary data
    for generating a wallet pass. The data includes customer information, barcode details,
    expiration dates, and field values to populate the template.
    
    Args:
        template_id: ID of the template to use
        customer_id: Customer identifier for the pass owner
        serial_number: Optional serial number (will be generated as UUID if not provided)
        barcode_message: Content to encode in the pass barcode (e.g., membership number)
        barcode_alt_text: Human-readable text to display below the barcode
        expiration_date: Date when the pass expires (if applicable)
        relevant_date: Date when the pass becomes relevant (e.g., event date)
        field_values: Dictionary of field values to populate the template fields
            The keys should match the field keys in the template
        **kwargs: Additional pass data attributes
    
    Returns:
        A PassData instance ready to be used with create_pass method
        
    Examples:
        >>> pass_data = create_pass_data(
        ...     template_id="event-template-123",
        ...     customer_id="customer456",
        ...     barcode_message="TICKET123456",
        ...     field_values={
        ...         "event_name": "Summer Music Festival",
        ...         "event_date": "June 1, 2025 at 7:00 PM",
        ...         "ticket_type": "VIP Access"
        ...     }
        ... )
    """
    # Generate a serial number if not provided
    if not serial_number:
        serial_number = str(uuid.uuid4())
    
    # Create the pass data
    pass_data = PassData(
        template_id=template_id,
        customer_id=customer_id,
        serial_number=serial_number,
        field_values=field_values or {},
        **kwargs
    )
    
    return pass_data


def create_location(
    latitude: float,
    longitude: float,
    relevant_text: Optional[str] = None,
    altitude: Optional[float] = None,
    radius: float = 100
) -> Location:
    """
    Create a location for geofencing notifications.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        relevant_text: Text to display when near this location
        altitude: Optional altitude
        radius: Radius in meters (default 100)
    
    Returns:
        A Location instance
    """
    return Location(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        relevant_text=relevant_text,
        radius=radius
    )


def create_barcode(
    message: str,
    format: str = "PKBarcodeFormatQR",
    alt_text: Optional[str] = None
) -> Barcode:
    """
    Create a barcode for a pass.
    
    Args:
        message: Barcode content
        format: Barcode format (default QR)
        alt_text: Text to display under the barcode
    
    Returns:
        A Barcode instance
    """
    return Barcode(
        format=format,
        message=message,
        alt_text=alt_text
    )


def create_event_pass_template(
    name: str,
    organization_id: str,
    platform: str = "both",
    style: Optional[PassStyle] = None,
    images: Optional[PassImages] = None,
    description: Optional[str] = None,
    locations: Optional[List[Location]] = None,
    **kwargs
) -> PassTemplate:
    """
    Create a template for event tickets.
    
    This function creates a template pre-configured for event tickets with common fields
    like event name, date, location, and ticket type. The template can be used
    to create passes for Apple Wallet, Google Wallet, or both platforms.
    
    Args:
        name: Name of the event (e.g., "Summer Music Festival")
        organization_id: Organization identifier for your company or brand
        platform: Target platform ('apple', 'google', or 'both')
        style: Optional PassStyle instance with custom colors and text styling
        images: Optional PassImages instance with paths to logo, icon, etc.
        description: Optional description of the pass template
        locations: Optional list of Location objects for geofencing notifications
        **kwargs: Additional template attributes
    
    Returns:
        A PassTemplate instance configured for event tickets
    
    Examples:
        >>> template = create_event_pass_template(
        ...     name="Summer Music Festival",
        ...     organization_id="example-corp",
        ...     platform="apple",
        ...     style=PassStyle(
        ...         background_color="#FF5733",
        ...         foreground_color="#FFFFFF"
        ...     )
        ... )
    """
    # Determine the pass type based on the platform
    if platform.lower() == "apple":
        pass_type = PassType.APPLE_EVENTTICKET
    elif platform.lower() == "google":
        pass_type = PassType.GOOGLE_EVENT_TICKET
    else:
        # Default to Apple for 'both' - the PassManager will handle creating both types
        pass_type = PassType.APPLE_EVENTTICKET
    
    # Create the base template with provided or default values
    template = create_template(
        name=name,
        organization_id=organization_id,
        pass_type=pass_type,
        description=description or f"{name} Event Ticket",
        style=style,
        images=images,
        **kwargs
    )
    
    # Add locations if provided
    if locations:
        template.locations = locations
    
    # Add common fields for event tickets
    add_field_to_template(template, "header", "event_name", "Event", name)
    add_field_to_template(template, "primary", "event_date", "Date", "")
    add_field_to_template(template, "secondary", "event_location", "Location", "")
    add_field_to_template(template, "auxiliary", "ticket_type", "Ticket Type", "General Admission")
    add_field_to_template(template, "back", "event_details", "Details", "")
    
    return template


def create_coupon_pass_template(
    name: str,
    organization_id: str,
    platform: str = "both",
    style: Optional[PassStyle] = None,
    images: Optional[PassImages] = None,
    description: Optional[str] = None,
    locations: Optional[List[Location]] = None,
    **kwargs
) -> PassTemplate:
    """
    Create a template for coupons and offers.
    
    This function creates a template pre-configured for coupons and offers with common fields
    like offer name, expiration date, and promo code. The template can be used
    to create passes for Apple Wallet, Google Wallet, or both platforms.
    
    Args:
        name: Name of the coupon or offer (e.g., "25% Off Everything")
        organization_id: Organization identifier for your company or brand
        platform: Target platform ('apple', 'google', or 'both')
        style: Optional PassStyle instance with custom colors and text styling
        images: Optional PassImages instance with paths to logo, icon, etc.
        description: Optional description of the pass template
        locations: Optional list of Location objects for geofencing notifications
        **kwargs: Additional template attributes
    
    Returns:
        A PassTemplate instance configured for coupons and offers
    
    Examples:
        >>> template = create_coupon_pass_template(
        ...     name="25% Off Everything",
        ...     organization_id="example-corp",
        ...     platform="apple",
        ...     style=PassStyle(
        ...         background_color="#4CAF50",
        ...         foreground_color="#FFFFFF"
        ...     )
        ... )
    """
    # Determine the pass type based on the platform
    if platform.lower() == "apple":
        pass_type = PassType.APPLE_COUPON
    elif platform.lower() == "google":
        pass_type = PassType.GOOGLE_OFFER
    else:
        # Default to Apple for 'both'
        pass_type = PassType.APPLE_COUPON
    
    # Create the base template with provided or default values
    template = create_template(
        name=name,
        organization_id=organization_id,
        pass_type=pass_type,
        description=description or f"{name} Coupon",
        style=style,
        images=images,
        **kwargs
    )
    
    # Add locations if provided
    if locations:
        template.locations = locations
    
    # Add common fields for coupons
    add_field_to_template(template, "primary", "offer", "Offer", name)
    add_field_to_template(template, "secondary", "expiration", "Expires", "")
    add_field_to_template(template, "auxiliary", "promo_code", "Promo Code", "")
    add_field_to_template(template, "back", "terms", "Terms & Conditions", "")
    
    return template


def create_loyalty_pass_template(
    name: str,
    organization_id: str,
    platform: str = "both",
    style: Optional[PassStyle] = None,
    images: Optional[PassImages] = None,
    description: Optional[str] = None,
    locations: Optional[List[Location]] = None,
    **kwargs
) -> PassTemplate:
    """
    Create a template for loyalty cards.
    
    This function creates a template pre-configured for loyalty cards with common fields
    like member name, points balance, membership level, and program details. The template 
    can be used to create passes for Apple Wallet, Google Wallet, or both platforms.
    
    Args:
        name: Name of the loyalty program (e.g., "Coffee Rewards")
        organization_id: Organization identifier for your company or brand
        platform: Target platform ('apple', 'google', or 'both')
        style: Optional PassStyle instance with custom colors and text styling
        images: Optional PassImages instance with paths to logo, icon, etc.
        description: Optional description of the pass template
        locations: Optional list of Location objects for geofencing notifications
        **kwargs: Additional template attributes
    
    Returns:
        A PassTemplate instance configured for loyalty cards
    
    Examples:
        >>> template = create_loyalty_pass_template(
        ...     name="Coffee Rewards",
        ...     organization_id="example-corp",
        ...     platform="google",
        ...     style=PassStyle(
        ...         background_color="#8B4513",
        ...         foreground_color="#FFFFFF"
        ...     )
        ... )
    """
    # Determine the pass type based on the platform
    if platform.lower() == "apple":
        pass_type = PassType.APPLE_STORECARD
    elif platform.lower() == "google":
        pass_type = PassType.GOOGLE_LOYALTY
    else:
        # Default to Apple for 'both'
        pass_type = PassType.APPLE_STORECARD
    
    # Create the base template with provided or default values
    template = create_template(
        name=name,
        organization_id=organization_id,
        pass_type=pass_type,
        description=description or f"{name} Loyalty Card",
        style=style,
        images=images,
        **kwargs
    )
    
    # Add locations if provided
    if locations:
        template.locations = locations
    
    # Add common fields for loyalty cards
    add_field_to_template(template, "header", "member_name", "Member", "")
    add_field_to_template(template, "primary", "points", "Points", "0")
    add_field_to_template(template, "secondary", "member_since", "Member Since", "")
    add_field_to_template(template, "auxiliary", "membership_level", "Level", "Standard")
    add_field_to_template(template, "back", "program_details", "Program Details", "")
    
    return template


def create_boarding_pass_template(
    name: str,
    organization_id: str,
    platform: str = "both",
    style: Optional[PassStyle] = None,
    images: Optional[PassImages] = None,
    description: Optional[str] = None,
    locations: Optional[List[Location]] = None,
    **kwargs
) -> PassTemplate:
    """
    Create a template for boarding passes.
    
    This function creates a template pre-configured for boarding passes with common fields
    like passenger name, flight number, seat, and departure/arrival information. The template 
    can be used to create passes for Apple Wallet, Google Wallet, or both platforms.
    
    Args:
        name: Name of the airline or transport provider (e.g., "Acme Airlines")
        organization_id: Organization identifier for your company or brand
        platform: Target platform ('apple', 'google', or 'both')
        style: Optional PassStyle instance with custom colors and text styling
        images: Optional PassImages instance with paths to logo, icon, etc.
        description: Optional description of the pass template
        locations: Optional list of Location objects for geofencing notifications
        **kwargs: Additional template attributes
    
    Returns:
        A PassTemplate instance configured for boarding passes
    
    Examples:
        >>> template = create_boarding_pass_template(
        ...     name="Acme Airlines",
        ...     organization_id="acme-air",
        ...     platform="apple",
        ...     style=PassStyle(
        ...         background_color="#1E40AF",
        ...         foreground_color="#FFFFFF"
        ...     )
        ... )
    """
    # Determine the pass type based on the platform
    if platform.lower() == "apple":
        pass_type = PassType.APPLE_BOARDINGPASS
    elif platform.lower() == "google":
        pass_type = PassType.GOOGLE_FLIGHT
    else:
        # Default to Apple for 'both'
        pass_type = PassType.APPLE_BOARDINGPASS
    
    # Create the base template with provided or default values
    template = create_template(
        name=name,
        organization_id=organization_id,
        pass_type=pass_type,
        description=description or f"{name} Boarding Pass",
        style=style,
        images=images,
        **kwargs
    )
    
    # Add locations if provided
    if locations:
        template.locations = locations
    
    # Add common fields for boarding passes
    add_field_to_template(template, "header", "passenger_name", "Passenger", "")
    add_field_to_template(template, "primary", "flight_number", "Flight", "")
    add_field_to_template(template, "primary", "date", "Date", "")
    add_field_to_template(template, "secondary", "from", "From", "")
    add_field_to_template(template, "secondary", "to", "To", "")
    add_field_to_template(template, "auxiliary", "boarding_time", "Boarding", "")
    add_field_to_template(template, "auxiliary", "seat", "Seat", "")
    add_field_to_template(template, "back", "flight_details", "Flight Details", "")
    
    return template