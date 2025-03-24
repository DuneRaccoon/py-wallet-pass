# Pass Customization Guide

This guide explains how to customize the appearance and content of wallet passes created with the py-wallet-pass SDK. Proper pass design is crucial for user adoption and engagement.

## Basic Customization Elements

The py-wallet-pass SDK provides several key objects for customizing passes:

1. **PassStyle**: Controls colors and text styling
2. **PassImages**: Defines images used in the pass
3. **PassStructure**: Organizes fields and their layout
4. **PassField**: Individual data fields displayed on the pass

## Styling Your Passes

### Using PassStyle

The `PassStyle` class allows you to define the visual style of your passes:

```python
from py_wallet_pass import PassStyle

# Create a style for a coffee shop loyalty card
style = PassStyle(
    background_color="#8B4513",      # Brown background
    foreground_color="#FFFFFF",      # White text
    label_color="#D2B48C",           # Tan labels
    logo_text="Coffee Rewards",      # Text displayed near logo
    logo_text_color="#FFEBCD"        # Light tan logo text
)
```

### Color Guidelines

Choose colors that:

1. **Reflect your brand**: Use your brand's primary colors
2. **Provide good contrast**: Ensure text is readable against the background
3. **Differentiate passes**: Use different colors for different pass types

### Color Formats

Colors can be specified in hexadecimal format:

```python
# Full hex format with alpha
background_color="#FF5733FF"  # RGB + Alpha

# Standard hex format (implied alpha = FF)
background_color="#FF5733"    # RGB only
```

## Adding Images to Passes

### Using PassImages

The `PassImages` class defines the images used in your pass:

```python
from py_wallet_pass import PassImages

# Define images for an event ticket
images = PassImages(
    logo="images/logo.png",          # Main logo (required)
    icon="images/icon.png",          # Small icon (required)
    strip="images/event_banner.png", # Header banner (optional)
    background="images/bg.png",      # Background texture (optional)
    thumbnail="images/thumbnail.png", # Thumbnail image (optional)
    footer="images/footer.png"       # Footer image (optional)
)
```

### Image Requirements by Platform

#### Apple Wallet

| Image      | Recommended Size | Format | Required |
|------------|------------------|--------|----------|
| logo       | 160×50 px        | PNG    | Yes      |
| icon       | 58×58 px         | PNG    | Yes      |
| strip      | 640×84-132 px    | PNG    | No       |
| background | 180×220 px       | PNG    | No       |
| thumbnail  | 90×90 px         | PNG    | No       |
| footer     | 312×44 px        | PNG    | No       |

For Retina displays, provide @2x versions at double the resolution (e.g., logo@2x.png at 320×100 px).

#### Google Wallet

| Image      | Recommended Size | Format | Required |
|------------|------------------|--------|----------|
| logo       | 200×200 px       | PNG    | Yes      |
| icon       | 96×96 px         | PNG    | Yes      |
| hero       | 960×320 px       | PNG    | No       |
| background | 200×286 px       | PNG    | No       |
| thumbnail  | 100×100 px       | PNG    | No       |

#### Samsung Wallet

| Image      | Recommended Size | Format | Required |
|------------|------------------|--------|----------|
| logo       | 200×200 px       | PNG    | Yes      |
| icon       | 96×96 px         | PNG    | Yes      |
| strip      | 960×320 px       | PNG    | No       |
| background | 200×286 px       | PNG    | No       |
| thumbnail  | 100×100 px       | PNG    | No       |

### Image Best Practices

1. **Use transparent PNGs**: Especially for logos and icons
2. **Optimize image size**: Keep file sizes small for faster loading
3. **Test on actual devices**: Images may appear differently on different screens
4. **Use appropriate content**: Avoid text in images that duplicates pass fields
5. **Consider safe areas**: Ensure important elements aren't cropped

## Organizing Pass Fields

### Field Sections

Passes are organized into sections to create a clear visual hierarchy:

1. **Header Fields**: Appear at the top of the pass
2. **Primary Fields**: Most prominent information (large font)
3. **Secondary Fields**: Supporting information
4. **Auxiliary Fields**: Additional details
5. **Back Fields**: Information shown on the "back" of the pass

### Adding Fields to Templates

Use the `add_field_to_template` utility to add fields:

```python
import py_wallet_pass as pwp

# Create a template first
template = pwp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="coffeecompany",
    platform="both"
)

# Add fields to different sections
pwp.utils.add_field_to_template(
    template, "header", "member_name", "Member", ""
)

pwp.utils.add_field_to_template(
    template, "primary", "points", "Points", "0"
)

pwp.utils.add_field_to_template(
    template, "secondary", "member_since", "Member Since", "January 2023"
)

pwp.utils.add_field_to_template(
    template, "auxiliary", "membership_level", "Level", "Gold"
)

pwp.utils.add_field_to_template(
    template, "back", "program_details", "Program Details",
    "Earn 1 point for every $1 spent. 100 points = free coffee."
)
```

### Field Properties

Fields have several properties you can customize:

```python
# Add a field with additional properties
pwp.utils.add_field_to_template(
    template, "primary", "balance", "Balance", "0",
    change_message="Your balance changed to %@",  # Message shown when value changes
    text_alignment="right",                       # left, center, or right
    date_style="PKDateStyleMedium",               # For date formatting
    time_style="PKTimeStyleShort",                # For time formatting
    is_relative=False,                            # For relative dates
    currency_code="USD",                          # For currency formatting
    number_format="100.00"                        # For number formatting
)
```

## Pass Type-Specific Customization

Different pass types have unique characteristics and field requirements.

### Event Tickets

```python
# Create an event ticket template
template = pwp.utils.create_event_pass_template(
    name="Summer Music Festival",
    organization_id="eventcompany",
    platform="both",
    style=PassStyle(
        background_color="#FF5733",
        foreground_color="#FFFFFF",
        label_color="#FFCCCB",
        logo_text="Summer Festival"
    ),
    images=PassImages(
        logo="images/logo.png",
        icon="images/icon.png",
        strip="images/festival_banner.png"
    )
)

# Add event-specific fields
pwp.utils.add_field_to_template(
    template, "header", "event_name", "Event", "Summer Music Festival"
)
pwp.utils.add_field_to_template(
    template, "primary", "event_date", "Date", "June 15, 2025"
)
pwp.utils.add_field_to_template(
    template, "primary", "event_time", "Time", "7:30 PM"
)
pwp.utils.add_field_to_template(
    template, "secondary", "venue", "Venue", "Central Park"
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "ticket_type", "Ticket", "VIP Access"
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "seat", "Seat", "GA-101"
)
pwp.utils.add_field_to_template(
    template, "back", "event_details", "Details", 
    "Gates open at 6:00 PM. No re-entry after exit."
)
```

### Loyalty Cards

```python
# Create a loyalty card template
template = pwp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="coffeecompany",
    platform="both",
    style=PassStyle(
        background_color="#8B4513",
        foreground_color="#FFFFFF",
        label_color="#D2B48C",
        logo_text="Coffee Rewards"
    ),
    images=PassImages(
        logo="images/coffee_logo.png",
        icon="images/coffee_icon.png"
    )
)

# Add loyalty-specific fields
pwp.utils.add_field_to_template(
    template, "header", "member_name", "Member", ""
)
pwp.utils.add_field_to_template(
    template, "primary", "points", "Points", "0"
)
pwp.utils.add_field_to_template(
    template, "secondary", "member_since", "Member Since", ""
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "membership_level", "Level", "Standard"
)
pwp.utils.add_field_to_template(
    template, "back", "program_details", "Program Details", 
    "Earn 1 point for every $1 spent."
)
pwp.utils.add_field_to_template(
    template, "back", "rewards", "Rewards", 
    "100 points = Free coffee\n500 points = Free lunch"
)
```

### Coupons

```python
# Create a coupon template
template = pwp.utils.create_coupon_pass_template(
    name="25% Off Everything",
    organization_id="retailcompany",
    platform="both",
    style=PassStyle(
        background_color="#4CAF50",
        foreground_color="#FFFFFF",
        label_color="#E8F5E9",
        logo_text="25% OFF"
    ),
    images=PassImages(
        logo="images/retailer_logo.png",
        icon="images/retailer_icon.png",
        strip="images/coupon_banner.png"
    )
)

# Add coupon-specific fields
pwp.utils.add_field_to_template(
    template, "primary", "offer", "Offer", "25% Off Everything"
)
pwp.utils.add_field_to_template(
    template, "secondary", "expiration", "Expires", ""
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "promo_code", "Promo Code", "SAVE25"
)
pwp.utils.add_field_to_template(
    template, "back", "terms", "Terms & Conditions", 
    "Valid in-store only. Cannot be combined with other offers."
)
```

### Boarding Passes

```python
# Create a boarding pass template
template = pwp.utils.create_boarding_pass_template(
    name="Acme Airlines",
    organization_id="acmeair",
    platform="both",
    style=PassStyle(
        background_color="#1E40AF",
        foreground_color="#FFFFFF",
        label_color="#BFDBFE",
        logo_text="Acme Airlines"
    ),
    images=PassImages(
        logo="images/airline_logo.png",
        icon="images/airline_icon.png",
        strip="images/airline_banner.png"
    )
)

# Add boarding pass-specific fields
pwp.utils.add_field_to_template(
    template, "header", "passenger_name", "Passenger", ""
)
pwp.utils.add_field_to_template(
    template, "primary", "flight", "Flight", "AC123"
)
pwp.utils.add_field_to_template(
    template, "secondary", "departure", "Departs", "SFO 10:00 AM"
)
pwp.utils.add_field_to_template(
    template, "secondary", "arrival", "Arrives", "JFK 6:30 PM"
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "gate", "Gate", "B12"
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "seat", "Seat", "14A"
)
pwp.utils.add_field_to_template(
    template, "auxiliary", "boarding", "Boarding", "9:30 AM"
)
pwp.utils.add_field_to_template(
    template, "back", "flight_details", "Flight Details", 
    "Boeing 787. Flight time: 5h 30m. WiFi available."
)
```

## Barcode Customization

### Setting Barcode Format

You can specify the barcode format when creating a template:

```python
template = pwp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="coffeecompany",
    platform="both",
    barcode_format="PKBarcodeFormatQR"  # Set barcode format
)
```

### Available Barcode Formats

| Format Name           | Description          | Supported Platforms        |
|-----------------------|----------------------|----------------------------|
| PKBarcodeFormatQR     | QR Code              | Apple, Google, Samsung     |
| PKBarcodeFormatPDF417 | PDF417 (2D barcode)  | Apple, Google, Samsung     |
| PKBarcodeFormatAztec  | Aztec code           | Apple, Google              |
| PKBarcodeFormatCode128| Code 128 (1D barcode)| Apple, Google, Samsung     |

### Providing Barcode Data

When creating pass data, specify the barcode content:

```python
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",
    barcode_message="MEMBER123456",        # Content encoded in the barcode
    barcode_alt_text="MEMBER123456",       # Text displayed below the barcode
    # ... other fields
)
```

## Locations and Relevancy

### Adding Locations

You can associate geographic locations with a pass to trigger notifications when the user is nearby:

```python
from py_wallet_pass import utils

# Create locations
coffee_shop_downtown = utils.create_location(
    latitude=37.7749,
    longitude=-122.4194,
    relevant_text="Show this pass for 10% off your purchase!",
    radius=100  # meters
)

coffee_shop_uptown = utils.create_location(
    latitude=37.7833,
    longitude=-122.4167,
    relevant_text="Welcome to our Uptown store!",
    radius=150  # meters
)

# Add locations to the template
template = pwp.utils.create_loyalty_pass_template(
    # ... other parameters
    locations=[coffee_shop_downtown, coffee_shop_uptown]
)
```

### Setting Relevancy

You can specify when a pass becomes relevant:

```python
# Create pass data with a relevant date
event_date = datetime.datetime(2025, 6, 15, 19, 30)
pass_data = pwp.utils.create_pass_data(
    # ... other parameters
    relevant_date=event_date,  # Pass becomes relevant near this date
    # ... other fields
)
```

## Advanced Customization

### Platform-Specific Styling

You can create different templates for each platform:

```python
# Create an Apple-specific template
apple_template = pwp.utils.create_coupon_pass_template(
    name="25% Off Everything",
    organization_id="retailcompany",
    platform="apple",
    style=PassStyle(
        background_color="#4CAF50",
        foreground_color="#FFFFFF",
        label_color="#E8F5E9",
        logo_text="25% Off"
    )
)

# Create a Google-specific template with different styling
google_template = pwp.utils.create_coupon_pass_template(
    name="25% Off Everything",
    organization_id="retailcompany",
    platform="google",
    style=PassStyle(
        background_color="#388E3C",  # Darker green for Google
        foreground_color="#FFFFFF",
        label_color="#C8E6C9",  # Different label color
        logo_text="SAVE 25%"    # Different logo text
    )
)
```

### NFC Integration

For Apple Wallet passes, you can enable NFC functionality:

```python
from py_wallet_pass import NFC

# Create NFC data
nfc_data = NFC(
    message="MEMBER123456",  # Message to be transmitted via NFC
    encryption_public_key=None,  # Optional encryption key
    requires_authentication=False  # Whether authentication is required
)

# Create a template with NFC enabled
template = pwp.utils.create_loyalty_pass_template(
    # ... other parameters
    nfc_enabled=True,
    nfc_data=nfc_data
)
```

### Expiration Dates

Set an expiration date for passes:

```python
# Set an expiration date 30 days from now
expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
pass_data = pwp.utils.create_pass_data(
    # ... other parameters
    expiration_date=expiration_date,
    # ... other fields
)
```

## Design Best Practices

### General Guidelines

1. **Keep it simple**: Focus on the most important information
2. **Use clear hierarchy**: Make it obvious what's most important
3. **Maintain brand consistency**: Use your brand colors and logo
4. **Optimize for small screens**: Passes are viewed on mobile devices
5. **Test on actual devices**: Different platforms render passes differently

### Apple Wallet Design Tips

1. Use the strip image for visual appeal
2. Limit text in primary fields to ensure it's readable
3. Use relevant dates for time-sensitive passes
4. Keep images simple and recognizable

### Google Wallet Design Tips

1. Use hero images for visual impact
2. Keep text concise and clear
3. Ensure high contrast between text and background
4. Test on both Android and iOS devices (Google Wallet works on both)

### Samsung Wallet Design Tips

1. Similar to Apple, keep designs clean and simple
2. Ensure good contrast for readability
3. Keep text fields concise
4. Test on Samsung devices

## Testing Your Pass Designs

### Cross-Platform Testing

To ensure your passes look good on all platforms:

1. Generate passes for each platform
2. Install them on actual devices
3. Check all views (front, back, notification)
4. Test under different conditions (dark mode, low brightness)

### Testing Tools

- **Apple Wallet**: Use the Wallet app on iOS/macOS
- **Google Wallet**: Use the Google Wallet app on Android/iOS
- **Samsung Wallet**: Use the Samsung Wallet app on Samsung devices

## Conclusion

Well-designed passes enhance user experience and increase usage. By following these customization guidelines, you can create passes that are visually appealing, functional, and aligned with your brand.

Remember to test your passes thoroughly on actual devices to ensure they look and function as expected across all platforms.
