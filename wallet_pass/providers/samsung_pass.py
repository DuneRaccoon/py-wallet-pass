"""Samsung Wallet pass implementation."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..config import WalletConfig
from ..exceptions import PassCreationError, ValidationError
from ..schema.core import PassData, PassResponse, PassTemplate, PassType, Barcode
from ..storage import StorageBackend, FileSystemStorage
from ..logging import get_logger, with_context
from .base import BasePass

logger = get_logger(__name__)

try:
    import requests
    SAMSUNG_API_AVAILABLE = True
except ImportError:
    logger.warning("Requests library not installed. Install with: pip install requests")
    SAMSUNG_API_AVAILABLE = False


class SamsungWalletError(Exception):
    """Raised when a Samsung Wallet operation fails."""
    pass


class SamsungPass(BasePass):
    """Implementation of Samsung Wallet passes."""
    
    def __init__(self, config: WalletConfig, storage: Optional[StorageBackend] = None):
        """Initialize with configuration."""
        super().__init__(config)
        
        if not SAMSUNG_API_AVAILABLE:
            raise ImportError(
                "Requests library not installed. Install with: pip install requests"
            )
        
        # Initialize storage
        self.storage = storage or FileSystemStorage(config.storage_path)
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize API client
        self._init_client()
    
    def _validate_config(self) -> None:
        """Validate the configuration for Samsung Wallet."""
        required_fields = [
            'samsung_issuer_id',
            'samsung_api_key',
            'samsung_service_id',
            'samsung_api_base_url',
        ]
        
        missing_fields = [field for field in required_fields 
                        if not hasattr(self.config, field) or not getattr(self.config, field)]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required Samsung Wallet configuration fields: {', '.join(missing_fields)}"
            )
    
    def _init_client(self) -> None:
        """Initialize the Samsung Wallet API client."""
        self.api_base_url = getattr(self.config, 'samsung_api_base_url', 
                                  'https://wallet-api.samsung.com/v1')
        self.api_key = getattr(self.config, 'samsung_api_key', '')
        self.issuer_id = getattr(self.config, 'samsung_issuer_id', '')
        self.service_id = getattr(self.config, 'samsung_service_id', '')
        
        # Setup default headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'X-ISSUER-ID': self.issuer_id,
            'X-SERVICE-ID': self.service_id
        }
        
        logger.info("Samsung Wallet API client initialized")
    
    def create_pass(self, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Create a new Samsung Wallet pass."""
        try:
            # Generate the pass payload
            pass_payload = self._generate_pass_payload(pass_data, template)
            
            # Create a pass ID
            pass_id = f"samsung_{self.issuer_id}_{pass_data.serial_number}"
            
            # In a real implementation, we would call the Samsung API here
            # For now, we'll simulate a successful response
            
            # Store the pass payload for later retrieval
            self._store_pass_data(pass_id, pass_payload)
            
            # Generate the pass URL (this would be provided by Samsung in a real implementation)
            pass_url = self._generate_pass_url(pass_id)
            
            # Create and return the pass response
            return PassResponse(
                id=pass_id,
                template_id=template.id,
                customer_id=pass_data.customer_id,
                serial_number=pass_data.serial_number,
                pass_type_identifier=f"samsung.{template.pass_type.value}",
                authentication_token=str(uuid.uuid4()),
                organization_id=template.organization_id,
                voided=pass_data.voided,
                expiration_date=pass_data.expiration_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                # We would typically store Samsung-specific IDs here
            )
        except Exception as e:
            raise PassCreationError(f"Failed to create Samsung pass: {e}")
    
    def update_pass(self, pass_id: str, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Update an existing Samsung Wallet pass."""
        try:
            # Get the existing pass
            existing_pass = self.get_pass(pass_id)
            
            # Generate the updated pass payload
            pass_payload = self._generate_pass_payload(pass_data, template)
            
            # In a real implementation, we would call the Samsung API to update the pass
            
            # Store the updated pass payload
            self._store_pass_data(pass_id, pass_payload)
            
            # Update the response with the latest information
            existing_pass.voided = pass_data.voided
            existing_pass.expiration_date = pass_data.expiration_date
            existing_pass.updated_at = datetime.now()
            
            return existing_pass
        except Exception as e:
            raise PassCreationError(f"Failed to update Samsung pass: {e}")
    
    def get_pass(self, pass_id: str) -> PassResponse:
        """Retrieve a pass by ID."""
        try:
            # In a real implementation, we would call the Samsung API
            # For now, retrieve the stored pass data
            pass_payload = self._retrieve_pass_data(pass_id)
            
            # Extract metadata from the stored payload
            serial_number = pass_payload.get('serialNumber', '')
            customer_id = pass_payload.get('customerId', '')
            template_id = pass_payload.get('templateId', '')
            organization_id = pass_payload.get('organizationId', '')
            voided = pass_payload.get('voided', False)
            
            # Parse dates if available
            created_at = datetime.fromisoformat(pass_payload.get('createdAt', datetime.now().isoformat()))
            updated_at = datetime.fromisoformat(pass_payload.get('updatedAt', datetime.now().isoformat()))
            
            # Create the pass response
            return PassResponse(
                id=pass_id,
                template_id=template_id,
                customer_id=customer_id,
                serial_number=serial_number,
                pass_type_identifier=pass_payload.get('passTypeIdentifier', ''),
                authentication_token=pass_payload.get('authenticationToken', ''),
                organization_id=organization_id,
                voided=voided,
                expiration_date=None,  # Would parse from payload if available
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            raise SamsungWalletError(f"Failed to retrieve Samsung pass: {e}")
    
    def void_pass(self, pass_id: str) -> PassResponse:
        """Mark a pass as void."""
        try:
            # Get the existing pass
            existing_pass = self.get_pass(pass_id)
            
            # Get the stored pass data
            pass_payload = self._retrieve_pass_data(pass_id)
            
            # Update the voided status
            pass_payload['voided'] = True
            pass_payload['updatedAt'] = datetime.now().isoformat()
            
            # Store the updated pass data
            self._store_pass_data(pass_id, pass_payload)
            
            # In a real implementation, we would call the Samsung API to void the pass
            
            # Update the pass response
            existing_pass.voided = True
            existing_pass.updated_at = datetime.now()
            
            return existing_pass
        except Exception as e:
            raise SamsungWalletError(f"Failed to void Samsung pass: {e}")
    
    def generate_pass_file(self, pass_id: str, template: PassTemplate) -> bytes:
        """Generate the Samsung Wallet pass file."""
        try:
            # Retrieve the pass data
            pass_payload = self._retrieve_pass_data(pass_id)
            
            # Convert to JSON bytes
            return json.dumps(pass_payload, indent=2).encode('utf-8')
        except Exception as e:
            raise SamsungWalletError(f"Failed to generate Samsung pass file: {e}")
    
    def send_update_notification(self, pass_id: str) -> bool:
        """Send a push notification for pass updates."""
        try:
            # In a real implementation, we would call the Samsung API to send a notification
            logger.info(f"Samsung Wallet notification (simulated) sent for pass {pass_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Samsung Wallet notification: {e}")
            return False
    
    def _generate_pass_payload(self, pass_data: PassData, template: PassTemplate) -> Dict[str, Any]:
        """Generate the pass payload for Samsung Wallet."""
        # Basic payload structure based on Samsung Wallet API requirements
        payload = {
            "passTypeIdentifier": f"samsung.{template.pass_type.value}",
            "serialNumber": pass_data.serial_number,
            "templateId": template.id,
            "customerId": pass_data.customer_id,
            "organizationId": template.organization_id,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "voided": pass_data.voided,
            
            # Pass visual properties
            "backgroundColor": template.style.background_color or "#FFFFFF",
            "foregroundColor": template.style.foreground_color or "#000000",
            "labelColor": template.style.label_color or "#666666",
            "logoText": template.style.logo_text or template.name,
            
            # Field data organized by section
            "fields": {},
            
            # Images
            "images": {
                "logo": template.images.logo,
                "icon": template.images.icon,
                "thumbnail": template.images.thumbnail,
                "strip": template.images.strip,
                "background": template.images.background
            }
        }
        
        # Add barcode if provided
        if pass_data.barcode_message:
            payload["barcode"] = {
                "format": self._map_barcode_format(template.barcode_format),
                "message": pass_data.barcode_message,
                "altText": pass_data.barcode_alt_text
            }
        
        # Add expiration date if provided
        if pass_data.expiration_date:
            payload["expirationDate"] = pass_data.expiration_date.isoformat()
        
        # Add locations if provided
        if template.locations:
            payload["locations"] = [
                {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "altitude": location.altitude,
                    "relevantText": location.relevant_text
                } for location in template.locations
            ]
        
        # Add fields from the template structure
        self._add_fields_to_payload(payload, template.structure, pass_data)
        
        return payload
    
    def _map_barcode_format(self, format_str: str) -> str:
        """Map our barcode format to Samsung Wallet's format."""
        format_map = {
            "PKBarcodeFormatQR": "QR_CODE",
            "PKBarcodeFormatPDF417": "PDF_417",
            "PKBarcodeFormatAztec": "AZTEC",
            "PKBarcodeFormatCode128": "CODE_128"
        }
        return format_map.get(format_str, "QR_CODE")
    
    def _add_fields_to_payload(self, payload: Dict[str, Any], structure: Any, pass_data: PassData) -> None:
        """Add fields from the template structure to the pass payload."""
        # Organize fields by section
        field_sections = {
            "header": structure.header_fields,
            "primary": structure.primary_fields,
            "secondary": structure.secondary_fields,
            "auxiliary": structure.auxiliary_fields,
            "back": structure.back_fields
        }
        
        # Initialize fields in payload
        payload["fields"] = {section: [] for section in field_sections}
        
        # Add fields from each section
        for section, fields in field_sections.items():
            for field in fields:
                # Get actual value from pass_data or use default from template
                value = pass_data.field_values.get(field.key, field.value)
                
                field_dict = {
                    "key": field.key,
                    "label": field.label,
                    "value": str(value)  # Ensure value is a string
                }
                
                # Add optional field attributes if they exist
                if field.change_message:
                    field_dict["changeMessage"] = field.change_message
                
                if field.text_alignment:
                    field_dict["textAlignment"] = field.text_alignment
                
                payload["fields"][section].append(field_dict)
    
    def _store_pass_data(self, pass_id: str, pass_payload: Dict[str, Any]) -> None:
        """Store the pass data for later retrieval."""
        self.storage.store_pass("samsung", pass_id, pass_payload)
    
    def _retrieve_pass_data(self, pass_id: str) -> Dict[str, Any]:
        """Retrieve stored pass data."""
        try:
            return self.storage.retrieve_pass("samsung", pass_id)
        except Exception as e:
            raise SamsungWalletError(f"Pass not found: {pass_id}")
    
    def _generate_pass_url(self, pass_id: str) -> str:
        """Generate a URL for the Samsung Wallet pass."""
        # In a real implementation, this would be a URL provided by Samsung
        # For now, we'll simulate a URL
        return f"https://wallet.samsung.com/passes/{pass_id}"
