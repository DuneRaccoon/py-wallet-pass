from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Union

from ..config import WalletConfig
from ..exceptions import PassCreationError
from ..schema.core import PassData, PassResponse, PassTemplate, PassType
from ..storage import StorageBackend, FileSystemStorage
from ..logging import get_logger, with_context

logger = get_logger(__name__)

# Check for optional providers
try:
    from .apple_pass import ApplePass
except ImportError:
    class ApplePass:
        def __init__(self, *args, **kwargs):
            pass
    ApplePass._dummy = True  # Mark as dummy implementation
    logger.debug("⚠️ Apple Wallet provider not available (missing dependencies)")

try:
    from .google_pass import GooglePass
except ImportError:
    class GooglePass:
        def __init__(self, *args, **kwargs):
            pass
    GooglePass._dummy = True  # Mark as dummy implementation
    logger.debug("⚠️ Google Wallet provider not available (missing dependencies)")

try:
    from .samsung_pass import SamsungPass
except ImportError:
    class SamsungPass:
        def __init__(self, *args, **kwargs):
            pass
    SamsungPass._dummy = True  # Mark as dummy implementation
    logger.debug("⚠️ Samsung Wallet provider not available (missing dependencies)")


class PassManager:
    """Manager for handling both Apple and Google wallet passes."""
    
    def __init__(
        self,
        config: WalletConfig,
        apple_pass: Optional["ApplePass"] = None,
        google_pass: Optional["GooglePass"] = None,
        samsung_pass: Optional["SamsungPass"] = None,
        storage: Optional[StorageBackend] = None,
    ):
        """Initialize with pass implementations."""
        self.config = config
        self.apple_pass = apple_pass
        self.google_pass = google_pass
        self.samsung_pass = samsung_pass
        
        # Initialize storage backend if not provided
        self.storage = storage or FileSystemStorage(config.storage_path)
        
        # Initialize pass providers if not provided
        if not self.apple_pass and self._has_apple_config():
            try:
                self.apple_pass = ApplePass(config, storage=self.storage)
                logger.info("💾 Apple Wallet provider initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Apple Pass provider: {e}")
        
        if not self.google_pass and self._has_google_config():
            try:
                self.google_pass = GooglePass(config, storage=self.storage)
                logger.info("💾 Google Wallet provider initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Google Pass provider: {e}")
        
        if not self.samsung_pass and self._has_samsung_config():
            try:
                self.samsung_pass = SamsungPass(config, storage=self.storage)
                logger.info("💾 Samsung Wallet provider initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Samsung Pass provider: {e}")
    
    def _has_apple_config(self) -> bool:
        """Check if Apple Wallet configuration is available."""
        return all([
            self.config.apple_pass_type_identifier,
            self.config.apple_team_identifier,
            self.config.apple_certificate_path,
            self.config.apple_private_key_path,
            self.config.apple_wwdr_certificate_path,
        ])
    
    def _has_google_config(self) -> bool:
        """Check if Google Wallet configuration is available."""
        return all([
            self.config.google_application_credentials,
            self.config.google_issuer_id,
        ])
    
    def _has_samsung_config(self) -> bool:
        """Check if Samsung Wallet configuration is available."""
        required_attrs = ['samsung_issuer_id', 'samsung_api_key', 'samsung_service_id']
        return all(hasattr(self.config, attr) and getattr(self.config, attr) for attr in required_attrs)
    
    def _is_apple_pass_type(self, pass_type: PassType) -> bool:
        """Check if the pass type is for Apple Wallet."""
        return pass_type.name.startswith("APPLE_")
    
    def _is_google_pass_type(self, pass_type: PassType) -> bool:
        """Check if the pass type is for Google Wallet."""
        return pass_type.name.startswith("GOOGLE_")
    
    def _is_samsung_pass_type(self, pass_type: PassType) -> bool:
        """Check if the pass type is for Samsung Wallet."""
        return pass_type.name.startswith("SAMSUNG_")
    
    def create_pass(
        self, pass_data: PassData, template: PassTemplate, create_for: Optional[List[str]] = None
    ) -> Dict[str, PassResponse]:
        """
        Create a pass across multiple wallet platforms.
        
        Args:
            pass_data: Data for the pass
            template: Template to use for the pass
            create_for: List of platforms to create for ("apple", "google", or both)
        
        Returns:
            Dict mapping platform to pass response
        """
        context = with_context(
            action="create_pass",
            template_id=template.id,
            template_name=template.name,
            pass_type=template.pass_type.value,
            customer_id=pass_data.customer_id
        )
        
        if create_for is None:
            create_for = ["apple", "google", "samsung"]
            logger.bind(**context).debug(f"Creating pass for all platforms: {create_for}")
        else:
            logger.bind(**context).debug(f"Creating pass for platforms: {create_for}")
        
        result = {}
        
        # Generate a common serial number if not provided
        if not pass_data.serial_number:
            import uuid
            pass_data.serial_number = str(uuid.uuid4())
            logger.bind(**context).debug(f"Generated serial number: {pass_data.serial_number}")
        
        # Create passes for specified platforms
        if "apple" in create_for and self.apple_pass and self._is_apple_pass_type(template.pass_type):
            try:
                result["apple"] = self.apple_pass.create_pass(pass_data, template)
                logger.bind(**context).info("🍏 Created Apple Wallet pass")
            except Exception as e:
                logger.bind(**context).error(f"❌ Failed to create Apple Wallet pass: {e}")
        
        if "google" in create_for and self.google_pass and self._is_google_pass_type(template.pass_type):
            try:
                result["google"] = self.google_pass.create_pass(pass_data, template)
                logger.bind(**context).info("📱 Created Google Wallet pass")
            except Exception as e:
                logger.bind(**context).error(f"❌ Failed to create Google Wallet pass: {e}")
        
        if "samsung" in create_for and self.samsung_pass and self._is_samsung_pass_type(template.pass_type):
            try:
                result["samsung"] = self.samsung_pass.create_pass(pass_data, template)
                logger.bind(**context).info("📱 Created Samsung Wallet pass")
            except Exception as e:
                logger.bind(**context).error(f"❌ Failed to create Samsung Wallet pass: {e}")
        
        if not result:
            error_msg = "Failed to create passes: No compatible pass platforms available"
            logger.bind(**context).error(f"❌ {error_msg}")
            raise PassCreationError(error_msg)
        
        logger.bind(**context).success(f"🎉 Successfully created passes for {list(result.keys())}")
        return result
    
    def update_pass(
        self, pass_id: str, pass_data: PassData, template: PassTemplate, update_for: Optional[List[str]] = None
    ) -> Dict[str, PassResponse]:
        """
        Update a pass across multiple wallet platforms.
        
        Args:
            pass_id: ID of the pass to update
            pass_data: Updated data for the pass
            template: Template for the pass
            update_for: List of platforms to update ("apple", "google", or both)
        
        Returns:
            Dict mapping platform to pass response
        """
        if update_for is None:
            update_for = ["apple", "google", "samsung"]
        
        result = {}
        
        # Update passes for specified platforms
        if "apple" in update_for and self.apple_pass and self._is_apple_pass_type(template.pass_type):
            try:
                result["apple"] = self.apple_pass.update_pass(pass_id, pass_data, template)
            except Exception as e:
                logger.error(f"Failed to update Apple pass: {e}")
        
        if "google" in update_for and self.google_pass and self._is_google_pass_type(template.pass_type):
            try:
                result["google"] = self.google_pass.update_pass(pass_id, pass_data, template)
            except Exception as e:
                logger.error(f"Failed to update Google pass: {e}")
        
        if "samsung" in update_for and self.samsung_pass and self._is_samsung_pass_type(template.pass_type):
            try:
                result["samsung"] = self.samsung_pass.update_pass(pass_id, pass_data, template)
            except Exception as e:
                logger.error(f"Failed to update Samsung pass: {e}")
        
        if not result:
            raise PassCreationError(
                f"Failed to update pass {pass_id}: No compatible pass platforms available"
            )
        
        return result
    
    def void_pass(
        self, pass_id: str, template: PassTemplate, void_for: Optional[List[str]] = None
    ) -> Dict[str, PassResponse]:
        """
        Mark a pass as void across multiple wallet platforms.
        
        Args:
            pass_id: ID of the pass to void
            template: Template for the pass
            void_for: List of platforms to void for ("apple", "google", or both)
        
        Returns:
            Dict mapping platform to pass response
        """
        if void_for is None:
            void_for = ["apple", "google", "samsung"]
        
        result = {}
        
        # Void passes for specified platforms
        if "apple" in void_for and self.apple_pass and self._is_apple_pass_type(template.pass_type):
            try:
                result["apple"] = self.apple_pass.void_pass(pass_id)
            except Exception as e:
                logger.error(f"Failed to void Apple pass: {e}")
        
        if "google" in void_for and self.google_pass and self._is_google_pass_type(template.pass_type):
            try:
                result["google"] = self.google_pass.void_pass(pass_id)
            except Exception as e:
                logger.error(f"Failed to void Google pass: {e}")
        
        if "samsung" in void_for and self.samsung_pass and self._is_samsung_pass_type(template.pass_type):
            try:
                result["samsung"] = self.samsung_pass.void_pass(pass_id)
            except Exception as e:
                logger.error(f"Failed to void Samsung pass: {e}")
        
        if not result:
            raise PassCreationError(
                f"Failed to void pass {pass_id}: No compatible pass platforms available"
            )
        
        return result
    
    def generate_pass_files(
        self, pass_id: str, template: PassTemplate, platforms: Optional[List[str]] = None
    ) -> Dict[str, bytes]:
        """
        Generate pass files for multiple platforms.
        
        Args:
            pass_id: ID of the pass
            template: Template for the pass
            platforms: List of platforms to generate for ("apple", "google", or both)
        
        Returns:
            Dict mapping platform to pass file bytes
        """
        if platforms is None:
            platforms = ["apple", "google", "samsung"]
        
        result = {}
        
        # Generate pass files for specified platforms
        if "apple" in platforms and self.apple_pass and self._is_apple_pass_type(template.pass_type):
            try:
                result["apple"] = self.apple_pass.generate_pass_file(pass_id, template)
            except Exception as e:
                logger.error(f"Failed to generate Apple pass file: {e}")
        
        if "google" in platforms and self.google_pass and self._is_google_pass_type(template.pass_type):
            try:
                result["google"] = self.google_pass.generate_pass_file(pass_id, template)
            except Exception as e:
                logger.error(f"Failed to generate Google pass file: {e}")
        
        if "samsung" in platforms and self.samsung_pass and self._is_samsung_pass_type(template.pass_type):
            try:
                result["samsung"] = self.samsung_pass.generate_pass_file(pass_id, template)
            except Exception as e:
                logger.error(f"Failed to generate Samsung pass file: {e}")
        
        if not result:
            raise PassCreationError(
                f"Failed to generate pass files for {pass_id}: No compatible pass platforms available"
            )
        
        return result
    
    def send_update_notification(
        self, pass_id: str, template: PassTemplate, platforms: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send update notifications for a pass across multiple platforms.
        
        Args:
            pass_id: ID of the pass
            template: Template for the pass
            platforms: List of platforms to notify ("apple", "google", or both)
        
        Returns:
            Dict mapping platform to success status
        """
        if platforms is None:
            platforms = ["apple", "google", "samsung"]
        
        result = {}
        
        # Send notifications for specified platforms
        if "apple" in platforms and self.apple_pass and self._is_apple_pass_type(template.pass_type):
            try:
                result["apple"] = self.apple_pass.send_update_notification(pass_id)
            except Exception as e:
                logger.error(f"Failed to send Apple pass notification: {e}")
                result["apple"] = False
        
        if "google" in platforms and self.google_pass and self._is_google_pass_type(template.pass_type):
            try:
                result["google"] = self.google_pass.send_update_notification(pass_id)
            except Exception as e:
                logger.error(f"Failed to send Google pass notification: {e}")
                result["google"] = False
        
        if "samsung" in platforms and self.samsung_pass and self._is_samsung_pass_type(template.pass_type):
            try:
                result["samsung"] = self.samsung_pass.send_update_notification(pass_id)
            except Exception as e:
                logger.error(f"Failed to send Samsung pass notification: {e}")
                result["samsung"] = False
        
        return result