"""Example usage of the py-wallet-pass SDK with Samsung Wallet."""

import datetime
import os
from pathlib import Path

import py_wallet_pass as pwp


def create_samsung_membership_card():
    """Create a Samsung Wallet membership card."""
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
        description="Fitness Club Membership Card",
        style=pwp.PassStyle(
            background_color="#1E3A8A",  # Dark blue
            foreground_color="#FFFFFF",  # White
            label_color="#93C5FD",       # Light blue
            logo_text="Fitness Club"
        ),
        images=pwp.PassImages(
            logo="images/fitness_logo.png",
            icon="images/fitness_icon.png"
        )
    )
    
    # Add fields to the template
    pwp.utils.add_field_to_template(
        template, "header", "member_name", "Member", ""
    )
    pwp.utils.add_field_to_template(
        template, "primary", "member_id", "Member ID", ""
    )
    pwp.utils.add_field_to_template(
        template, "secondary", "membership_type", "Membership", ""
    )
    pwp.utils.add_field_to_template(
        template, "secondary", "expiration", "Valid Until", ""
    )
    pwp.utils.add_field_to_template(
        template, "auxiliary", "tier", "Tier", ""
    )
    pwp.utils.add_field_to_template(
        template, "back", "gym_locations", "Club Locations", 
        "Downtown: 123 Main St\nUptown: 456 North Ave\nWestside: 789 West Blvd"
    )
    pwp.utils.add_field_to_template(
        template, "back", "benefits", "Member Benefits", 
        "• Free group fitness classes\n• Unlimited guest passes\n• Access to all locations\n• Discounted personal training"
    )
    
    # Create pass data
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=365)
    member_since = datetime.datetime(2023, 3, 15)
    
    pass_data = pwp.utils.create_pass_data(
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
    
    # Create the pass
    response = manager.create_pass(pass_data, template, create_for=["samsung"])
    print(f"Created Samsung pass: {response['samsung'].id}")
    
    # Generate the pass file
    pass_file = manager.generate_pass_files(response['samsung'].id, template, platforms=["samsung"])
    
    # Save the pass file
    os.makedirs("output", exist_ok=True)
    with open("output/samsung_membership.json", "wb") as f:
        f.write(pass_file['samsung'])
    
    print(f"Saved Samsung pass file to: output/samsung_membership.json")
    
    return response['samsung'].id


def main():
    print("\n=== Creating Samsung Membership Card ===")
    create_samsung_membership_card()


if __name__ == "__main__":
    main()