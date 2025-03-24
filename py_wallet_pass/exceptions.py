"""Custom exceptions for the py-wallet-pass."""

class PyWalletPassError(Exception):
    """Base exception for all SDK-related errors."""
    pass


class ConfigurationError(PyWalletPassError):
    """Raised when there's an issue with the SDK configuration."""
    pass


class PassCreationError(PyWalletPassError):
    """Raised when pass creation fails."""
    pass


class TemplateError(PyWalletPassError):
    """Raised when there's an issue with a pass template."""
    pass


class CertificateError(PyWalletPassError):
    """Raised when there's an issue with a certificate."""
    pass


class GoogleWalletError(PyWalletPassError):
    """Raised when a Google Wallet operation fails."""
    pass


class AppleWalletError(PyWalletPassError):
    """Raised when an Apple Wallet operation fails."""
    pass


class SamsungWalletError(PyWalletPassError):
    """Raised when a Samsung Wallet operation fails."""
    pass


class ValidationError(PyWalletPassError):
    """Raised when validation fails."""
    pass