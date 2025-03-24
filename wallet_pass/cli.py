"""Command-line interface for the wallet pass SDK."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from . import create_pass_manager, WalletConfig
from .schema.core import PassType, PassData, PassTemplate
from .logging import get_logger, with_context
from .utils import (
    create_template, add_field_to_template, create_pass_data,
    create_event_pass_template, create_coupon_pass_template,
    create_loyalty_pass_template, create_boarding_pass_template
)

logger = get_logger(__name__)


def load_config(config_file: str) -> WalletConfig:
    """Load configuration from a JSON file."""
    with open(config_file, 'r') as f:
        config_dict = json.load(f)
    
    return WalletConfig.from_dict(config_dict)


def create_template_cli(args: argparse.Namespace) -> None:
    """Create a new pass template."""
    context = with_context(command="create-template", name=args.name, type=args.type)
    logger.info(f"📂 Creating {args.type} template: {args.name}")
    
    # Load configuration
    config = load_config(args.config)
    
    # Determine the pass type
    pass_type_map = {
        'generic': PassType.APPLE_GENERIC,
        'coupon': PassType.APPLE_COUPON,
        'event': PassType.APPLE_EVENTTICKET,
        'boarding': PassType.APPLE_BOARDINGPASS,
        'loyalty': PassType.APPLE_STORECARD,
        'google-offer': PassType.GOOGLE_OFFER,
        'google-loyalty': PassType.GOOGLE_LOYALTY,
        'google-gift': PassType.GOOGLE_GIFT_CARD,
        'google-event': PassType.GOOGLE_EVENT_TICKET,
        'google-flight': PassType.GOOGLE_FLIGHT,
        'google-transit': PassType.GOOGLE_TRANSIT,
        'samsung-coupon': PassType.SAMSUNG_COUPON,
        'samsung-membership': PassType.SAMSUNG_MEMBERSHIP,
        'samsung-ticket': PassType.SAMSUNG_TICKET,
        'samsung-boarding': PassType.SAMSUNG_BOARDING,
        'samsung-voucher': PassType.SAMSUNG_VOUCHER,
    }
    
    pass_type = pass_type_map.get(args.type)
    if not pass_type:
        logger.error(f"❌ Unknown pass type: {args.type}")
        sys.exit(1)
    
    try:
        # Create the template
        template = create_template(
            name=args.name,
            organization_id=args.organization,
            pass_type=pass_type,
            description=args.description
        )
        
        # Save the template to a file
        template_file = Path(args.output) if args.output else Path(f"{args.name.lower().replace(' ', '_')}_template.json")
        with open(template_file, 'w') as f:
            f.write(template.json(indent=2))
        
        logger.success(f"✅ Template created and saved to {template_file}")
    except Exception as e:
        logger.error(f"❌ Failed to create template: {e}")
        sys.exit(1)


def create_pass_cli(args: argparse.Namespace) -> None:
    """Create a new wallet pass."""
    # Load configuration
    config = load_config(args.config)
    
    # Create pass manager
    manager = create_pass_manager(config=config)
    
    # Load template
    with open(args.template, 'r') as f:
        template_dict = json.load(f)
        template = PassTemplate.parse_obj(template_dict)
    
    # Load field values if provided
    field_values = {}
    if args.fields:
        with open(args.fields, 'r') as f:
            field_values = json.load(f)
    
    # Create pass data
    pass_data = create_pass_data(
        template_id=template.id,
        customer_id=args.customer_id,
        serial_number=args.serial_number,
        barcode_message=args.barcode,
        barcode_alt_text=args.barcode_alt,
        field_values=field_values
    )
    
    # Determine which platforms to create for
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Create the pass
    response = manager.create_pass(pass_data, template, create_for=platforms)
    
    # Generate pass files
    pass_files = manager.generate_pass_files(
        list(response.values())[0].id, template, platforms=platforms
    )
    
    # Save pass files
    os.makedirs(args.output_dir, exist_ok=True)
    
    for platform, pass_file in pass_files.items():
        extension = 'pkpass' if platform == 'apple' else 'json'
        filename = f"{args.output_prefix}_{platform}.{extension}" if args.output_prefix else f"{platform}_{pass_data.serial_number}.{extension}"
        filepath = Path(args.output_dir) / filename
        
        with open(filepath, 'wb') as f:
            f.write(pass_file)
        
        print(f"Pass file for {platform} saved to {filepath}")
    
    # Save response data
    response_data = {
        platform: {
            "id": resp.id,
            "serial_number": resp.serial_number,
            "created_at": resp.created_at.isoformat(),
            "updated_at": resp.updated_at.isoformat(),
        }
        for platform, resp in response.items()
    }
    
    response_file = Path(args.output_dir) / f"{args.output_prefix}_response.json" if args.output_prefix else Path(args.output_dir) / f"response_{pass_data.serial_number}.json"
    with open(response_file, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    print(f"Pass response data saved to {response_file}")


def update_pass_cli(args: argparse.Namespace) -> None:
    """Update an existing wallet pass."""
    # Load configuration
    config = load_config(args.config)
    
    # Create pass manager
    manager = create_pass_manager(config=config)
    
    # Load template
    with open(args.template, 'r') as f:
        template_dict = json.load(f)
        template = PassTemplate.parse_obj(template_dict)
    
    # Load field values if provided
    field_values = {}
    if args.fields:
        with open(args.fields, 'r') as f:
            field_values = json.load(f)
    
    # Create pass data
    pass_data = create_pass_data(
        template_id=template.id,
        customer_id=args.customer_id,
        serial_number=args.serial_number,
        barcode_message=args.barcode,
        barcode_alt_text=args.barcode_alt,
        field_values=field_values
    )
    
    # Determine which platforms to update for
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Update the pass
    response = manager.update_pass(args.pass_id, pass_data, template, update_for=platforms)
    
    # Generate updated pass files
    pass_files = manager.generate_pass_files(
        args.pass_id, template, platforms=platforms
    )
    
    # Save pass files
    os.makedirs(args.output_dir, exist_ok=True)
    
    for platform, pass_file in pass_files.items():
        extension = 'pkpass' if platform == 'apple' else 'json'
        filename = f"{args.output_prefix}_updated_{platform}.{extension}" if args.output_prefix else f"updated_{platform}_{pass_data.serial_number}.{extension}"
        filepath = Path(args.output_dir) / filename
        
        with open(filepath, 'wb') as f:
            f.write(pass_file)
        
        print(f"Updated pass file for {platform} saved to {filepath}")
    
    # Save response data
    response_data = {
        platform: {
            "id": resp.id,
            "serial_number": resp.serial_number,
            "updated_at": resp.updated_at.isoformat(),
        }
        for platform, resp in response.items()
    }
    
    response_file = Path(args.output_dir) / f"{args.output_prefix}_update_response.json" if args.output_prefix else Path(args.output_dir) / f"update_response_{pass_data.serial_number}.json"
    with open(response_file, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    print(f"Pass update response data saved to {response_file}")


def void_pass_cli(args: argparse.Namespace) -> None:
    """Void an existing wallet pass."""
    # Load configuration
    config = load_config(args.config)
    
    # Create pass manager
    manager = create_pass_manager(config=config)
    
    # Load template
    with open(args.template, 'r') as f:
        template_dict = json.load(f)
        template = PassTemplate.parse_obj(template_dict)
    
    # Determine which platforms to void for
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Void the pass
    response = manager.void_pass(args.pass_id, template, void_for=platforms)
    
    print(f"Pass {args.pass_id} voided successfully")


def send_notification_cli(args: argparse.Namespace) -> None:
    """Send a push notification for a pass update."""
    # Load configuration
    config = load_config(args.config)
    
    # Create pass manager
    manager = create_pass_manager(config=config)
    
    # Load template
    with open(args.template, 'r') as f:
        template_dict = json.load(f)
        template = PassTemplate.parse_obj(template_dict)
    
    # Determine which platforms to send notifications for
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Send notifications
    result = manager.send_update_notification(args.pass_id, template, platforms=platforms)
    
    # Display results
    for platform, success in result.items():
        status = "succeeded" if success else "failed"
        print(f"Notification for {platform} {status}")


def main():
    """Run the CLI application."""
    logger.info("""
    [1;36m╔════════════════════════════════════════════════╗[0m
    [1;36m║             [1;33mpy-wallet-pass CLI[0m               [1;36m║[0m
    [1;36m║        [0;37mCreate and manage digital wallet passes[0m     [1;36m║[0m
    [1;36m╚════════════════════════════════════════════════╝[0m
    """)
    parser = argparse.ArgumentParser(description="Wallet Pass SDK Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Template creation command
    template_parser = subparsers.add_parser("create-template", help="Create a new pass template")
    template_parser.add_argument("--config", required=True, help="Path to configuration file")
    template_parser.add_argument("--name", required=True, help="Template name")
    template_parser.add_argument("--organization", required=True, help="Organization ID")
    template_parser.add_argument(
        "--type", required=True, 
        choices=[
            "generic", "coupon", "event", "boarding", "loyalty",
            "google-offer", "google-loyalty", "google-gift", "google-event", "google-flight", "google-transit",
            "samsung-coupon", "samsung-membership", "samsung-ticket", "samsung-boarding", "samsung-voucher"
        ],
        help="Pass type"
    )
    template_parser.add_argument("--description", help="Template description")
    template_parser.add_argument("--output", help="Output file path")
    
    # Pass creation command
    pass_parser = subparsers.add_parser("create-pass", help="Create a new wallet pass")
    pass_parser.add_argument("--config", required=True, help="Path to configuration file")
    pass_parser.add_argument("--template", required=True, help="Path to template file")
    pass_parser.add_argument("--customer-id", required=True, help="Customer ID")
    pass_parser.add_argument("--serial-number", help="Serial number (will be generated if not provided)")
    pass_parser.add_argument("--barcode", help="Barcode message")
    pass_parser.add_argument("--barcode-alt", help="Barcode alternative text")
    pass_parser.add_argument("--fields", help="Path to JSON file with field values")
    pass_parser.add_argument("--platforms", help="Comma-separated list of platforms (apple,google,samsung)")
    pass_parser.add_argument("--output-dir", default=".", help="Output directory for pass files")
    pass_parser.add_argument("--output-prefix", help="Prefix for output filenames")
    
    # Pass update command
    update_parser = subparsers.add_parser("update-pass", help="Update an existing wallet pass")
    update_parser.add_argument("--config", required=True, help="Path to configuration file")
    update_parser.add_argument("--pass-id", required=True, help="Pass ID to update")
    update_parser.add_argument("--template", required=True, help="Path to template file")
    update_parser.add_argument("--customer-id", required=True, help="Customer ID")
    update_parser.add_argument("--serial-number", required=True, help="Serial number")
    update_parser.add_argument("--barcode", help="Updated barcode message")
    update_parser.add_argument("--barcode-alt", help="Updated barcode alternative text")
    update_parser.add_argument("--fields", help="Path to JSON file with updated field values")
    update_parser.add_argument("--platforms", help="Comma-separated list of platforms (apple,google,samsung)")
    update_parser.add_argument("--output-dir", default=".", help="Output directory for updated pass files")
    update_parser.add_argument("--output-prefix", help="Prefix for output filenames")
    
    # Pass voiding command
    void_parser = subparsers.add_parser("void-pass", help="Void an existing wallet pass")
    void_parser.add_argument("--config", required=True, help="Path to configuration file")
    void_parser.add_argument("--pass-id", required=True, help="Pass ID to void")
    void_parser.add_argument("--template", required=True, help="Path to template file")
    void_parser.add_argument("--platforms", help="Comma-separated list of platforms (apple,google,samsung)")
    
    # Send notification command
    notify_parser = subparsers.add_parser("send-notification", help="Send a push notification for a pass update")
    notify_parser.add_argument("--config", required=True, help="Path to configuration file")
    notify_parser.add_argument("--pass-id", required=True, help="Pass ID to send notification for")
    notify_parser.add_argument("--template", required=True, help="Path to template file")
    notify_parser.add_argument("--platforms", help="Comma-separated list of platforms (apple,google,samsung)")
    
    args = parser.parse_args()
    
    # Log the command being executed
    if args.command:
        logger.debug(f"Executing command: {args.command}")
    
    if args.command == "create-template":
        create_template_cli(args)
    elif args.command == "create-pass":
        create_pass_cli(args)
    elif args.command == "update-pass":
        update_pass_cli(args)
    elif args.command == "void-pass":
        void_pass_cli(args)
    elif args.command == "send-notification":
        send_notification_cli(args)
    else:
        logger.info("No command specified, showing help...")
        parser.print_help()


if __name__ == "__main__":
    main()
