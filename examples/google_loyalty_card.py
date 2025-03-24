"""Example usage of the py-wallet-pass SDK."""

import datetime
import os
from pathlib import Path

import py_wallet_pass as pwp


def create_google_loyalty_card():
    """Create a Google Wallet loyalty card."""
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
        platform="google",
        style=pwp.PassStyle(
            background_color="#8B4513",
            foreground_color="#FFFFFF",
            label_color="#D2B48C",
            logo_text="Coffee Rewards"
        ),
        images=pwp.PassImages(
            logo="images/logo.png",
            icon="images/icon.png"
        )
    )
    
    # Add some custom fields
    pwp.utils.add_field_to_template(
        template, "back", "rewards", "Rewards", "10 points = Free coffee"
    )
    
    # Create pass data
    member_since = datetime.datetime(2023, 1, 15)
    pass_data = pwp.utils.create_pass_data(
        template_id=template.id,
        customer_id="customer456",
        barcode_message="MEMBER456789",
        barcode_alt_text="MEMBER456789",
        field_values={
            "member_name": "John Smith",
            "points": "450",
            "member_since": member_since.strftime("%B %d, %Y"),
            "membership_level": "Gold",
            "program_details": "Earn 1 point for every $1 spent.",
            "rewards": "10 points = Free coffee\n50 points = Free pastry\n100 points = Free lunch"
        }
    )
    
    # Create the pass
    response = manager.create_pass(pass_data, template)
    print(f"Created pass: {response['google'].id}")
    
    # Generate the Google Wallet JSON file
    pass_file = manager.generate_pass_files(response['google'].id, template)
    
    # Save the JSON file
    os.makedirs("output", exist_ok=True)
    with open("output/loyalty_card.json", "wb") as f:
        f.write(pass_file['google'])
    
    print(f"Saved pass file to: output/loyalty_card.json")
    print(f"Google Pay link: {response['google'].google_pass_url}")
    
    return response['google'].id

def main():
    print("\n=== Creating Google Loyalty Card ===")
    create_google_loyalty_card()
    

if __name__ == "__main__":
    main()