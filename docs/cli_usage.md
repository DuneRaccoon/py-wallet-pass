# Command Line Interface (CLI) Usage

The py-wallet-pass package includes a command-line interface (CLI) that allows you to create and manage wallet passes directly from the terminal. This is useful for quick tasks, automation, and testing.

## Installation

The CLI is automatically installed when you install the py-wallet-pass package:

```bash
# Basic installation
pip install py-wallet-pass

# With all extras
pip install py-wallet-pass[all]
```

## Basic Commands

The CLI executable is named `wallet-pass`. To see available commands:

```bash
wallet-pass --help
```

You should see output similar to:

```
╔════════════════════════════════════════════════╗
║             py-wallet-pass CLI                ║
║        Create and manage digital wallet passes     ║
╚════════════════════════════════════════════════╝

usage: wallet-pass [-h] {create-template,create-pass,update-pass,void-pass,send-notification} ...

Wallet Pass SDK Command Line Interface

positional arguments:
  {create-template,create-pass,update-pass,void-pass,send-notification}
                        Command to execute
    create-template     Create a new pass template
    create-pass         Create a new wallet pass
    update-pass         Update an existing wallet pass
    void-pass           Void an existing wallet pass
    send-notification   Send a push notification for a pass update

optional arguments:
  -h, --help            show this help message and exit
```

## Configuration File

Many commands require a configuration file. This JSON file contains your wallet provider credentials:

```json
{
  "apple_pass_type_identifier": "pass.com.example.passtype",
  "apple_team_identifier": "ABCDE12345",
  "apple_organization_name": "Your Company",
  "apple_certificate_path": "certificates/certificate.pem",
  "apple_private_key_path": "certificates/key.pem",
  "apple_wwdr_certificate_path": "certificates/wwdr.pem",
  
  "google_application_credentials": "certificates/google_credentials.json",
  "google_issuer_id": "3388000000022195611",
  
  "samsung_issuer_id": "samsung-issuer-123",
  "samsung_api_key": "samsung-api-key-456",
  "samsung_service_id": "samsung-service-789",
  
  "web_service_url": "https://example.com/wallet",
  "storage_path": "passes"
}
```

Save this file as `wallet_config.json` in your project directory.

## Creating Templates

### Template Creation Command

To create a new pass template:

```bash
wallet-pass create-template \
  --config wallet_config.json \
  --name "Summer Music Festival" \
  --organization "example-corp" \
  --type "event" \
  --description "Event ticket for Summer Music Festival" \
  --output "festival_template.json"
```

### Template Types

The `--type` parameter accepts various pass types:

| Type Value           | Description                       | Platform     |
|----------------------|-----------------------------------|--------------|
| `generic`            | Generic pass                      | Apple        |
| `coupon`             | Coupon/offer                      | Apple        |
| `event`              | Event ticket                      | Apple        |
| `boarding`           | Boarding pass                     | Apple        |
| `loyalty`            | Loyalty/store card                | Apple        |
| `google-offer`       | Offer/coupon                      | Google       |
| `google-loyalty`     | Loyalty program                   | Google       |
| `google-gift`        | Gift card                         | Google       |
| `google-event`       | Event ticket                      | Google       |
| `google-flight`      | Flight boarding pass              | Google       |
| `google-transit`     | Transit pass                      | Google       |
| `samsung-coupon`     | Coupon                            | Samsung      |
| `samsung-membership` | Membership card                   | Samsung      |
| `samsung-ticket`     | Ticket                            | Samsung      |
| `samsung-boarding`   | Boarding pass                     | Samsung      |
| `samsung-voucher`    | Voucher                           | Samsung      |

## Creating Passes

### Pass Creation Command

To create a new wallet pass from a template:

```bash
wallet-pass create-pass \
  --config wallet_config.json \
  --template festival_template.json \
  --customer-id "customer123" \
  --serial-number "TICKET987654" \
  --barcode "TICKET987654" \
  --barcode-alt "TICKET987654" \
  --fields pass_fields.json \
  --platforms "apple,google" \
  --output-dir "passes" \
  --output-prefix "festival"
```

### Field Values

The `--fields` parameter accepts a JSON file with field values:

```json
{
  "event_name": "Summer Music Festival",
  "event_date": "June 15, 2025 at 7:30 PM",
  "event_location": "Central Park, New York",
  "ticket_type": "VIP Access",
  "event_details": "Please arrive 30 minutes before the show."
}
```

Save this file as `pass_fields.json`.

### Platform Selection

Use the `--platforms` parameter to specify which wallet platforms to target:

```bash
# Create for Apple Wallet only
--platforms "apple"

# Create for Google Wallet only
--platforms "google"

# Create for Samsung Wallet only
--platforms "samsung"

# Create for multiple platforms
--platforms "apple,google,samsung"
```

If omitted, the pass will be created for all supported platforms.

## Updating Passes

### Pass Update Command

To update an existing wallet pass:

```bash
wallet-pass update-pass \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json \
  --customer-id "customer123" \
  --serial-number "TICKET987654" \
  --barcode "TICKET987654" \
  --barcode-alt "TICKET987654" \
  --fields updated_fields.json \
  --platforms "apple,google" \
  --output-dir "passes" \
  --output-prefix "festival_updated"
```

### Updated Field Values

Create a JSON file with the updated field values:

```json
{
  "event_name": "Summer Music Festival",
  "event_date": "June 16, 2025 at 8:00 PM",
  "event_location": "Central Park, New York",
  "ticket_type": "VIP Access",
  "event_details": "RESCHEDULED: Please arrive 30 minutes before the show."
}
```

Save this file as `updated_fields.json`.

## Voiding Passes

To mark a pass as void (no longer valid):

```bash
wallet-pass void-pass \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json \
  --platforms "apple,google"
```

## Sending Notifications

To send a push notification for an updated pass:

```bash
wallet-pass send-notification \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json \
  --platforms "apple,google"
```

## Examples

### Complete Workflow Example

Here's a complete workflow example for creating and managing an event ticket:

```bash
# 1. Create a template
wallet-pass create-template \
  --config wallet_config.json \
  --name "Summer Music Festival" \
  --organization "example-corp" \
  --type "event" \
  --output "festival_template.json"

# 2. Create a pass
wallet-pass create-pass \
  --config wallet_config.json \
  --template festival_template.json \
  --customer-id "customer123" \
  --barcode "TICKET987654" \
  --fields pass_fields.json \
  --output-dir "passes" \
  --output-prefix "festival"

# 3. Update the pass (e.g., when the event is rescheduled)
wallet-pass update-pass \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json \
  --customer-id "customer123" \
  --serial-number "TICKET987654" \
  --barcode "TICKET987654" \
  --fields updated_fields.json \
  --output-dir "passes" \
  --output-prefix "festival_updated"

# 4. Send a notification to inform the user about the update
wallet-pass send-notification \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json

# 5. Void the pass (e.g., after the event)
wallet-pass void-pass \
  --config wallet_config.json \
  --pass-id "pass.com.example.passtype.TICKET987654" \
  --template festival_template.json
```

### Multi-Platform Pass Example

Create a loyalty card for all three wallet platforms:

```bash
# Create a loyalty card template
wallet-pass create-template \
  --config wallet_config.json \
  --name "Coffee Rewards" \
  --organization "coffee-company" \
  --type "loyalty" \
  --output "loyalty_template.json"

# Create a loyalty card for Apple, Google, and Samsung
wallet-pass create-pass \
  --config wallet_config.json \
  --template loyalty_template.json \
  --customer-id "member456" \
  --barcode "MEMBER456789" \
  --fields loyalty_fields.json \
  --platforms "apple,google,samsung" \
  --output-dir "passes" \
  --output-prefix "coffee_rewards"
```

With the `loyalty_fields.json` file:

```json
{
  "member_name": "John Smith",
  "points": "450",
  "member_since": "January 15, 2023",
  "membership_level": "Gold",
  "program_details": "Earn 1 point for every $1 spent."
}
```

## Automation and Integration

The CLI is designed to be used in scripts and automated workflows.

### Bash Script Example

Here's a bash script that creates passes for multiple customers:

```bash
#!/bin/bash

# Load customer data from a CSV file
while IFS=, read -r customer_id name email points level join_date
do
  # Skip header row
  if [ "$customer_id" != "customer_id" ]; then
    # Create a temp JSON file with field values
    cat > temp_fields.json << EOF
{
  "member_name": "$name",
  "points": "$points",
  "member_since": "$join_date",
  "membership_level": "$level",
  "program_details": "Earn 1 point for every $1 spent."
}
EOF

    # Create the pass
    wallet-pass create-pass \
      --config wallet_config.json \
      --template loyalty_template.json \
      --customer-id "$customer_id" \
      --barcode "MEMBER$customer_id" \
      --barcode-alt "MEMBER$customer_id" \
      --fields temp_fields.json \
      --output-dir "passes/$customer_id" \
      --output-prefix "coffee_rewards"
    
    # Optional: email the pass to the customer
    echo "Created pass for $name ($email)"
  fi
done < customers.csv

# Clean up
rm temp_fields.json
```

### Integration with Web Services

You can integrate the CLI with web services using a simple wrapper script:

```python
#!/usr/bin/env python
import subprocess
import sys
import json

def create_pass(customer_data):
    """Create a pass based on customer data."""
    # Write field values to a temp file
    with open('temp_fields.json', 'w') as f:
        json.dump({
            "member_name": customer_data["name"],
            "points": str(customer_data["points"]),
            "member_since": customer_data["join_date"],
            "membership_level": customer_data["level"]
        }, f)
    
    # Build the command
    cmd = [
        "wallet-pass", "create-pass",
        "--config", "wallet_config.json",
        "--template", "loyalty_template.json",
        "--customer-id", customer_data["id"],
        "--barcode", f"MEMBER{customer_data['id']}",
        "--fields", "temp_fields.json",
        "--output-dir", "passes",
        "--output-prefix", f"customer_{customer_data['id']}"
    ]
    
    # Execute the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

if __name__ == "__main__":
    # Parse input data
    customer_data = json.loads(sys.stdin.read())
    
    # Create the pass
    success, stdout, stderr = create_pass(customer_data)
    
    # Output result
    result = {
        "success": success,
        "output": stdout,
        "error": stderr
    }
    print(json.dumps(result))
```

This script can be called from a web service:

```python
# In your web framework (e.g., Flask)
@app.route('/api/create-pass', methods=['POST'])
def api_create_pass():
    customer_data = request.json
    
    # Call the wrapper script
    process = subprocess.Popen(
        ['./create_pass_wrapper.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Pass the customer data and get the result
    stdout, stderr = process.communicate(input=json.dumps(customer_data).encode())
    
    try:
        result = json.loads(stdout)
        return jsonify(result)
    except:
        return jsonify({
            "success": False,
            "error": "Failed to create pass"
        }), 500
```

## Troubleshooting

### Common Issues

#### Command Not Found

If you get "command not found" when running `wallet-pass`:

```bash
# Check if the package is installed
pip list | grep py-wallet-pass

# Ensure the script directory is in your PATH
echo $PATH

# You can run it with the full path
python -m py_wallet_pass.cli --help
```

#### Configuration Errors

If you get errors related to configuration:

```
Missing required Apple Wallet configuration fields: apple_pass_type_identifier, apple_team_identifier
```

Ensure your configuration file contains all required fields for the platforms you're targeting.

#### File Not Found Errors

If you get "file not found" errors:

```
Error: Certificate file not found: certificates/certificate.pem
```

Check that all file paths in your configuration are correct and accessible.

### Logging and Debugging

The CLI uses loguru for logging. To see more detailed logs:

```bash
# Set environment variable for debug logging
export PYTHONUNBUFFERED=1
export LOG_LEVEL=DEBUG

# Run the command
wallet-pass create-pass --config wallet_config.json ...
```

To save logs to a file:

```bash
# Set log directory
export PY_WALLET_PASS_LOG_DIR=./logs

# Run the command
wallet-pass create-pass --config wallet_config.json ...
```

## Advanced Usage

### Custom Storage

You can specify a custom storage path in your configuration:

```json
{
  "storage_path": "/path/to/custom/storage",
  ...
}
```

This is useful for:
- Storing passes in a shared location
- Using network storage or cloud storage
- Separating passes by environment (development, staging, production)

### Using Environment Variables

You can use environment variables in your configuration file:

```json
{
  "apple_certificate_path": "${APPLE_CERT_PATH}",
  "google_application_credentials": "${GOOGLE_CREDENTIALS_PATH}",
  ...
}
```

Then set the environment variables:

```bash
export APPLE_CERT_PATH=/path/to/certificates/certificate.pem
export GOOGLE_CREDENTIALS_PATH=/path/to/google_credentials.json
```

This is useful for:
- Keeping sensitive information out of configuration files
- Using different configurations for different environments
- CI/CD pipelines

## Conclusion

The py-wallet-pass CLI provides a convenient way to create and manage wallet passes from the command line. It's perfect for automation, batch processing, and integration with other systems.

For more information on the wallet pass formats and options, see:
- [Pass Customization Guide](pass_customization.md)
- [Apple Wallet Integration](apple_wallet.md)
- [Google Wallet Integration](google_wallet.md)
- [Samsung Wallet Integration](samsung_wallet.md)
