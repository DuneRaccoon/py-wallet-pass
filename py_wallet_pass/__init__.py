"""
py-wallet-pass: SDK for easily creating/managing Apple and Google wallet passes.

This package provides a simple API for creating and managing digital wallet passes
for both Apple Wallet and Google Wallet platforms.
"""

__version__ = "0.1.0"

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
from .providers.base import PassManager
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
def create_pass_manager(config_dict=None, config=None, storage=None):
    """
    Create a PassManager instance with the given configuration.
    
    Args:
        config_dict: Dictionary containing configuration values
        config: WalletConfig instance
        storage: StorageBackend instance
        
    Returns:
        PassManager instance
    """
    if config is None:
        if config_dict is None:
            config_dict = {}
        config = WalletConfig.from_dict(config_dict)
    
    return PassManager(config, storage=storage)