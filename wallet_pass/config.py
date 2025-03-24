from pathlib import Path
from typing import Dict, Optional


class WalletConfig:
    """Configuration for wallet pass generation."""
    
    def __init__(
        self,
        # Apple Wallet settings
        apple_pass_type_identifier: Optional[str] = None,
        apple_team_identifier: Optional[str] = None,
        apple_organization_name: Optional[str] = None,
        apple_certificate_path: Optional[str] = None,
        apple_private_key_path: Optional[str] = None,
        apple_wwdr_certificate_path: Optional[str] = None,
        
        # Google Wallet settings
        google_application_credentials: Optional[str] = None,
        google_issuer_id: Optional[str] = None,
        
        # Samsung Wallet settings
        samsung_issuer_id: Optional[str] = None,
        samsung_api_key: Optional[str] = None,
        samsung_service_id: Optional[str] = None,
        samsung_api_base_url: Optional[str] = None,
        
        # Pass storage
        storage_path: Optional[str] = None,
        
        # Additional settings
        web_service_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize with configuration values."""
        
        # Apple Wallet settings
        self.apple_pass_type_identifier = apple_pass_type_identifier
        self.apple_team_identifier = apple_team_identifier
        self.apple_organization_name = apple_organization_name
        self.apple_certificate_path = Path(apple_certificate_path) if apple_certificate_path else None
        self.apple_private_key_path = Path(apple_private_key_path) if apple_private_key_path else None
        self.apple_wwdr_certificate_path = Path(apple_wwdr_certificate_path) if apple_wwdr_certificate_path else None
        
        # Google Wallet settings
        self.google_application_credentials = Path(google_application_credentials) if google_application_credentials else None
        self.google_issuer_id = google_issuer_id
        
        # Samsung Wallet settings
        self.samsung_issuer_id = samsung_issuer_id
        self.samsung_api_key = samsung_api_key
        self.samsung_service_id = samsung_service_id
        self.samsung_api_base_url = samsung_api_base_url
        
        # Pass storage
        self.storage_path = Path(storage_path) if storage_path else Path("/tmp/py_wallet_pass")
        
        # Additional settings
        self.web_service_url = web_service_url
        
        # Store any additional settings
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, str]) -> "WalletConfig":
        """Create a config instance from a dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_settings(cls, settings) -> "WalletConfig":
        """Create a config instance from a settings object."""
        # Extract relevant settings
        config_dict = {}
        
        # Try to extract settings based on common naming patterns
        for key in dir(settings):
            # Skip private attributes and methods
            if key.startswith("_") or callable(getattr(settings, key)):
                continue
            
            # Check if it's a wallet-related setting
            if any(prefix in key.lower() for prefix in ["apple", "google", "wallet", "pass"]):
                config_dict[key.lower()] = getattr(settings, key)
        
        return cls.from_dict(config_dict)