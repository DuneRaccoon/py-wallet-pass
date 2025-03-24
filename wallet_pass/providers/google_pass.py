"""Google Wallet pass implementation."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..config import WalletConfig
from ..exceptions import GoogleWalletError, PassCreationError
from ..schema.core import PassData, PassResponse, PassTemplate, PassType, Barcode, PassField
from ..storage import StorageBackend, FileSystemStorage
from ..logging import get_logger, with_context
from .base import BasePass

logger = get_logger(__name__)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    logger.warning("Google API client not installed. Install with: pip install google-api-python-client google-auth")
    GOOGLE_API_AVAILABLE = False


class GooglePass(BasePass):
    """Implementation of Google Wallet passes."""
    
    def __init__(self, config: WalletConfig, storage: Optional[StorageBackend] = None):
        """Initialize with configuration."""
        super().__init__(config)
        
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google API client not installed. Install with: pip install google-api-python-client google-auth"
            )
        
        # Initialize storage
        self.storage = storage or FileSystemStorage(config.storage_path)
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize the Google Wallet API client
        self._init_client()
    
    def _validate_config(self) -> None:
        """Validate the configuration for Google Wallet.
        
        Ensures all required Google Wallet configuration parameters are present
        and valid. Raises GoogleWalletError if configuration is invalid.
        """
        missing_fields = []
        
        if not self.config.google_application_credentials:
            missing_fields.append("google_application_credentials")
        elif not self.config.google_application_credentials.exists():
            raise GoogleWalletError(
                f"Google credentials file not found: {self.config.google_application_credentials}. "
                f"Please provide a valid service account credentials JSON file."
            )
        
        if not self.config.google_issuer_id:
            missing_fields.append("google_issuer_id")
        
        if missing_fields:
            raise GoogleWalletError(
                f"Missing required Google Wallet configuration: {', '.join(missing_fields)}. "
                f"Please provide values for all required fields."
            )
    
    def _init_client(self) -> None:
        """Initialize the Google Wallet API client."""
        try:
            # Set up credentials
            credentials = service_account.Credentials.from_service_account_file(
                str(self.config.google_application_credentials),
                scopes=['https://www.googleapis.com/auth/wallet_object.issuer']
            )
            
            # Build the Google Wallet API client
            self.client = build('walletobjects', 'v1', credentials=credentials)
            
            logger.info("Google Wallet API client initialized successfully")
        except Exception as e:
            raise GoogleWalletError(f"Failed to initialize Google Wallet API client: {e}")
    
    def create_pass(self, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Create a new Google Wallet pass."""
        try:
            # Generate the pass content based on the pass type
            pass_payload = self._generate_pass_payload(pass_data, template)
            
            # Determine the Google Wallet object type
            object_type = self._get_object_type(template.pass_type)
            
            # Create a unique class ID if not specified
            class_id = f"{self.config.google_issuer_id}.{template.id}"
            
            # Create a unique object ID
            object_id = f"{class_id}.{pass_data.serial_number}"
            
            # Check if the class exists, if not create it
            self._ensure_class_exists(class_id, template)
            
            # Create the object
            wallet_object = self.client.walletobjects().genericObject().insert(body=pass_payload).execute()
            
            # Store the pass data for retrieval
            self._store_pass_data(object_id, pass_payload)
            
            # Generate a Google Pay link
            pass_url = self._generate_save_link(object_id)
            
            # Return the pass response
            return PassResponse(
                id=object_id,
                template_id=template.id,
                customer_id=pass_data.customer_id,
                serial_number=pass_data.serial_number,
                pass_type_identifier=object_type,
                authentication_token=str(uuid.uuid4()),  # Google doesn't use this, but we need it for compatibility
                organization_id=template.organization_id,
                voided=pass_data.voided,
                expiration_date=pass_data.expiration_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                google_pass_id=object_id,
                google_pass_url=pass_url
            )
        except Exception as e:
            raise PassCreationError(f"Failed to create Google pass: {e}")
    
    def update_pass(self, pass_id: str, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Update an existing Google Wallet pass."""
        try:
            # Get the existing pass data
            existing_pass = self.get_pass(pass_id)
            
            # Generate the updated pass content
            pass_payload = self._generate_pass_payload(pass_data, template)
            
            # Update the object
            wallet_object = self.client.walletobjects().genericObject().patch(
                resourceId=pass_id,
                body=pass_payload
            ).execute()
            
            # Store the updated pass data
            self._store_pass_data(pass_id, pass_payload)
            
            # Return the updated pass response
            return PassResponse(
                id=pass_id,
                template_id=template.id,
                customer_id=pass_data.customer_id,
                serial_number=pass_data.serial_number,
                pass_type_identifier=self._get_object_type(template.pass_type),
                authentication_token=existing_pass.authentication_token,
                organization_id=template.organization_id,
                voided=pass_data.voided,
                expiration_date=pass_data.expiration_date,
                created_at=existing_pass.created_at,
                updated_at=datetime.now(),
                google_pass_id=pass_id,
                google_pass_url=existing_pass.google_pass_url
            )
        except Exception as e:
            raise PassCreationError(f"Failed to update Google pass: {e}")
    
    def get_pass(self, pass_id: str) -> PassResponse:
        """Retrieve a pass by ID."""
        try:
            # Get the pass object from Google
            wallet_object = self.client.walletobjects().genericObject().get(resourceId=pass_id).execute()
            
            # Extract metadata
            class_id = wallet_object.get('classId', '')
            template_id = class_id.split('.')[-1] if '.' in class_id else ''
            serial_number = wallet_object.get('id', '').split('.')[-1]
            
            # Determine the state
            voided = wallet_object.get('state', '') == 'INACTIVE'
            
            # Create a pass response
            return PassResponse(
                id=pass_id,
                template_id=template_id,
                customer_id=wallet_object.get('customerId', ''),
                serial_number=serial_number,
                pass_type_identifier=wallet_object.get('objectType', ''),
                authentication_token=str(uuid.uuid4()),  # Google doesn't use this, but we need it for compatibility
                organization_id=wallet_object.get('organizationId', ''),
                voided=voided,
                expiration_date=None,  # Would parse from the object if available
                created_at=datetime.now(),  # This information isn't directly available from Google
                updated_at=datetime.now(),
                google_pass_id=pass_id,
                google_pass_url=self._generate_save_link(pass_id)
            )
        except Exception as e:
            raise GoogleWalletError(f"Failed to retrieve Google pass: {e}")
    
    def void_pass(self, pass_id: str) -> PassResponse:
        """Mark a pass as void."""
        try:
            # Get the existing pass
            existing_pass = self.get_pass(pass_id)
            
            # Update the state to inactive
            wallet_object = self.client.walletobjects().genericObject().patch(
                resourceId=pass_id,
                body={'state': 'INACTIVE'}
            ).execute()
            
            # Update the pass response
            existing_pass.voided = True
            existing_pass.updated_at = datetime.now()
            
            return existing_pass
        except Exception as e:
            raise GoogleWalletError(f"Failed to void Google pass: {e}")
    
    def generate_pass_file(self, pass_id: str, template: PassTemplate) -> bytes:
        """Generate a Google Wallet JSON file."""
        try:
            # Retrieve the pass data
            pass_payload = self._retrieve_pass_data(pass_id)
            
            # Convert to JSON string
            pass_json = json.dumps(pass_payload, indent=2)
            
            return pass_json.encode('utf-8')
        except Exception as e:
            raise GoogleWalletError(f"Failed to generate Google pass file: {e}")
    
    def send_update_notification(self, pass_id: str) -> bool:
        """Send a push notification for pass updates."""
        try:
            # Google handles push notifications automatically when you update a pass
            # This method is included for API compatibility
            logger.info(f"Google Wallet handles push notifications automatically for pass {pass_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to handle Google notification: {e}")
            return False
    
    def _generate_pass_payload(self, pass_data: PassData, template: PassTemplate) -> Dict[str, Any]:
        """Generate the pass payload for Google Wallet.
        
        Creates a properly formatted JSON payload for the Google Wallet API based on
        the provided pass data and template.
        
        Args:
            pass_data: The pass data containing values for the pass fields
            template: The pass template defining the structure and style
            
        Returns:
            A dictionary containing the Google Wallet JSON payload
        """
        # Determine the Google Wallet object type
        object_type = self._get_object_type(template.pass_type)
        
        # Create class ID
        class_id = f"{self.config.google_issuer_id}.{template.id}"
        
        # Create object ID
        object_id = f"{class_id}.{pass_data.serial_number}"
        
        # Basic pass structure
        payload = {
            "id": object_id,
            "classId": class_id,
            "state": "INACTIVE" if pass_data.voided else "ACTIVE",
            "heroImage": {
                "sourceUri": {
                    "uri": template.images.strip or template.images.logo or "https://example.com/logo.png"
                }
            },
            "textModulesData": [],
            "linksModuleData": {
                "uris": []
            },
            "imageModulesData": [],
            "barcode": self._create_barcode(pass_data, template),
            "infoModuleData": {
                "hexBackgroundColor": template.style.background_color or "#FFFFFF",
                "showLastUpdateTime": True
            },
            "customerId": pass_data.customer_id,
            # Custom metadata
            "organizationId": template.organization_id
        }
        
        # Add fields from the template structure
        self._add_fields_to_pass(payload, template.structure, pass_data)
        
        # Add locations if specified
        if template.locations:
            payload["locations"] = [
                {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                } for location in template.locations
            ]
        
        # Add expiration if specified
        if pass_data.expiration_date:
            payload["validTimeInterval"] = {
                "end": {
                    "date": pass_data.expiration_date.isoformat()
                }
            }
        
        return payload
    
    def _get_object_type(self, pass_type: PassType) -> str:
        """Convert our pass type to Google Wallet object type."""
        if pass_type == PassType.GOOGLE_OFFER:
            return "offerObject"
        elif pass_type == PassType.GOOGLE_LOYALTY:
            return "loyaltyObject"
        elif pass_type == PassType.GOOGLE_GIFT_CARD:
            return "giftCardObject"
        elif pass_type == PassType.GOOGLE_EVENT_TICKET:
            return "eventTicketObject"
        elif pass_type == PassType.GOOGLE_FLIGHT:
            return "flightObject"
        elif pass_type == PassType.GOOGLE_TRANSIT:
            return "transitObject"
        else:
            # Default to generic object for other types
            return "genericObject"
    
    def _create_barcode(self, pass_data: PassData, template: PassTemplate) -> Dict[str, Any]:
        """Create a barcode object for Google Wallet."""
        barcode_message = pass_data.barcode_message or pass_data.serial_number
        
        # Map Apple barcode format to Google barcode format
        barcode_format = template.barcode_format
        if barcode_format == "PKBarcodeFormatQR":
            google_format = "QR_CODE"
        elif barcode_format == "PKBarcodeFormatPDF417":
            google_format = "PDF_417"
        elif barcode_format == "PKBarcodeFormatAztec":
            google_format = "AZTEC"
        elif barcode_format == "PKBarcodeFormatCode128":
            google_format = "CODE_128"
        else:
            google_format = "QR_CODE"  # Default to QR code
        
        return {
            "type": google_format,
            "value": barcode_message,
            "alternateText": pass_data.barcode_alt_text
        }
    
    def _add_fields_to_pass(self, payload: Dict[str, Any], structure: Any, pass_data: PassData) -> None:
        """Add fields from the template structure to the pass payload.
        
        Takes fields from different sections of the pass structure and adds them
        to the appropriate section in the Google Wallet pass payload.
        
        Args:
            payload: The Google Wallet JSON payload to update
            structure: The pass structure containing field definitions
            pass_data: The pass data containing values for the fields
        """
        # Define field sections to process
        field_sections = {
            "header": structure.header_fields,
            "primary": structure.primary_fields,
            "secondary": structure.secondary_fields,
            "auxiliary": structure.auxiliary_fields,
            "back": structure.back_fields
        }
        
        # Process all field sections
        for section_name, fields in field_sections.items():
            self._add_section_fields_to_payload(payload, fields, pass_data, section_name)
    
    def _add_section_fields_to_payload(
        self, 
        payload: Dict[str, Any], 
        fields: List[PassField], 
        pass_data: PassData,
        section_name: str
    ) -> None:
        """Add fields from a specific section to the pass payload.
        
        Args:
            payload: The Google Wallet JSON payload to update
            fields: List of fields in this section
            pass_data: The pass data containing values for the fields
            section_name: Name of the section (for logging purposes)
        """
        for field in fields:
            # Get value from pass_data or use default from template
            value = pass_data.field_values.get(field.key, field.value)
            
            # Add the field to the text modules section
            payload["textModulesData"].append({
                "id": field.key,
                "header": field.label,
                "body": str(value)
            })
            
            logger.debug(f"Added {section_name} field {field.key} with value {value}")
    
    def _ensure_class_exists(self, class_id: str, template: PassTemplate) -> None:
        """Ensure that the Google Wallet class exists."""
        try:
            # Try to get the class
            self.client.walletobjects().genericClass().get(resourceId=class_id).execute()
            logger.debug(f"Class {class_id} already exists")
        except Exception:
            # Class doesn't exist, create it
            class_payload = self._generate_class_payload(class_id, template)
            self.client.walletobjects().genericClass().insert(body=class_payload).execute()
            logger.info(f"Created class {class_id}")
    
    def _generate_class_payload(self, class_id: str, template: PassTemplate) -> Dict[str, Any]:
        """Generate the class payload for Google Wallet."""
        return {
            "id": class_id,
            "issuerName": self.config.apple_organization_name or "Organization",
            "reviewStatus": "UNDER_REVIEW",
            "hexBackgroundColor": template.style.background_color or "#FFFFFF",
            "homepageUri": {
                "uri": self.config.web_service_url or "https://example.com",
                "description": template.name
            }
        }
    
    def _generate_save_link(self, object_id: str) -> str:
        """Generate a Google Pay Save link for the pass."""
        # The format for a Google Pay save link
        return f"https://pay.google.com/gp/v/save/{object_id}"
    
    def _store_pass_data(self, pass_id: str, pass_json: Dict[str, Any]) -> None:
        """Store the pass data for retrieval."""
        self.storage.store_pass("google", pass_id, pass_json)
    
    def _retrieve_pass_data(self, pass_id: str) -> Dict[str, Any]:
        """Retrieve stored pass data."""
        try:
            return self.storage.retrieve_pass("google", pass_id)
        except Exception as e:
            raise GoogleWalletError(f"Pass not found: {pass_id}")