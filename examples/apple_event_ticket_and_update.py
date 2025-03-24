"""Example usage of the py-wallet-pass SDK."""

import datetime
import os
from pathlib import Path

import wallet_pass as wp


def create_apple_event_ticket():
    """Create an Apple Wallet event ticket."""
    # Configure the SDK
    config = wp.WalletConfig(
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
    manager = wp.create_pass_manager(config=config)
    
    # Create an event ticket template
    template = wp.utils.create_event_pass_template(
        name="Summer Music Festival",
        organization_id="example-corp",
        platform="apple",
        style=wp.PassStyle(
            background_color="#FF5733",
            foreground_color="#FFFFFF",
            label_color="#FFCCCB",
            logo_text="Summer Festival"
        ),
        images=wp.PassImages(
            logo="images/logo.png",
            icon="images/icon.png",
            strip="images/strip.png"
        )
    )
    
    # Add some custom fields
    wp.utils.add_field_to_template(
        template, "auxiliary", "stage", "Stage", "Main Stage"
    )
    
    # Create pass data
    concert_date = datetime.datetime(2025, 6, 1, 19, 0)
    pass_data = wp.utils.create_pass_data(
        template_id=template.id,
        customer_id="customer123",
        barcode_message="TICKET123456",
        barcode_alt_text="TICKET123456",
        relevant_date=concert_date,
        field_values={
            "event_name": "Summer Music Festival",
            "event_date": concert_date.strftime("%B %d, %Y at %I:%M %p"),
            "event_location": "Central Park, New York",
            "ticket_type": "VIP Access",
            "stage": "Main Stage",
            "event_details": "Please arrive 30 minutes before the show. No refunds."
        }
    )
    
    # Create the pass
    response = manager.create_pass(pass_data, template)
    print(f"Created pass: {response['apple'].id}")
    
    # Generate the .pkpass file
    pass_file = manager.generate_pass_files(response['apple'].id, template)
    
    # Save the .pkpass file
    os.makedirs("output", exist_ok=True)
    with open("output/concert_ticket.pkpass", "wb") as f:
        f.write(pass_file['apple'])
    
    print(f"Saved pass file to: output/concert_ticket.pkpass")
    
    return response['apple'].id

def update_pass_example(pass_id: str):
    """Example of updating an existing pass."""
    # Configure the SDK
    config = wp.WalletConfig(
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
    manager = wp.create_pass_manager(config=config)
    
    # Get the existing pass (this would typically be stored in your database)
    response = manager.apple_pass.get_pass(pass_id)
    
    # Retrieve the template (in a real app, you'd store this)
    # For this example, we'll create a new template with the same ID
    template = wp.utils.create_event_pass_template(
        name="Summer Music Festival",
        organization_id="example-corp",
        platform="apple"
    )
    template.id = response.template_id
    
    # Create updated pass data with new values
    concert_date = datetime.datetime(2025, 6, 2, 20, 0)  # Changed date/time
    pass_data = wp.utils.create_pass_data(
        template_id=template.id,
        customer_id=response.customer_id,
        serial_number=response.serial_number,
        barcode_message="TICKET123456",
        barcode_alt_text="TICKET123456",
        relevant_date=concert_date,
        field_values={
            "event_name": "Summer Music Festival",
            "event_date": concert_date.strftime("%B %d, %Y at %I:%M %p"),  # Updated date
            "event_location": "Central Park, New York",
            "ticket_type": "VIP Access",
            "event_details": "RESCHEDULED: Please arrive 30 minutes before the show. No refunds."  # Updated details
        }
    )
    
    # Update the pass
    updated_response = manager.update_pass(pass_id, pass_data, template)
    print(f"Updated pass: {updated_response['apple'].id}")
    
    # Generate the updated .pkpass file
    pass_file = manager.generate_pass_files(updated_response['apple'].id, template)
    
    # Save the updated .pkpass file
    os.makedirs("output", exist_ok=True)
    with open("output/updated_concert_ticket.pkpass", "wb") as f:
        f.write(pass_file['apple'])
    
    print(f"Saved updated pass file to: output/updated_concert_ticket.pkpass")
    
    # Send push notification for the update
    notification_result = manager.send_update_notification(pass_id, template)
    print(f"Push notification result: {notification_result}")


def main():
    """Run the examples."""
    print("=== Creating Apple Event Ticket ===")
    apple_pass_id = create_apple_event_ticket()
    
    print("\n=== Updating an Existing Pass ===")
    update_pass_example(apple_pass_id)


if __name__ == "__main__":
    main()