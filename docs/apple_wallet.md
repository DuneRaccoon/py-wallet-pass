# Apple Wallet Integration Guide

This guide explains how to use py-wallet-pass to create and manage Apple Wallet passes (.pkpass files).

## Prerequisites

Before you begin, you'll need:

1. An **Apple Developer account** ($99/year)
2. A **Pass Type ID** created in your developer account
3. A **Pass Type ID certificate** downloaded from Apple
4. Your **Team Identifier** from your Apple Developer account
5. The **Apple Worldwide Developer Relations Certification Authority (WWDR) certificate**

## Setup

### 1. Setting up your Apple Developer Account

1. Log in to your [Apple Developer Account](https://developer.apple.com/)
2. Go to "Certificates, Identifiers & Profiles"
3. Create a new Pass Type ID under "Identifiers"
4. Create a certificate for your Pass Type ID
5. Download the certificate and convert it to PEM format

### 2. Converting Certificates to PEM Format

Convert your certificates to PEM format using the following commands:

```bash
# Convert your Pass Type ID certificate
openssl pkcs12 -in Certificates.p12 -clcerts -nokeys -out certificate.pem

# Extract the private key
openssl pkcs12 -in Certificates.p12 -nocerts -out key.pem

# Remove the passphrase from the private key
openssl rsa -in key.pem -out key_no_pass.pem

# Download and convert the WWDR certificate
curl https://www.apple.com/certificateauthority/AppleWWDRCA.cer -O
openssl x509 -inform der -in AppleWWDRCA.cer -out wwdr.pem
```

## Basic Usage

Here's how to create a simple Apple Wallet pass:

```python
import py_wallet_pass as pwp
import datetime

# Configure the SDK
config = pwp.WalletConfig(
    apple_pass_type_identifier="pass.com.yourcompany.passtype",
    apple_team_identifier="ABCDE12345",  # Your team ID
    apple_organization_name="Your Company Name",
    apple_certificate_path="path/to/certificate.pem",
    apple_private_key_path="path/to/key_no_pass.pem",
    apple_wwdr_certificate_path="path/to/wwdr.pem",
    web_service_url="https://example.com/wallet",  # Optional
    storage_path="passes"  # Where to store pass data
)

# Create a pass manager
manager = pwp.create_pass_manager(config=config)

# Create a template (this example is for an event ticket)
template = pwp.utils.create_event_pass_template(
    name="Summer Festival",
    organization_id="your-company",
    platform="apple",
    style=pwp.PassStyle(
        background_color="#FF5733",
        foreground_color="#FFFFFF",
        label_color="#FFCCCB",
        logo_text="Summer Festival"
    ),
    images=pwp.PassImages(
        logo="images/logo.png",
        icon="images/icon.png",
        strip="images/strip.png"  # Optional header image
    )
)

# Create pass data
event_date = datetime.datetime(2025, 6, 15, 19, 30)
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",
    barcode_message="TICKET123456",
    barcode_alt_text="TICKET123456",
    relevant_date=event_date,  # When the pass becomes relevant
    field_values={
        "event_name": "Summer Festival",
        "event_date": event_date.strftime("%B %d, %Y at %I:%M %p"),
        "event_location": "Central Park, New York",
        "ticket_type": "VIP Access",
        "event_details": "Please arrive 30 minutes before the show."
    }
)

# Create the pass
response = manager.create_pass(pass_data, template)
print(f"Created pass: {response['apple'].id}")

# Generate the .pkpass file
pass_file = manager.generate_pass_files(response['apple'].id, template)

# Save the .pkpass file
with open("ticket.pkpass", "wb") as f:
    f.write(pass_file['apple'])

print("Pass saved to ticket.pkpass")
```

## Pass Updates and Push Notifications

To update an existing pass and send a push notification:

```python
# Update the pass with new information
updated_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",
    serial_number=response['apple'].serial_number,  # Use the same serial number
    barcode_message="TICKET123456",
    barcode_alt_text="TICKET123456",
    field_values={
        "event_name": "Summer Festival",
        "event_date": "June 16, 2025 at 7:30 PM",  # Changed date
        "event_location": "Central Park, New York",
        "ticket_type": "VIP Access",
        "event_details": "RESCHEDULED: Please arrive 30 minutes before the show."
    }
)

# Update the pass
update_response = manager.update_pass(response['apple'].id, updated_data, template)

# Send a push notification to all devices that have this pass
notification_result = manager.send_update_notification(response['apple'].id, template)
print(f"Push notification result: {notification_result}")
```

## Web Service Integration

To support updates and push notifications, you'll need to set up a web service. See the [Web Service Guide](web_service.md) for details.

## Customizing Pass Appearance

You can customize the appearance of your pass by adjusting the `PassStyle` and `PassImages` objects:

```python
style = pwp.PassStyle(
    background_color="#1E3A8A",  # Dark blue background
    foreground_color="#FFFFFF",  # White text
    label_color="#93C5FD",       # Light blue labels
    logo_text="VIP Concert Pass"
)

images = pwp.PassImages(
    logo="images/logo.png",      # Main logo (required)
    icon="images/icon.png",      # Small icon (required)
    strip="images/strip.png",    # Header image (optional)
    background="images/bg.png",  # Background image (optional)
    footer="images/footer.png"   # Footer image (optional)
)
```

## Common Issues and Troubleshooting

### Certificate Problems

If you encounter certificate issues:

```
Failed to generate Apple Wallet pass file: Unable to sign pass
```

Check that:
- All certificates are in valid PEM format
- The private key has its passphrase removed
- The WWDR certificate is current

### Image Issues

If images don't appear correctly:

- Ensure they're in PNG format
- Check that the paths are correct
- Verify the file permissions
- Images must follow Apple's size guidelines (see Apple's PassKit documentation)

## References

- [Apple PassKit Documentation](https://developer.apple.com/documentation/passkit)
- [Pass Design Guidelines](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)
