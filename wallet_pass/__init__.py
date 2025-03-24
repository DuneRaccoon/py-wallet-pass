"""
py-wallet-pass: SDK for easily creating/managing Apple and Google wallet passes.

This package provides a simple API for creating and managing digital wallet passes
for both Apple Wallet and Google Wallet platforms.
"""

import sys
from pathlib import Path

__version__ = "0.1.0"

# Import the logging configuration first
from .logging import get_logger, with_context

logger = get_logger(__name__)

from .config import WalletConfig
from .exceptions import (
    PyWalletPassError, 
    ConfigurationError, 
    PassCreationError,
    TemplateError, 
    CertificateError, 
    GoogleWalletError, 
    AppleWalletError, 
    SamsungWalletError,
    ValidationError
)
from .schema.core import (
    PassType, 
    Barcode, 
    Location, 
    PassField, 
    PassStructure, 
    PassStyle, 
    PassImages, 
    NFC, 
    PassTemplate, 
    PassData, 
    PassResponse
)
from .providers.manager import PassManager
from .utils import (
    create_template,
    add_field_to_template,
    create_pass_data,
    create_location,
    create_barcode,
    create_event_pass_template,
    create_coupon_pass_template,
    create_loyalty_pass_template,
    create_boarding_pass_template
)
from .storage import StorageBackend, FileSystemStorage, MemoryStorage, create_storage_backend

# Convenience function to quickly set up a pass manager
def create_pass_manager(config_dict=None, config=None, storage=None, storage_path=None):
    """
    Create a PassManager instance with the given configuration.
    
    This function is the main entry point for creating a PassManager that can handle 
    passes for multiple wallet platforms. It automatically initializes the appropriate
    pass providers based on the configuration provided.
    
    Args:
        config_dict: Dictionary containing configuration values
        config: WalletConfig instance (takes precedence over config_dict)
        storage: StorageBackend instance (optional custom storage backend)
        storage_path: Path for file storage (used only if storage is None)
        
    Returns:
        PassManager instance configured with the appropriate pass providers
        
    Examples:
        >>> # Create with config dictionary
        >>> manager = create_pass_manager(config_dict={
        ...     'apple_pass_type_identifier': 'pass.com.example.eventticket',
        ...     'apple_team_identifier': 'ABCDE12345',
        ...     'apple_certificate_path': 'path/to/certificate.pem'
        ... })
        >>> 
        >>> # Create with WalletConfig instance
        >>> config = WalletConfig(
        ...     apple_pass_type_identifier='pass.com.example.coupon',
        ...     apple_team_identifier='ABCDE12345'
        ... )
        >>> manager = create_pass_manager(config=config)
    """
    # Create config if none provided
    if config is None:
        if config_dict is None:
            config_dict = {}
            logger.debug("Using empty config dictionary")
        logger.debug("Creating WalletConfig from dictionary")
        config = WalletConfig.from_dict(config_dict)
    
    # Override storage path if provided
    if storage_path is not None:
        config.storage_path = Path(storage_path)
        logger.debug(f"Set custom storage path: {storage_path}")
    
    # Create the PassManager
    logger.info("🛠️ Creating PassManager instance")
    manager = PassManager(config, storage=storage)
    
    # Check if any pass providers were initialized
    has_providers = any([
        manager.apple_pass is not None,
        manager.google_pass is not None,
        manager.samsung_pass is not None
    ])
    
    if has_providers:
        provider_names = []
        if manager.apple_pass is not None:
            provider_names.append("Apple Wallet")
        if manager.google_pass is not None:
            provider_names.append("Google Wallet")
        if manager.samsung_pass is not None:
            provider_names.append("Samsung Wallet")
            
        logger.success(f"✅ PassManager ready with providers: {', '.join(provider_names)}")
    else:
        logger.warning(
            "⚠️ No pass providers were initialized. Check your configuration for at least one "
            "platform (Apple, Google, or Samsung) and ensure required dependencies are installed."
        )
    
    return manager