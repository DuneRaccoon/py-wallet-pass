# Web Service Implementation Guide

This guide explains how to implement a web service for pass updates and notifications using the py-wallet-pass SDK. A web service is essential for enabling pass updates, push notifications, and registration of devices.

## Why You Need a Web Service

A web service performs several critical functions for digital wallet passes:

1. **Pass Updates**: Allows you to update passes when information changes (e.g., flight schedules, event times, loyalty points)
2. **Push Notifications**: Sends notifications to users when their passes change
3. **Device Registration**: Tracks which devices have installed which passes
4. **Location Notifications**: Triggers location-based alerts when users are near relevant locations

## Web Service Architecture

### Required Endpoints

For a fully functional wallet pass web service, you'll need to implement these endpoints:

#### For Apple Wallet:

1. **Registration**: `POST /v1/devices/{device_library_identifier}/registrations/{pass_type_identifier}/{serial_number}`
2. **Unregistration**: `DELETE /v1/devices/{device_library_identifier}/registrations/{pass_type_identifier}/{serial_number}`
3. **Pass Updates**: `GET /v1/passes/{pass_type_identifier}/{serial_number}`
4. **Log**: `POST /v1/log`
5. **Latest Versions**: `GET /v1/devices/{device_library_identifier}/registrations/{pass_type_identifier}`

#### For Google Wallet:

Google Wallet doesn't require the same web service endpoints as Apple Wallet. Updates are handled through the Google Wallet API directly. However, you may want similar endpoints for your own record keeping.

#### For Samsung Wallet:

Samsung Wallet requirements are similar to Apple Wallet but with different endpoint structures. Check the Samsung Wallet documentation for specific requirements.

## Implementation Example

Here's a basic implementation using Flask:

```python
from flask import Flask, request, jsonify, abort, send_file
import wallet_pass as wp
import json
import os
from pathlib import Path
import datetime

app = Flask(__name__)

# Initialize the Pass Manager (done once at startup)
config = wp.WalletConfig(
    apple_pass_type_identifier="pass.com.example.passtype",
    apple_team_identifier="ABCDE12345",
    apple_organization_name="Your Company",
    apple_certificate_path="certificates/certificate.pem",
    apple_private_key_path="certificates/key.pem",
    apple_wwdr_certificate_path="certificates/wwdr.pem",
    google_application_credentials="certificates/google_credentials.json",
    google_issuer_id="3388000000022195611",
    samsung_issuer_id="samsung-issuer-123",
    samsung_api_key="samsung-api-key-456",
    samsung_service_id="samsung-service-789",
    web_service_url="https://example.com/wallet",
    storage_path="passes"
)
manager = wp.create_pass_manager(config=config)

# Database for device registrations (in a real app, use a proper database)
REGISTRATIONS_DIR = Path("registrations")
REGISTRATIONS_DIR.mkdir(exist_ok=True)

# Apple Wallet specific endpoints
@app.route('/v1/devices/<device_library_identifier>/registrations/<pass_type_identifier>/<serial_number>', methods=['POST'])
def register_device(device_library_identifier, pass_type_identifier, serial_number):
    """Register a device to receive push notifications for a pass."""
    # Get the push token from the request
    push_token = request.headers.get('pushToken')
    if not push_token:
        abort(400)  # Bad request
    
    # Store the registration
    registration_dir = REGISTRATIONS_DIR / pass_type_identifier / serial_number
    registration_dir.mkdir(parents=True, exist_ok=True)
    
    with open(registration_dir / f"{device_library_identifier}.json", 'w') as f:
        json.dump({
            'device_library_identifier': device_library_identifier,
            'push_token': push_token,
            'registered_at': datetime.datetime.now().isoformat()
        }, f)
    
    return '', 201  # Created

@app.route('/v1/devices/<device_library_identifier>/registrations/<pass_type_identifier>/<serial_number>', methods=['DELETE'])
def unregister_device(device_library_identifier, pass_type_identifier, serial_number):
    """Unregister a device from receiving push notifications for a pass."""
    # Remove the registration
    registration_file = REGISTRATIONS_DIR / pass_type_identifier / serial_number / f"{device_library_identifier}.json"
    
    if registration_file.exists():
        os.remove(registration_file)
        return '', 200  # OK
    else:
        abort(404)  # Not found

@app.route('/v1/passes/<pass_type_identifier>/<serial_number>', methods=['GET'])
def get_latest_pass(pass_type_identifier, serial_number):
    """Get the latest version of a pass."""
    # Authentication
    auth_token = request.headers.get('Authorization', '')
    if not auth_token.startswith('ApplePass '):
        abort(401)  # Unauthorized
    
    # Extract the token
    token = auth_token.replace('ApplePass ', '')
    
    # Validate the token (in a real app, check against your stored token)
    # For this example, we'll assume it's valid
    
    # Construct the pass ID
    pass_id = f"{pass_type_identifier}.{serial_number}"
    
    try:
        # Retrieve the template (in a real app, this would be stored in a database)
        template = None  # You would retrieve this based on the pass_id
        
        # Generate the .pkpass file
        pass_file = manager.apple_pass.generate_pass_file(pass_id, template)
        
        # Create a temporary file
        temp_file = Path(f"temp_{serial_number}.pkpass")
        with open(temp_file, 'wb') as f:
            f.write(pass_file)
        
        # Send the file
        return send_file(
            temp_file,
            mimetype='application/vnd.apple.pkpass',
            as_attachment=True,
            attachment_filename=f"{serial_number}.pkpass"
        )
    except Exception as e:
        print(f"Error generating pass: {e}")
        abort(404)  # Not found

@app.route('/v1/devices/<device_library_identifier>/registrations/<pass_type_identifier>', methods=['GET'])
def get_serial_numbers(device_library_identifier, pass_type_identifier):
    """Get serial numbers of passes that need to be updated."""
    # Get the passesUpdatedSince parameter
    passes_updated_since = request.args.get('passesUpdatedSince')
    if passes_updated_since:
        updated_since = datetime.datetime.fromisoformat(passes_updated_since.replace('Z', '+00:00'))
    else:
        updated_since = datetime.datetime.min
    
    # Get all registrations for this device
    registrations_dir = REGISTRATIONS_DIR / pass_type_identifier
    if not registrations_dir.exists():
        return jsonify({"serialNumbers": [], "lastUpdated": datetime.datetime.now().isoformat()})
    
    # Find all serial numbers registered to this device that have been updated
    serial_numbers = []
    last_updated = updated_since
    
    for serial_dir in registrations_dir.iterdir():
        if serial_dir.is_dir():
            device_file = serial_dir / f"{device_library_identifier}.json"
            if device_file.exists():
                # Check if the pass has been updated
                pass_id = f"{pass_type_identifier}.{serial_dir.name}"
                # In a real app, check your database for the last update time
                # For this example, we'll just return all registered passes
                serial_numbers.append(serial_dir.name)
    
    return jsonify({
        "serialNumbers": serial_numbers,
        "lastUpdated": datetime.datetime.now().isoformat()
    })

@app.route('/v1/log', methods=['POST'])
def log():
    """Log Apple Wallet errors."""
    logs = request.json
    # In a real app, properly log these errors
    print(f"Received logs from Apple Wallet: {logs}")
    return '', 200

# Additional endpoints for your application

@app.route('/api/passes/<pass_id>/send-update', methods=['POST'])
def send_update_notification(pass_id):
    """Trigger an update notification for a pass."""
    try:
        # Get the template (in a real app, this would be stored in a database)
        template = None  # You would retrieve this based on the pass_id
        
        # Send the notification
        result = manager.send_update_notification(pass_id, template)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Setting Up the Web Service

### Using a Framework

You can implement your web service using any web framework you prefer:

- **Flask**: Lightweight and easy to set up
- **Django**: Comprehensive framework with ORM, admin panel, etc.
- **FastAPI**: Modern, fast framework with automatic OpenAPI documentation

### Deployment Options

Consider these deployment options:

1. **Cloud Services**:
   - AWS Lambda + API Gateway
   - Google Cloud Functions
   - Azure Functions
   - Heroku

2. **Traditional Hosting**:
   - VPS with Nginx/Apache
   - Containerized deployment with Docker
   - Kubernetes for larger deployments

### Security Considerations

Your web service handles sensitive information, so implement these security measures:

1. **HTTPS**: Use SSL/TLS for all connections
2. **Authentication**: Validate authentication tokens
3. **Input Validation**: Validate all incoming data
4. **Rate Limiting**: Prevent abuse with rate limiting
5. **Logging**: Implement comprehensive logging for debugging and security

## Database Schema

You'll need to store pass data and device registrations. Here's a suggested schema:

### Passes Table

| Column           | Type          | Description                                  |
|------------------|---------------|----------------------------------------------|
| id               | String        | Unique pass identifier                       |
| template_id      | String        | ID of the template used for the pass         |
| customer_id      | String        | Your system's customer identifier            |
| serial_number    | String        | Serial number of the pass                    |
| data             | JSON/BLOB     | The complete pass data                       |
| voided           | Boolean       | Whether the pass is voided                   |
| created_at       | DateTime      | When the pass was created                    |
| updated_at       | DateTime      | When the pass was last updated               |

### Device Registrations Table

| Column                   | Type          | Description                                  |
|--------------------------|---------------|----------------------------------------------|
| id                       | String        | Unique registration identifier               |
| device_library_identifier| String        | Device identifier from the wallet app        |
| pass_id                  | String        | Pass identifier                              |
| push_token               | String        | Push notification token                      |
| registered_at            | DateTime      | When the device registered                   |
| last_updated             | DateTime      | When the pass was last updated for the device|

## Implementing Push Notifications

### Apple Push Notifications

To send push notifications to Apple Wallet, you'll need:

1. An **Apple Push Certificate**
2. A **Push Notification Service** library

Example using PyAPNs2:

```python
from hyper import HTTPConnection
from hyper.tls import init_context
import json
import base64

def send_apple_push_notification(push_token, pass_type_identifier, serial_number, certificate_path):
    """Send a push notification to Apple Wallet."""
    # Load the certificate
    with open(certificate_path, 'rb') as f:
        certificate = f.read()
    
    # Create a connection to APNs
    context = init_context()
    context.load_cert_chain(certificate_path)
    
    conn = HTTPConnection('api.push.apple.com:443', ssl_context=context)
    
    # Prepare notification payload
    payload = {
        'aps': {},  # Empty payload for pass updates
    }
    
    # Convert payload to JSON
    payload_json = json.dumps(payload)
    
    # Create the request headers
    headers = {
        'apns-topic': pass_type_identifier,
        'apns-push-type': 'background',
    }
    
    # Send the notification
    token_hex = push_token.replace(' ', '')
    path = f'/3/device/{token_hex}'
    
    conn.request('POST', path, payload_json, headers)
    resp = conn.get_response()
    
    return resp.status == 200
```

## Testing Your Web Service

### Local Testing

1. Use **ngrok** to expose your local server to the internet
2. Configure your passes with the ngrok URL as the web service URL

### Test Scenarios

Test these key scenarios:

1. **Device Registration**: Test registering a device for pass updates
2. **Pass Updates**: Test updating a pass and sending notifications
3. **Location Triggers**: Test location-based notifications
4. **Error Handling**: Test how your service handles errors
5. **Load Testing**: Test performance under load for production readiness

## Advanced Topics

### Scaling Your Web Service

As your user base grows, consider:

1. **Caching**: Implement Redis or Memcached for caching
2. **Database Optimization**: Index fields used in frequent queries
3. **Horizontal Scaling**: Use load balancers with multiple instances
4. **Queue Systems**: Use RabbitMQ or Redis for push notification queues
5. **CDN**: Serve static assets via a CDN

### Analytics and Monitoring

Track key metrics:

1. **Usage Statistics**: Track installations, updates, and deletions
2. **Performance Metrics**: Monitor response times and error rates
3. **User Engagement**: Track how often passes are used
4. **Notification Success Rate**: Monitor push notification delivery

## Integrating Multiple Providers

### Unified API

The py-wallet-pass SDK provides a unified API for managing passes across platforms:

```python
# Create a pass for all supported platforms
response = manager.create_pass(pass_data, template)

# Update a pass on all platforms
manager.update_pass(pass_id, updated_data, template)

# Send notifications to all platforms
manager.send_update_notification(pass_id, template)
```

### Platform-Specific Handling

You may need platform-specific code for certain operations:

```python
# Handle Apple-specific registration
if platform == "apple":
    # Process Apple registration
    pass

# Handle Google-specific operations
if platform == "google":
    # Google-specific code
    pass

# Handle Samsung-specific operations
if platform == "samsung":
    # Samsung-specific code
    pass
```

## Conclusion

A well-designed web service is essential for digital wallet pass integration. It enables pass updates, push notifications, and device tracking. By following this guide, you can implement a robust web service that works with Apple Wallet, Google Wallet, and Samsung Wallet.

For more information on platform-specific requirements, refer to:
- [Apple PassKit Web Service Reference](https://developer.apple.com/documentation/passkit/wallet_passes/pass_kit_web_service)
- [Google Wallet API Documentation](https://developers.google.com/wallet)
- [Samsung Wallet Developer Documentation](https://developer.samsung.com/wallet)
