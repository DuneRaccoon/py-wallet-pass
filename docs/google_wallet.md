# Google Wallet Integration Guide

This guide explains how to use py-wallet-pass to create and manage Google Wallet passes.

## Prerequisites

Before you begin, you'll need:

1. A **Google Cloud Platform account**
2. A **Google Wallet API project** with the Wallet API enabled
3. A **Service Account** with appropriate permissions
4. An **Issuer ID** from the Google Pay and Wallet Console

## Setup

### 1. Setting up your Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Wallet API
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Wallet API" and enable it

### 2. Getting an Issuer ID

1. Visit the [Google Pay and Wallet Console](https://pay.google.com/business/console/)
2. Click "Create a new Issuer ID" 
3. Follow the steps to complete the process and receive your Issuer ID

### 3. Creating a Service Account

1. In the Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter a name and optional description
4. Grant the service account the "Wallet Object Issuer" role
5. Create a key for the service account (JSON format)
6. Download and securely store the JSON key file

## Basic Usage

Here's how to create a simple Google Wallet pass:

```python
import wallet_pass as wp
import datetime

# Configure the SDK
config = wp.WalletConfig(
    google_application_credentials="path/to/service-account-key.json",
    google_issuer_id="your-issuer-id-from-google-wallet-console",
    web_service_url="https://example.com/wallet",  # Optional
    storage_path="passes"  # Where to store pass data
)

# Create a pass manager
manager = wp.create_pass_manager(config=config)

# Create a template (this example is for a loyalty card)
template = wp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="your-company",
    platform="google",
    style=wp.PassStyle(
        background_color="#8B4513",  # Brown background
        foreground_color="#FFFFFF",  # White text
        label_color="#D2B48C",       # Tan labels
        logo_text="Coffee Rewards"
    ),
    images=wp.PassImages(
        logo="images/logo.png",
        icon="images/icon.png"
    )
)

# Add additional fields to the template if needed
wp.utils.add_field_to_template(
    template, "back", "rewards", "Rewards", "10 points = Free coffee"
)

# Create pass data
pass_data = wp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer456",
    barcode_message="MEMBER456789",
    barcode_alt_text="MEMBER456789",
    field_values={
        "member_name": "John Smith",
        "points": "450",
        "member_since": "January 15, 2023",
        "membership_level": "Gold",
        "program_details": "Earn 1 point for every $1 spent.",
        "rewards": "10 points = Free coffee\n50 points = Free pastry\n100 points = Free lunch"
    }
)

# Create the pass
response = manager.create_pass(pass_data, template)
print(f"Created pass: {response['google'].id}")

# Get the Google Pay link that can be shared with users
google_pass_url = response['google'].google_pass_url
print(f"Google Pay link: {google_pass_url}")

# Generate the Google Wallet JSON file (optional, usually just need the URL)
pass_file = manager.generate_pass_files(response['google'].id, template)

# Save the JSON file if needed
with open("loyalty_card.json", "wb") as f:
    f.write(pass_file['google'])

print("Pass saved to loyalty_card.json")
```

## Google Wallet Pass Types

Google Wallet supports multiple pass types, each with specific use cases:

1. **Loyalty Cards** (`GOOGLE_LOYALTY`): For membership and rewards programs
2. **Offers** (`GOOGLE_OFFER`): For coupons, promotions, and discounts
3. **Gift Cards** (`GOOGLE_GIFT_CARD`): For stored value and gift cards
4. **Event Tickets** (`GOOGLE_EVENT_TICKET`): For concerts, sports, and other events
5. **Flight Boarding Passes** (`GOOGLE_FLIGHT`): For airline travel
6. **Transit Passes** (`GOOGLE_TRANSIT`): For public transportation

Each pass type has specific fields and formatting. The SDK provides helper functions for creating templates:

```python
# For loyalty cards
template = wp.utils.create_loyalty_pass_template(...)

# For offers/coupons
template = wp.utils.create_coupon_pass_template(...)

# For event tickets
template = wp.utils.create_event_pass_template(...)

# For boarding passes
template = wp.utils.create_boarding_pass_template(...)
```

## Pass Distribution

### Share URL

The simplest way to distribute Google Wallet passes is through the generated Google Pay URL:

```python
google_pass_url = response['google'].google_pass_url
# Share this URL with your users via email, SMS, etc.
```

### QR Code

You can generate a QR code with the Google Pay URL:

```python
import qrcode

google_pass_url = response['google'].google_pass_url
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(google_pass_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("pass_qr.png")
```

## Updating Passes

To update an existing Google Wallet pass:

```python
# Create updated pass data
updated_data = wp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer456",
    serial_number=response['google'].serial_number,  # Use the same serial number
    barcode_message="MEMBER456789",
    barcode_alt_text="MEMBER456789",
    field_values={
        "member_name": "John Smith",
        "points": "550",  # Updated points value
        "member_since": "January 15, 2023",
        "membership_level": "Platinum",  # Updated level
        "program_details": "Earn 1 point for every $1 spent.",
        "rewards": "10 points = Free coffee\n50 points = Free pastry\n100 points = Free lunch"
    }
)

# Update the pass
update_response = manager.update_pass(response['google'].id, updated_data, template)
print(f"Updated pass: {update_response['google'].id}")
```

## Voiding Passes

To void a Google Wallet pass:

```python
# Void the pass
void_response = manager.void_pass(response['google'].id, template)
print(f"Voided pass: {void_response['google'].id}")
```

## Pass Notifications

Google Wallet handles push notifications automatically when you update a pass. There's no need to send a separate notification as with Apple Wallet.

## Customizing Google Wallet Passes

### Visual Customization

You can customize the appearance of your Google Wallet pass:

```python
template = wp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="your-company",
    platform="google",
    style=wp.PassStyle(
        background_color="#5D4037",  # Dark brown background
        foreground_color="#FFFFFF",  # White text
        label_color="#D7CCC8",       # Light tan labels
        logo_text="Premium Coffee Club"
    ),
    images=wp.PassImages(
        logo="images/logo.png",     # Main logo
        icon="images/icon.png",     # Small icon
        thumbnail="images/thumb.png"  # Optional thumbnail image
    )
)
```

### Adding Custom Fields

You can add custom fields to your pass template:

```python
# Add fields to different sections
wp.utils.add_field_to_template(
    template, "header", "tier", "Tier", "Premium"
)

wp.utils.add_field_to_template(
    template, "primary", "points_balance", "Points", "0"
)

wp.utils.add_field_to_template(
    template, "secondary", "expiration", "Expires", "Never"
)

wp.utils.add_field_to_template(
    template, "back", "terms", "Terms & Conditions", 
    "Points never expire. Rewards subject to availability."
)
```

## Adding Locations

You can add location information to trigger notifications when users are near specific locations:

```python
# Create locations
coffee_shop_downtown = wp.utils.create_location(
    latitude=37.7749,
    longitude=-122.4194,
    relevant_text="Welcome to our Downtown location! Show your pass for a free cookie."
)

coffee_shop_uptown = wp.utils.create_location(
    latitude=37.7833,
    longitude=-122.4167,
    relevant_text="Visit our Uptown location and earn double points today!"
)

# Add locations to the template
template = wp.utils.create_loyalty_pass_template(
    # ... other parameters
    locations=[coffee_shop_downtown, coffee_shop_uptown]
)
```

## Common Issues and Troubleshooting

### Authentication Issues

If you encounter authentication problems:

```
Failed to create Google pass: Error getting access token
```

Check that:
- Your service account key file is correctly formatted and readable
- The service account has the proper permissions
- The path to the credentials file is correct in your config

### API Quota and Limits

Google Wallet API has rate limits that may affect high-volume use:

- If you're creating many passes, implement retry logic with exponential backoff
- Consider batching operations when possible
- Monitor your API usage in the Google Cloud Console

### Missing Fields

If fields are missing or not displaying correctly:

- Ensure field IDs are unique across the entire pass
- Check that required fields for the pass type are included
- Verify that the field values are properly formatted

## References

- [Google Wallet API Documentation](https://developers.google.com/wallet)
- [Google Wallet Pass Design Guidelines](https://developers.google.com/wallet/generic/design-guidelines)
- [Google Pay Business Console](https://pay.google.com/business/console/)
