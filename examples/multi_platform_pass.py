"""Example usage of the py-wallet-pass SDK."""

import datetime
import os
from pathlib import Path

import wallet_pass as wp

def create_multi_platform_pass():
    """Create a pass for both Apple and Google platforms."""
    # Configure the SDK with both platforms
    config = wp.WalletConfig(
        # Apple configuration
        apple_pass_type_identifier="pass.com.example.coupon",
        apple_team_identifier="ABCDE12345",
        apple_organization_name="Example Corp",
        apple_certificate_path="certificates/certificate.pem",
        apple_private_key_path="certificates/key.pem",
        apple_wwdr_certificate_path="certificates/wwdr.pem",
        
        # Google configuration
        google_application_credentials="certificates/google_credentials.json",
        google_issuer_id="3388000000022195611",
        
        # Common configuration
        web_service_url="https://example.com/wallet",
        storage_path="passes"
    )
    
    # Create a pass manager
    manager = wp.create_pass_manager(config=config)
    
    # Create separate templates for each platform
    apple_template = wp.utils.create_coupon_pass_template(
        name="25% Off Everything",
        organization_id="example-corp",
        platform="apple",
        style=wp.PassStyle(
            background_color="#4CAF50",
            foreground_color="#FFFFFF",
            label_color="#E8F5E9",
            logo_text="25% Off"
        )
    )
    
    google_template = wp.utils.create_coupon_pass_template(
        name="25% Off Everything",
        organization_id="example-corp",
        platform="google",
        style=wp.PassStyle(
            background_color="#4CAF50",
            foreground_color="#FFFFFF",
            label_color="#E8F5E9",
            logo_text="25% Off"
        )
    )
    
    # Common expiration date
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
    
    # Create Apple pass data
    apple_pass_data = wp.utils.create_pass_data(
        template_id=apple_template.id,
        customer_id="customer789",
        barcode_message="COUPON25OFF",
        barcode_alt_text="COUPON25OFF",
        expiration_date=expiration_date,
        field_values={
            "offer": "25% Off Your Purchase",
            "expiration": expiration_date.strftime("%B %d, %Y"),
            "promo_code": "SAVE25",
            "terms": "One time use. Cannot be combined with other offers."
        }
    )
    
    # Create Google pass data (same content, different template)
    google_pass_data = wp.utils.create_pass_data(
        template_id=google_template.id,
        customer_id="customer789",
        barcode_message="COUPON25OFF",
        barcode_alt_text="COUPON25OFF",
        expiration_date=expiration_date,
        field_values={
            "offer": "25% Off Your Purchase",
            "expiration": expiration_date.strftime("%B %d, %Y"),
            "promo_code": "SAVE25",
            "terms": "One time use. Cannot be combined with other offers."
        }
    )
    
    # Create the passes
    apple_response = manager.create_pass(apple_pass_data, apple_template, create_for=["apple"])
    google_response = manager.create_pass(google_pass_data, google_template, create_for=["google"])
    
    print(f"Created Apple pass: {apple_response['apple'].id}")
    print(f"Created Google pass: {google_response['google'].id}")
    
    # Generate the pass files
    apple_pass_file = manager.generate_pass_files(apple_response['apple'].id, apple_template)
    google_pass_file = manager.generate_pass_files(google_response['google'].id, google_template)
    
    # Save the files
    os.makedirs("output", exist_ok=True)
    with open("output/coupon_apple.pkpass", "wb") as f:
        f.write(apple_pass_file['apple'])
    
    with open("output/coupon_google.json", "wb") as f:
        f.write(google_pass_file['google'])
    
    print("Saved pass files to:")
    print("- output/coupon_apple.pkpass")
    print("- output/coupon_google.json")
    print(f"Google Pay link: {google_response['google'].google_pass_url}")
    
def main():
    print("\n=== Creating Multi-platform Pass ===")
    create_multi_platform_pass()
    
if __name__ == "__main__":
    main()