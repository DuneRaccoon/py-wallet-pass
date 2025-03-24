# Samsung Wallet Integration Guide

This guide explains how to use py-wallet-pass to create and manage Samsung Wallet passes.

## Prerequisites

Before you begin, you'll need:

1. A **Samsung Wallet Developer account**
2. An **Issuer ID** from the Samsung Wallet portal
3. An **API Key** from the Samsung Wallet portal
4. A **Service ID** for your specific pass type

## Setup

### 1. Creating a Samsung Wallet Developer Account

1. Visit the [Samsung Wallet Developer Portal](https://developer.samsung.com/wallet)
2. Sign up for a developer account if you don't have one
3. Complete any required verification steps

### 2. Obtaining Credentials

Once your account is set up:

1. Navigate to the API Management section in the Samsung Wallet Developer Portal
2. Create a new project or application
3. Request an Issuer ID, API Key, and Service ID
4. Note down these credentials as you'll need them for configuration

## Basic Usage

Here's how to create a simple Samsung Wallet pass:

```python
import wallet_pass as wp
import datetime

# Configure the SDK
config = wp.WalletConfig(
    samsung_issuer_id="your-samsung-issuer-id",
    samsung_api_key="your-samsung-api-key",
    samsung_service_id="your-samsung-service-id",
    samsung_api_base_url="https://wallet-api.samsung.com/v1",  # Default API URL
    web_service_url="https://example.com/wallet",  # Optional for your web service
    storage_path="passes"  # Where to store pass data
)

# Create a pass manager
manager = wp.create_pass_manager(config=config)

# Create a membership card template
template = wp.utils.create_template(
    name="Fitness Club Membership",
    organization_id="your-company",
    pass_type=wp.PassType.SAMSUNG_MEMBERSHIP,
    description="Fitness Club Membership Card",
    style=wp.PassStyle(
        background_color="#1E3A8A",  # Dark blue
        foreground_color="#FFFFFF",  # White
        label_color="#93C5FD",       # Light blue
        logo_text="Fitness Club"
    ),
    images=wp.PassImages(
        logo="images/logo.png",
        icon="images/icon.png"
    )
)

# Add fields to the template
wp.utils.add_field_to_template(
    template, "header", "member_name", "Member", ""
)
wp.utils.add_field_to_template(
    template, "primary", "member_id", "Member ID", ""
)
wp.utils.add_field_to_template(
    template, "secondary", "membership_type", "Membership", ""
)
wp.utils.add_field_to_template(
    template, "secondary", "expiration", "Valid Until", ""
)
wp.utils.add_field_to_template(
    template, "auxiliary", "tier", "Tier", ""
)
wp.utils.add_field_to_template(
    template, "back", "gym_locations", "Club Locations", 
    "Downtown: 123 Main St\nUptown: 456 North Ave\nWestside: 789 West Blvd"
)

# Create pass data
expiration_date = datetime.datetime.now() + datetime.timedelta(days=365)
pass_data = wp.utils.create_pass_data(
    template_id=template.id,
    customer_id="member-9876",
    serial_number="FC-9876543",
    barcode_message="MEMBER9876543",
    barcode_alt_text="MEMBER9876543",
    expiration_date=expiration_date,
    field_values={
        "member_name": "Sarah Johnson",
        "member_id": "9876543",
        "membership_type": "Premium",
        "expiration": expiration_date.strftime("%B %d, %Y"),
        "tier": "Gold",
    }
)

# Create the pass (specify to create only for Samsung)
response = manager.create_pass(pass_data, template, create_for=["samsung"])
print(f"Created Samsung pass: {response['samsung'].id}")

# Generate the pass file
pass_file = manager.generate_pass_files(response['samsung'].id, template, platforms=["samsung"])

# Save the pass file
with open("samsung_membership.json", "wb") as f:
    f.write(pass_file['samsung'])

print("Pass saved to samsung_membership.json")
```

## Samsung Wallet Pass Types

Samsung Wallet supports several pass types, each represented in the SDK:

1. **Membership Cards** (`SAMSUNG_MEMBERSHIP`): For loyalty programs and memberships
2. **Coupons** (`SAMSUNG_COUPON`): For discounts and promotional offers
3. **Tickets** (`SAMSUNG_TICKET`): For event access
4. **Boarding Passes** (`SAMSUNG_BOARDING`): For travel and transportation
5. **Vouchers** (`SAMSUNG_VOUCHER`): For gift cards and stored value

Each pass type has specific field requirements and display properties.

## Creating Different Pass Types

### Coupon Example

```python
# Create a coupon template
template = wp.utils.create_template(
    name="25% Off Everything",
    organization_id="your-company",
    pass_type=wp.PassType.SAMSUNG_COUPON,
    description="Limited Time Offer",
    style=wp.PassStyle(
        background_color="#4CAF50",  # Green
        foreground_color="#FFFFFF",  # White
        label_color="#E8F5E9",       # Light green
        logo_text="SALE"
    ),
    images=wp.PassImages(
        logo="images/logo.png",
        icon="images/icon.png"
    )
)

# Add coupon-specific fields
wp.utils.add_field_to_template(
    template, "primary", "offer", "Offer", "25% Off Everything"
)
wp.utils.add_field_to_template(
    template, "secondary", "valid_until", "Valid Until", ""
)
wp.utils.add_field_to_template(
    template, "auxiliary", "promo_code", "Promo Code", "SAVE25"
)
wp.utils.add_field_to_template(
    template, "back", "terms", "Terms & Conditions", 
    "One time use. Cannot be combined with other offers."
)
```

### Event Ticket Example

```python
# Create an event ticket template
template = wp.utils.create_template(
    name="Concert Ticket",
    organization_id="your-company",
    pass_type=wp.PassType.SAMSUNG_TICKET,
    description="Rock Concert Ticket",
    style=wp.PassStyle(
        background_color="#9C27B0",  # Purple
        foreground_color="#FFFFFF",  # White
        label_color="#E1BEE7",       # Light purple
        logo_text="LIVE MUSIC"
    ),
    images=wp.PassImages(
        logo="images/concert_logo.png",
        icon="images/concert_icon.png"
    )
)

# Add ticket-specific fields
wp.utils.add_field_to_template(
    template, "header", "event_name", "Event", "Summer Rock Festival"
)
wp.utils.add_field_to_template(
    template, "primary", "date", "Date", ""
)
wp.utils.add_field_to_template(
    template, "secondary", "venue", "Venue", "Central Stadium"
)
wp.utils.add_field_to_template(
    template, "auxiliary", "seat", "Seat", "GA-101"
)
```

## Updating Passes

To update an existing Samsung Wallet pass:

```python
# Create updated pass data
updated_data = wp.utils.create_pass_data(
    template_id=template.id,
    customer_id="member-9876",
    serial_number="FC-9876543",
    barcode_message="MEMBER9876543",
    barcode_alt_text="MEMBER9876543",
    expiration_date=expiration_date,
    field_values={
        "member_name": "Sarah Johnson",
        "member_id": "9876543",
        "membership_type": "VIP",  # Updated membership type
        "expiration": expiration_date.strftime("%B %d, %Y"),
        "tier": "Platinum",  # Updated tier
    }
)

# Update the pass
update_response = manager.update_pass(response['samsung'].id, updated_data, template)
print(f"Updated Samsung pass: {update_response['samsung'].id}")

# Generate the updated pass file
updated_pass_file = manager.generate_pass_files(update_response['samsung'].id, template, platforms=["samsung"])

# Save the updated pass file
with open("updated_samsung_membership.json", "wb") as f:
    f.write(updated_pass_file['samsung'])
```

## Voiding Passes

To void a Samsung Wallet pass:

```python
# Void the pass
void_response = manager.void_pass(response['samsung'].id, template, void_for=["samsung"])
print(f"Voided Samsung pass: {void_response['samsung'].id}")
```

## Pass Distribution

### Distribution Methods

There are several ways to distribute Samsung Wallet passes to users:

1. **Direct Download**: Provide the JSON file for download
2. **QR Code**: Generate a QR code that links to the pass download
3. **Email**: Send the pass file as an attachment
4. **SMS**: Send a link to download the pass
5. **In-App**: Integrate with your mobile app for seamless pass creation

### Creating a QR Code

You can generate a QR code for pass distribution:

```python
import qrcode

# Create a QR code for the pass download URL
download_url = f"https://example.com/passes/download/{response['samsung'].id}"
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(download_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("pass_qr.png")
```

## Customizing Samsung Wallet Passes

### Visual Customization

Samsung Wallet passes can be visually customized to match your brand:

```python
template = wp.utils.create_template(
    name="Fitness Club Membership",
    organization_id="your-company",
    pass_type=wp.PassType.SAMSUNG_MEMBERSHIP,
    description="Fitness Club Membership Card",
    style=wp.PassStyle(
        background_color="#1E3A8A",  # Dark blue background
        foreground_color="#FFFFFF",  # White text
        label_color="#93C5FD",       # Light blue labels
        logo_text="Fitness Club",
        logo_text_color="#FFFFFF"    # White logo text
    ),
    images=wp.PassImages(
        logo="images/logo.png",      # Main logo
        icon="images/icon.png",      # Small icon
        background="images/bg.png",  # Background image
        thumbnail="images/thumb.png" # Thumbnail image
    )
)
```

### Adding Locations

To associate locations with your pass:

```python
# Create locations
gym_downtown = wp.utils.create_location(
    latitude=37.7749,
    longitude=-122.4194,
    relevant_text="Welcome to our Downtown location!"
)

gym_uptown = wp.utils.create_location(
    latitude=37.7833,
    longitude=-122.4167,
    relevant_text="Welcome to our Uptown location!"
)

# Add locations to the template
template = wp.utils.create_template(
    # ... other parameters
    locations=[gym_downtown, gym_uptown]
)
```

## Web Service Integration

For pass updates and notifications, you'll need to set up a web service. See the [Web Service Guide](web_service.md) for details.

## Common Issues and Troubleshooting

### API Connection Issues

If you encounter connection problems:

```
Failed to connect to Samsung Wallet API
```

Check that:
- Your API key and credentials are correct
- The Samsung API base URL is correct
- Your network can reach the Samsung API endpoints

### Image Requirements

Samsung Wallet has specific image requirements:

- Images should be PNG format
- Check the recommended sizes for each image type
- Verify that the image paths are correct and accessible

### Missing Required Fields

Each pass type requires specific fields:

- Ensure all required fields are included in your template
- Check that field values are properly formatted
- Verify that fields are assigned to the correct sections

## References

- [Samsung Wallet Developer Documentation](https://developer.samsung.com/wallet)
- [Samsung Wallet Design Guidelines](https://developer.samsung.com/wallet/design-guide.html)
