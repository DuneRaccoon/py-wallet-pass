# Py-Wallet-Pass

A Python SDK for easily creating and managing digital wallet passes for both Apple Wallet and Google Wallet platforms.

## Features

- Create, update, and manage digital passes for both Apple Wallet (.pkpass) and Google Wallet
- Support for all pass types:
  - Event tickets
  - Coupons and offers
  - Loyalty cards
  - Boarding passes
  - Store cards
  - Generic passes
- Simplified API for creating passes for both platforms with a single codebase
- Support for all pass features including barcodes, expiration dates, locations, and more
- Utility functions for common pass creation scenarios
- Local storage of pass data for retrieval and updates

## Installation

```bash
# Basic installation
pip install py-wallet-pass

# With Google Wallet support
pip install py-wallet-pass[google]

# With all extras
pip install py-wallet-pass[all]
```

Using Poetry:

```bash
# Basic installation
poetry add py-wallet-pass

# With Google Wallet support
poetry add "py-wallet-pass[google]"
```

## Quick Start

### Creating an Apple Wallet Event Ticket

```python
import py_wallet_pass as pwp

# Configure the SDK
config = pwp.WalletConfig(
    apple_pass_type_identifier="pass.com.example.eventticket",
    apple_team_identifier="ABCDE12345",
    apple_organization_name="Example Corp",
    apple_certificate_path="certificates/certificate.pem",
    apple_private_key_path="certificates/key.pem",
    apple_wwdr_certificate_path="certificates/wwdr.pem",
    web_service_url="https://example.com/wallet",
    storage_path="passes"
)

# Create a pass manager
manager = pwp.create_pass_manager(config=config)

# Create an event ticket template
template = pwp.utils.create_event_pass_template(
    name="Summer Music Festival",
    organization_id="example-corp",
    platform="apple"
)

# Create pass data
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer123",
    barcode_message="TICKET123456",
    field_values={
        "event_name": "Summer Music Festival",
        "event_date": "June 1, 2025 at 7:00 PM",
        "event_location": "Central Park, New York",
        "ticket_type": "VIP Access"
    }
)

# Create the pass
response = manager.create_pass(pass_data, template)

# Generate the .pkpass file
pass_file = manager.generate_pass_files(response['apple'].id, template)

# Save the .pkpass file
with open("concert_ticket.pkpass", "wb") as f:
    f.write(pass_file['apple'])
```

### Creating a Google Wallet Loyalty Card

```python
import py_wallet_pass as pwp

# Configure the SDK
config = pwp.WalletConfig(
    google_application_credentials="certificates/google_credentials.json",
    google_issuer_id="3388000000022195611",
    web_service_url="https://example.com/wallet",
    storage_path="passes"
)

# Create a pass manager
manager = pwp.create_pass_manager(config=config)

# Create a loyalty card template
template = pwp.utils.create_loyalty_pass_template(
    name="Coffee Rewards",
    organization_id="example-corp",
    platform="google"
)

# Create pass data
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="customer456",
    barcode_message="MEMBER456789",
    field_values={
        "member_name": "John Smith",
        "points": "450",
        "member_since": "January 15, 2023",
        "membership_level": "Gold"
    }
)

# Create the pass
response = manager.create_pass(pass_data, template)

# Print the Google Pay link for the pass
print(f"Google Pay link: {response['google'].google_pass_url}")
```

## Apple Wallet Pass Requirements

To create Apple Wallet passes, you need:

1. An Apple Developer account
2. A Pass Type ID certificate
3. Your Team Identifier
4. The WWDR certificate (Apple Worldwide Developer Relations Certificate)

## Google Wallet Pass Requirements

To create Google Wallet passes, you need:

1. A Google Cloud Platform account
2. A service account with appropriate permissions
3. An issuer ID from the Google Pay and Wallet Console

## Documentation

For more detailed examples and API documentation, see the [examples](examples/) directory and the full [documentation](docs/).

## License

MIT