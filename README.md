# Py-Wallet-Pass

A Python SDK for easily creating and managing digital wallet passes for Apple Wallet, Google Wallet, and Samsung Wallet platforms.

## Features

- Create, update, and manage digital passes for multiple wallet platforms:
  - Apple Wallet (.pkpass)
  - Google Wallet 
  - Samsung Wallet
- Support for all pass types:
  - Event tickets
  - Coupons and offers
  - Loyalty cards
  - Boarding passes
  - Store cards
  - Membership cards
  - Generic passes
- Flexible storage backends:
  - File system storage
  - In-memory storage (for testing)
  - Extensible for custom storage solutions
- Simplified API for creating passes with a single codebase
- Powerful utility functions for common pass creation scenarios
- Command-line interface for easy management
- Comprehensive test suite

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

### Creating a Samsung Wallet Membership Card

```python
import py_wallet_pass as pwp

# Configure the SDK
config = pwp.WalletConfig(
    samsung_issuer_id="samsung-issuer-123",
    samsung_api_key="samsung-api-key-456",
    samsung_service_id="samsung-service-789",
    samsung_api_base_url="https://wallet-api.samsung.com/v1",
    web_service_url="https://example.com/wallet",
    storage_path="passes"
)

# Create a pass manager
manager = pwp.create_pass_manager(config=config)

# Create a membership card template
template = pwp.utils.create_template(
    name="Fitness Club Membership",
    organization_id="example-fitness",
    pass_type=pwp.PassType.SAMSUNG_MEMBERSHIP,
    description="Fitness Club Membership Card"
)

# Add fields to the template
pwp.utils.add_field_to_template(
    template, "header", "member_name", "Member", ""
)
pwp.utils.add_field_to_template(
    template, "primary", "member_id", "Member ID", ""
)

# Create pass data
pass_data = pwp.utils.create_pass_data(
    template_id=template.id,
    customer_id="member-9876",
    barcode_message="MEMBER9876543",
    field_values={
        "member_name": "Sarah Johnson",
        "member_id": "9876543"
    }
)

# Create the pass
response = manager.create_pass(pass_data, template, create_for=["samsung"])

# Generate and save the pass file
pass_file = manager.generate_pass_files(response['samsung'].id, template)
with open("membership_card.json", "wb") as f:
    f.write(pass_file['samsung'])
```

## Using Custom Storage Backends

By default, the SDK uses the filesystem to store pass data. You can create a custom storage backend by implementing the `StorageBackend` interface:

```python
import py_wallet_pass as pwp

# Create a custom storage backend
class RedisStorage(pwp.StorageBackend):
    def __init__(self, redis_client):
        self.client = redis_client
    
    def store_pass(self, provider, pass_id, pass_data):
        key = f"{provider}:{pass_id}"
        self.client.set(key, json.dumps(pass_data))
    
    def retrieve_pass(self, provider, pass_id):
        key = f"{provider}:{pass_id}"
        data = self.client.get(key)
        if not data:
            raise KeyError(f"Pass not found: {pass_id}")
        return json.loads(data)
    
    def delete_pass(self, provider, pass_id):
        key = f"{provider}:{pass_id}"
        return bool(self.client.delete(key))
    
    def list_passes(self, provider):
        pattern = f"{provider}:*"
        keys = self.client.keys(pattern)
        return [key.split(':', 1)[1] for key in keys]

# Use the custom storage backend
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
storage = RedisStorage(redis_client)

config = pwp.WalletConfig(...)
manager = pwp.create_pass_manager(config=config, storage=storage)
```

## Command Line Interface

The package includes a command-line interface for managing wallet passes:

```bash
# Create a template
wallet-pass create-template --config config.json --name "Event Ticket" --organization "example-corp" --type "event"

# Create a pass
wallet-pass create-pass --config config.json --template template.json --customer-id "customer123" --barcode "TICKET123456"

# Update a pass
wallet-pass update-pass --config config.json --pass-id "pass.com.example.123" --template template.json --customer-id "customer123"

# Void a pass
wallet-pass void-pass --config config.json --pass-id "pass.com.example.123" --template template.json

# Send a notification
wallet-pass send-notification --config config.json --pass-id "pass.com.example.123" --template template.json
```

## Wallet Platform Requirements

### Apple Wallet Pass Requirements

To create Apple Wallet passes, you need:

1. An Apple Developer account
2. A Pass Type ID certificate
3. Your Team Identifier
4. The WWDR certificate (Apple Worldwide Developer Relations Certificate)

### Google Wallet Pass Requirements

To create Google Wallet passes, you need:

1. A Google Cloud Platform account
2. A service account with appropriate permissions
3. An issuer ID from the Google Pay and Wallet Console

### Samsung Wallet Pass Requirements

To create Samsung Wallet passes, you need:

1. A Samsung Wallet developer account
2. An issuer ID, API key, and service ID from the Samsung Wallet portal

## Examples

For more detailed examples, check out the [examples](examples/) directory:

- [Apple Event Ticket and Update](examples/apple_event_ticket_and_update.py)
- [Google Loyalty Card](examples/google_loyalty_card.py)
- [Multi-Platform Pass](examples/multi_platform_pass.py)
- [Samsung Membership Card](examples/samsung_membership_card.py)

## License

MIT