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

# Convenience function to quickly set up a pass manager
def create_pass_manager(config_dict=None, config=None):
    """
    Create a PassManager instance with the given configuration.
    
    Args:
        config_dict: Dictionary containing configuration values
        config: WalletConfig instance
        
    Returns:
        PassManager instance
    """
    if config is None:
        if config_dict is None:
            config_dict = {}
        config = WalletConfig.from_dict(config_dict)
    
    return PassManager(config)