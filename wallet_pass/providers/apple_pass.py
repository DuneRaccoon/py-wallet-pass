import base64
import hashlib
import json
import os
import tempfile
import zipfile
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from OpenSSL import crypto

from ..config import WalletConfig
from ..exceptions import AppleWalletError, CertificateError, PassCreationError
from ..schema.core import PassData, PassResponse, PassTemplate, PassType, Barcode
from ..storage import StorageBackend, FileSystemStorage
from ..logging import get_logger, with_context
from .base import BasePass

logger = get_logger(__name__)


class ApplePass(BasePass):
    """Implementation of Apple Wallet passes."""
    
    def __init__(self, config: WalletConfig, storage: Optional[StorageBackend] = None):
        """Initialize with configuration."""
        super().__init__(config)
        
        # Initialize storage
        self.storage = storage or FileSystemStorage(config.storage_path)
        
        # Validate required configuration
        self._validate_config()
        
        # Load certificates
        self._certificate = self._load_certificate()
        self._private_key = self._load_private_key()
        self._wwdr_certificate = self._load_wwdr_certificate()
    
    def _validate_config(self) -> None:
        """Validate the configuration for Apple Wallet."""
        required_fields = [
            'apple_pass_type_identifier',
            'apple_team_identifier',
            'apple_organization_name',
            'apple_certificate_path',
            'apple_private_key_path',
            'apple_wwdr_certificate_path',
        ]
        
        missing_fields = [field for field in required_fields 
                        if not getattr(self.config, field)]
        
        if missing_fields:
            raise CertificateError(
                f"Missing required Apple Wallet configuration fields: {', '.join(missing_fields)}"
            )
        
        # Check if certificate files exist
        for field in ['apple_certificate_path', 'apple_private_key_path', 'apple_wwdr_certificate_path']:
            path = getattr(self.config, field)
            if not path.exists():
                raise CertificateError(f"File not found: {path}")
    
    def _load_certificate(self) -> crypto.X509:
        """Load the Apple Wallet certificate."""
        try:
            with open(self.config.apple_certificate_path, 'rb') as f:
                cert_data = f.read()
            
            return crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        except Exception as e:
            raise CertificateError(f"Failed to load Apple certificate: {e}")
    
    def _load_private_key(self) -> crypto.PKey:
        """Load the Apple Wallet private key."""
        try:
            with open(self.config.apple_private_key_path, 'rb') as f:
                key_data = f.read()
            
            return crypto.load_privatekey(crypto.FILETYPE_PEM, key_data)
        except Exception as e:
            raise CertificateError(f"Failed to load Apple private key: {e}")
    
    def _load_wwdr_certificate(self) -> crypto.X509:
        """Load the Apple WWDR certificate."""
        try:
            with open(self.config.apple_wwdr_certificate_path, 'rb') as f:
                cert_data = f.read()
            
            return crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        except Exception as e:
            raise CertificateError(f"Failed to load Apple WWDR certificate: {e}")
    
    def create_pass(self, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Create a new Apple Wallet pass."""
        try:
            # Generate the pass content
            pass_json = self._generate_pass_json(pass_data, template)
            
            # Create a unique ID for the pass
            pass_id = f"{self.config.apple_pass_type_identifier}.{pass_data.serial_number}"
            
            context = with_context(
                action="create_pass",
                platform="apple", 
                pass_id=pass_id,
                template_id=template.id,
                customer_id=pass_data.customer_id
            )
            
            # Store the pass data for retrieval
            self._store_pass_data(pass_id, pass_json)
            
            # Return the pass response
            response = PassResponse(
                id=pass_id,
                template_id=template.id,
                customer_id=pass_data.customer_id,
                serial_number=pass_data.serial_number,
                pass_type_identifier=self.config.apple_pass_type_identifier,
                authentication_token=self._generate_authentication_token(),
                organization_id=template.organization_id,
                voided=pass_data.voided,
                expiration_date=pass_data.expiration_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                apple_pass_id=pass_id,
                apple_pass_url=self._generate_pass_url(pass_id)
            )
            
            logger.bind(**context).success("🍏 Created new Apple Wallet pass successfully")
            return response
        except Exception as e:
            context = with_context(
                action="create_pass_error",
                platform="apple", 
                customer_id=pass_data.customer_id,
                error=str(e)
            )
            logger.bind(**context).error(f"❌ Failed to create Apple Wallet pass: {e}")
            raise PassCreationError(f"Failed to create Apple pass: {e}")
    
    def update_pass(self, pass_id: str, pass_data: PassData, template: PassTemplate) -> PassResponse:
        """Update an existing Apple Wallet pass."""
        try:
            # Get the existing pass data
            existing_pass = self.get_pass(pass_id)
            
            # Generate the updated pass content
            pass_json = self._generate_pass_json(pass_data, template)
            
            # Store the updated pass data
            self._store_pass_data(pass_id, pass_json)
            
            # Return the updated pass response
            return PassResponse(
                id=pass_id,
                template_id=template.id,
                customer_id=pass_data.customer_id,
                serial_number=pass_data.serial_number,
                pass_type_identifier=self.config.apple_pass_type_identifier,
                authentication_token=existing_pass.authentication_token,
                organization_id=template.organization_id,
                voided=pass_data.voided,
                expiration_date=pass_data.expiration_date,
                created_at=existing_pass.created_at,
                updated_at=datetime.now(),
                apple_pass_id=pass_id,
                apple_pass_url=self._generate_pass_url(pass_id)
            )
        except Exception as e:
            raise PassCreationError(f"Failed to update Apple pass: {e}")
    
    def get_pass(self, pass_id: str) -> PassResponse:
        """Retrieve a pass by ID."""
        try:
            # Retrieve the stored pass data
            pass_json = self._retrieve_pass_data(pass_id)
            
            # Extract metadata
            serial_number = pass_json.get('serialNumber')
            voided = pass_json.get('voided', False)
            
            # Create a pass response
            return PassResponse(
                id=pass_id,
                template_id=pass_json.get('templateId', ''),
                customer_id=pass_json.get('customerId', ''),
                serial_number=serial_number,
                pass_type_identifier=self.config.apple_pass_type_identifier,
                authentication_token=pass_json.get('authenticationToken', ''),
                organization_id=pass_json.get('organizationId', ''),
                voided=voided,
                expiration_date=None,  # Would parse from the JSON if available
                created_at=datetime.fromisoformat(pass_json.get('createdAt', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(pass_json.get('updatedAt', datetime.now().isoformat())),
                apple_pass_id=pass_id,
                apple_pass_url=self._generate_pass_url(pass_id)
            )
        except Exception as e:
            raise AppleWalletError(f"Failed to retrieve Apple pass: {e}")
    
    def void_pass(self, pass_id: str) -> PassResponse:
        """Mark a pass as void."""
        try:
            # Get the existing pass data
            existing_pass = self.get_pass(pass_id)
            
            # Retrieve the stored pass JSON
            pass_json = self._retrieve_pass_data(pass_id)
            
            # Update the voided status
            pass_json['voided'] = True
            
            # Store the updated pass data
            self._store_pass_data(pass_id, pass_json)
            
            # Update the pass response
            existing_pass.voided = True
            existing_pass.updated_at = datetime.now()
            
            return existing_pass
        except Exception as e:
            raise AppleWalletError(f"Failed to void Apple pass: {e}")
    
    def generate_pass_file(self, pass_id: str, template: PassTemplate) -> bytes:
        """Generate an Apple Wallet .pkpass file."""
        try:
            context = with_context(
                action="generate_pass_file",
                platform="apple", 
                pass_id=pass_id,
                template_id=template.id
            )
            logger.bind(**context).debug("📦 Starting pass file generation")
            
            # Retrieve the pass data
            pass_json = self._retrieve_pass_data(pass_id)
            
            # Create a temporary directory for the pass files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                logger.bind(**context).debug(f"Created temporary directory at {temp_dir}")
                
                # Write the pass.json file
                with open(temp_path / 'pass.json', 'w') as f:
                    json.dump(pass_json, f)
                
                # Copy the required images
                self._add_pass_images(temp_path, template)
                
                # Create the manifest file
                manifest = self._create_manifest(temp_path)
                with open(temp_path / 'manifest.json', 'w') as f:
                    json.dump(manifest, f)
                
                # Sign the manifest
                signature = self._sign_manifest(manifest)
                with open(temp_path / 'signature', 'wb') as f:
                    f.write(signature)
                
                logger.bind(**context).debug("Creating .pkpass archive")
                # Create the .pkpass file
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, 'w') as zip_file:
                    for file_path in temp_path.glob('*'):
                        zip_file.write(file_path, arcname=file_path.name)
                
                # Return the .pkpass data
                buffer.seek(0)
                pkpass_data = buffer.read()
                
                logger.bind(**context).success(f"🎉 Successfully generated .pkpass file ({len(pkpass_data)/1024:.1f} KB)")
                return pkpass_data
        except Exception as e:
            context = with_context(action="generate_pass_file_error", platform="apple", pass_id=pass_id, error=str(e))
            logger.bind(**context).error(f"⚠️ Failed to generate Apple Wallet pass file: {e}")
            raise AppleWalletError(f"Failed to generate Apple Wallet pass file: {e}")
    
    def send_update_notification(self, pass_id: str) -> bool:
        """Send a push notification for pass updates.
        
        This method sends a push notification to Apple devices that have installed this pass,
        informing them that the pass has been updated.
        
        Note: This method requires proper APNs integration to function correctly.
        You'll need to set up an APNs certificate or token and configure the connection.
        
        Args:
            pass_id: ID of the pass to send a notification for
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            # Get the pass from storage
            pass_json = self._retrieve_pass_data(pass_id)
            
            # Get the push tokens associated with this pass
            # In a real implementation, these would be stored with the pass
            push_tokens = pass_json.get('pushTokens', [])
            
            if not push_tokens:
                logger.info(f"No push tokens available for pass {pass_id}")
                return True  # No tokens to notify, so technically success
            
            # In a real implementation, you'd set up APNs connection and send notifications
            # Example implementation (requires a proper APNs client):
            #
            # apns_client = APNSClient(
            #     certificate=self.config.apple_push_certificate_path,
            #     private_key=self.config.apple_push_private_key_path,
            #     use_sandbox=self.config.apple_push_use_sandbox
            # )
            # 
            # success = True
            # for token in push_tokens:
            #     try:
            #         response = apns_client.send_notification(
            #             token=token,
            #             payload={"aps": {"alert": {"body": "Your pass has been updated"}}}
            #         )
            #         logger.debug(f"APNs response for token {token}: {response}")
            #     except Exception as token_error:
            #         logger.error(f"Failed to send notification to token {token}: {token_error}")
            #         success = False
            #
            # return success
            
            # For now, log that this functionality requires additional implementation
            logger.warning("Apple push notification not fully implemented. Requires APNs integration.")
            logger.info(f"Would notify {len(push_tokens)} devices for pass {pass_id}")
            
            # Return success status (this is a placeholder)
            return True
        except Exception as e:
            logger.error(f"Failed to send Apple push notification: {e}")
            return False
    
    def _generate_pass_json(self, pass_data: PassData, template: PassTemplate) -> Dict[str, Any]:
        """Generate the pass.json content."""
        # Basic pass structure
        pass_dict = {
            # Standard pass headers
            "formatVersion": 1,
            "passTypeIdentifier": self.config.apple_pass_type_identifier,
            "serialNumber": pass_data.serial_number,
            "teamIdentifier": self.config.apple_team_identifier,
            "organizationName": self.config.apple_organization_name,
            
            # Custom metadata (not used by Apple, but useful for our SDK)
            "templateId": template.id,
            "customerId": pass_data.customer_id,
            "organizationId": template.organization_id,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            
            # Pass visual style
            "description": template.description or f"{template.name} Pass",
            "logoText": template.style.logo_text,
        }
        
        # Add colors if specified
        if template.style.background_color:
            pass_dict["backgroundColor"] = template.style.background_color
        if template.style.foreground_color:
            pass_dict["foregroundColor"] = template.style.foreground_color
        if template.style.label_color:
            pass_dict["labelColor"] = template.style.label_color
        
        # Add expiration if specified
        if pass_data.expiration_date:
            pass_dict["expirationDate"] = pass_data.expiration_date.isoformat()
        
        # Add relevant date if specified
        if pass_data.relevant_date:
            pass_dict["relevantDate"] = pass_data.relevant_date.isoformat()
        
        # Add voided status if specified
        if pass_data.voided:
            pass_dict["voided"] = True
        
        # Add barcode
        if pass_data.barcode_message:
            barcode = {
                "format": template.barcode_format,
                "message": pass_data.barcode_message,
                "messageEncoding": "iso-8859-1"
            }
            if pass_data.barcode_alt_text:
                barcode["altText"] = pass_data.barcode_alt_text
            
            pass_dict["barcodes"] = [barcode]
            # For backward compatibility with older iOS versions
            pass_dict["barcode"] = barcode
        
        # Add authentication token for web service
        if template.authentication_token:
            pass_dict["authenticationToken"] = template.authentication_token
        
        # Add web service URL if specified
        web_service_url = template.web_service_url or self.config.web_service_url
        if web_service_url:
            pass_dict["webServiceURL"] = str(web_service_url)
        
        # Add locations if specified
        if template.locations:
            pass_dict["locations"] = [
                {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "altitude": location.altitude,
                    "relevantText": location.relevant_text
                } for location in template.locations
            ]
        
        # Add NFC if enabled
        if template.nfc_enabled and template.nfc_data:
            pass_dict["nfc"] = {
                "message": template.nfc_data.message,
                "encryptionPublicKey": template.nfc_data.encryption_public_key,
                "requiresAuthentication": template.nfc_data.requires_authentication
            }
        
        # Add the pass style (generic, coupon, eventTicket, etc.)
        pass_type = template.pass_type.value
        if pass_type.startswith("APPLE_"):
            pass_type = pass_type[6:].lower()  # Remove APPLE_ prefix and convert to lowercase
        
        # Add fields for the pass type
        pass_dict[pass_type] = {}
        
        # Add structure fields
        self._add_fields_to_pass(pass_dict[pass_type], "headerFields", template.structure.header_fields, pass_data)
        self._add_fields_to_pass(pass_dict[pass_type], "primaryFields", template.structure.primary_fields, pass_data)
        self._add_fields_to_pass(pass_dict[pass_type], "secondaryFields", template.structure.secondary_fields, pass_data)
        self._add_fields_to_pass(pass_dict[pass_type], "auxiliaryFields", template.structure.auxiliary_fields, pass_data)
        self._add_fields_to_pass(pass_dict[pass_type], "backFields", template.structure.back_fields, pass_data)
        
        return pass_dict
    
    def _add_fields_to_pass(self, pass_dict: Dict[str, Any], field_type: str, fields: List[Any], pass_data: PassData) -> None:
        """Add fields to the pass JSON."""
        if not fields:
            return
        
        pass_dict[field_type] = []
        
        for field in fields:
            # Get the field value - either from the field_values in pass_data or use the default in the template
            value = pass_data.field_values.get(field.key, field.value)
            
            field_dict = {
                "key": field.key,
                "label": field.label,
                "value": value
            }
            
            # Add optional fields if they exist
            if field.change_message:
                field_dict["changeMessage"] = field.change_message
            
            if field.text_alignment:
                field_dict["textAlignment"] = field.text_alignment
            
            if field.date_style:
                field_dict["dateStyle"] = field.date_style
            
            if field.time_style:
                field_dict["timeStyle"] = field.time_style
            
            if field.is_relative:
                field_dict["isRelative"] = field.is_relative
            
            if field.currency_code:
                field_dict["currencyCode"] = field.currency_code
            
            if field.number_format:
                field_dict["numberFormat"] = field.number_format
            
            pass_dict[field_type].append(field_dict)
    
    def _add_pass_images(self, temp_path: Path, template: PassTemplate) -> None:
        """Add images to the pass package.
        
        This method copies image files specified in the template to the temporary pass directory.
        It checks for both normal and @2x (retina) versions of each image.
        
        Args:
            temp_path: Path to the temporary directory for the pass files
            template: Pass template containing image paths
        """
        import shutil
        
        if not template.images:
            logger.warning("No images specified in the template")
            return
        
        # Define the image types to process
        image_types = {
            'logo': template.images.logo,
            'icon': template.images.icon,
            'strip': template.images.strip,
            'background': template.images.background,
            'footer': template.images.footer,
            'thumbnail': template.images.thumbnail
        }
        
        for image_type, image_path in image_types.items():
            if not image_path:
                # Skip images that aren't specified
                continue
            
            # Check if the image file exists
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                if image_type == 'icon':
                    logger.error(f"Required image '{image_type}' not found at {image_path}")
                else:
                    logger.warning(f"Image file not found: {image_path}")
                continue
            
            # Copy the image to the temporary directory with the correct name
            target_path = temp_path / f"{image_type}.png"
            shutil.copy2(image_path_obj, target_path)
            logger.debug(f"Copied {image_path} to {target_path}")
            
            # Check for a @2x version using naming convention
            retina_path = image_path_obj.parent / f"{image_path_obj.stem}@2x{image_path_obj.suffix}"
            if retina_path.exists():
                retina_target_path = temp_path / f"{image_type}@2x.png"
                shutil.copy2(retina_path, retina_target_path)
                logger.debug(f"Copied {retina_path} to {retina_target_path}")
    
    def _create_manifest(self, pass_dir: Path) -> Dict[str, str]:
        """Create the pass manifest with SHA1 hashes of all files."""
        manifest = {}
        
        for file_path in pass_dir.glob('*'):
            # Skip the manifest itself and the signature
            if file_path.name in ('manifest.json', 'signature'):
                continue
            
            # Compute the SHA1 hash of the file
            with open(file_path, 'rb') as f:
                file_data = f.read()
                sha1_hash = hashlib.sha1(file_data).hexdigest()
            
            manifest[file_path.name] = sha1_hash
        
        return manifest
    
    def _sign_manifest(self, manifest: Dict[str, str]) -> bytes:
        """Sign the manifest with the certificate and private key."""
        # Create a PKCS7 signature
        manifest_json = json.dumps(manifest).encode()
        
        # Create the PKCS7 object
        p7 = crypto.PKCS7()
        
        # Set the type to signed
        p7.type_is_signed()
        
        # Set the content
        bio = crypto._new_mem_buf(manifest_json)
        p7.set_content(bio)
        
        # Add the signer certificate and key
        p7.add_signer(self._certificate, self._private_key, crypto.PKCS7_BINARY)
        
        # Add the WWDR certificate
        p7.add_certificate(self._wwdr_certificate)
        
        # Sign the manifest
        p7.sign(None, 0)
        
        # Get the signature
        signature = crypto.PKCS7_to_der(p7)
        
        return signature
    
    def _store_pass_data(self, pass_id: str, pass_json: Dict[str, Any]) -> None:
        """Store the pass data for retrieval."""
        self.storage.store_pass("apple", pass_id, pass_json)
    
    def _retrieve_pass_data(self, pass_id: str) -> Dict[str, Any]:
        """Retrieve stored pass data."""
        try:
            return self.storage.retrieve_pass("apple", pass_id)
        except Exception as e:
            raise AppleWalletError(f"Pass not found: {pass_id}")
    
    def _generate_authentication_token(self) -> str:
        """Generate a random authentication token."""
        token_bytes = os.urandom(16)
        return base64.b64encode(token_bytes).decode('utf-8')
    
    def _generate_pass_url(self, pass_id: str) -> Optional[str]:
        """Generate a URL for downloading the pass."""
        if not self.config.web_service_url:
            return None
        
        # Create a URL for downloading the pass
        return f"{self.config.web_service_url}/passes/{pass_id}"