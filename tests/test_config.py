"""Tests for the WalletConfig class."""

import os
import tempfile
from pathlib import Path

import pytest

from py_wallet_pass.config import WalletConfig


def test_wallet_config_init():
    """Test WalletConfig initialization with direct parameters."""
    config = WalletConfig(
        apple_pass_type_identifier="pass.com.example.test",
        apple_team_identifier="ABCDE12345",
        apple_organization_name="Test Organization",
        apple_certificate_path="/path/to/cert.pem",
        apple_private_key_path="/path/to/key.pem",
        apple_wwdr_certificate_path="/path/to/wwdr.pem",
        google_application_credentials="/path/to/google_creds.json",
        google_issuer_id="1234567890",
        samsung_issuer_id="samsung-issuer-123",
        samsung_api_key="samsung-api-key",
        samsung_service_id="samsung-service-id",
        storage_path="/path/to/storage",
        web_service_url="https://example.com/wallet"
    )
    
    # Check Apple settings
    assert config.apple_pass_type_identifier == "pass.com.example.test"
    assert config.apple_team_identifier == "ABCDE12345"
    assert config.apple_organization_name == "Test Organization"
    assert config.apple_certificate_path == Path("/path/to/cert.pem")
    assert config.apple_private_key_path == Path("/path/to/key.pem")
    assert config.apple_wwdr_certificate_path == Path("/path/to/wwdr.pem")