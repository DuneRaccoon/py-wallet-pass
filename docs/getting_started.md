# Getting Started with py-wallet-pass

This guide will help you get started with the py-wallet-pass SDK to create and manage digital wallet passes for Apple Wallet, Google Wallet, and Samsung Wallet.

## Installation

First, install the SDK using pip:

```bash
# Basic installation
pip install py-wallet-pass

# With all extras
pip install py-wallet-pass[all]
```

## Initial Setup

### 1. Import the SDK

```python
import py_wallet_pass as pwp
import datetime
```

### 2. Configure the SDK

Create a `WalletConfig` object with your platform credentials:

```python
config = pwp.WalletConfig(
    # Apple configuration (optional if not using Apple Wallet)
    apple_pass_type_identifier="pass.com.example.passtype",
    apple_team_identifier="ABCDE12345",
    apple_organization_name="Your Company",
    apple_certificate_path="certificates/certificate.pem",
    apple_private_key_path="certificates/key.pem",
    apple_wwdr_certificate_path="certificates/wwdr.pem",
    
    # Google configuration (optional if not using Google Wallet)
    google_application_credentials="certificates/google_credentials.json",
    google_issuer_id="3388000000022195611",
    
    # Samsung configuration (optional if not using Samsung Wallet)
    samsung_issuer_id="samsung-issuer-123",
    samsung_api_key="samsung-api-key-456",
    samsung_service_id="samsung-service-789",
    
    # Common configuration
    web_service_url="https://example.com/wallet",  # For updates and notifications
    storage_path="passes"  # Where to store pass data
)
```

### 3. Create a Pass Manager

The pass manager is your main interface to create and manage passes:

```python
manager = pwp.create_pass_manager(config=config)
```

## Creating a Pass

### 1. Create a Pass Template

Templates define the structure and appearance of your passes. You can use the helper functions for common pass types:

```python
# Create an event ticket template
template = pwp.utils.create_event_pass_template(
    name="Summer Music Festival",
    organization_id="example-corp",
    platform="both",  # Create for both Apple and Google
    style=pwp.PassStyle(
        background_color="#FF5733",  # Background color
        foreground_color="#FFFFFF",  # Text color
        label_color="#FFCCCB",       # Label color
        logo_text="Summer Festival"  # Text displayed near the logo
    ),
    images=pwp.PassImages(
        logo="images/logo.png",  # Main logo
        icon="images/icon.png"   # Small icon
    )
)
```

The SDK includes helper functions for different pass types:
- `create_event_pass_template()` - For event tickets
- `create_coupon_pass_template()` - For coupons and offers
- `create_loyalty_pass_template()` - For loyalty cards
- `create_boarding_pass_template()` - For boarding passes

### 2. Create Pass Data

Next, create the data for your pass:

```python
# Set the event date
event_date = datetime.datetime(2025, 6, 15, 19, 30)

# Create pass data
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",  # Unique identifier for the customer
    barcode_message="TICKET123456",  # Content for the barcode
    barcode_alt_text="TICKET123456",  # Text displayed under the barcode
    relevant_date=event_date,  # When the pass becomes relevant
    field_values={
        # Values for the template fields
        "event_name": "Summer Music Festival",
        "event_date": event_date.strftime("%B %d, %Y at %I:%M %p"),
        "event_location": "Central Park, New York",
        "ticket_type": "VIP Access",
        "event_details": "Please arrive 30 minutes before the show."
    }
)
```

### 3. Create the Pass

Now create the actual pass:

```python
# Create the pass
response = manager.create_pass(pass_data, template)

# The response contains pass info for each platform
apple_pass_id = response['apple'].id
google_pass_id = response['google'].id

print(f"Created Apple Pass: {apple_pass_id}")
print(f"Created Google Pass: {google_pass_id}")

# Get the Google Wallet URL (can be sent to users)
google_pass_url = response['google'].google_pass_url
print(f"Google Wallet URL: {google_pass_url}")
```

### 4. Generate Pass Files

Generate the pass files that users can add to their wallets:

```python
# Generate all pass files
pass_files = manager.generate_pass_files(response['apple'].id, template)

# Save the Apple Wallet .pkpass file
with open("ticket.pkpass", "wb") as f:
    f.write(pass_files['apple'])

# Save the Google Wallet JSON file
with open("ticket_google.json", "wb") as f:
    f.write(pass_files['google'])

print("Pass files saved!")
```

## Updating a Pass

You can update an existing pass and notify users of changes:

```python
# Create updated pass data
updated_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",
    serial_number=response['apple'].serial_number,  # Use the same serial number
    barcode_message="TICKET123456",
    barcode_alt_text="TICKET123456",
    relevant_date=datetime.datetime(2025, 6, 16, 20, 0),  # Updated date
    field_values={
        "event_name": "Summer Music Festival",
        "event_date": "June 16, 2025 at 8:00 PM",  # Updated time
        "event_location": "Central Park, New York",
        "ticket_type": "VIP Access",
        "event_details": "RESCHEDULED: Please arrive 30 minutes before the show."
    }
)

# Update the pass
update_response = manager.update_pass(apple_pass_id, updated_data, template)

# Send push notifications to users
notification_result = manager.send_update_notification(apple_pass_id, template)
print(f"Push notification sent: {notification_result}")
```

## Platform-Specific Integration

For more detailed information on integrating with specific wallet platforms, see:
- [Apple Wallet Integration](apple_wallet.md)
- [Google Wallet Integration](google_wallet.md)
- [Samsung Wallet Integration](samsung_wallet.md)

## Next Steps

- Learn how to [set up a web service](web_service.md) for pass updates and notifications
- See how to [customize pass appearance](pass_customization.md) for each platform
- Explore the [CLI tools](cli_usage.md) for managing passes from the command line