"""Test fixtures for py-wallet-pass."""

import os
import tempfile
from pathlib import Path

import pytest

from py_wallet_pass.config import WalletConfig
from py_wallet_pass.storage import MemoryStorage
from py_wallet_pass.schema.core import PassType, PassTemplate, PassStructure, PassStyle, PassImages


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def config():
    """Create a test configuration."""
    return WalletConfig(
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
        storage_path="/tmp/py_wallet_pass_test",
        web_service_url="https://example.com/wallet"
    )


@pytest.fixture
def memory_storage():
    """Create a test memory storage."""
    return MemoryStorage()


@pytest.fixture
def apple_template():
    """Create a test Apple Wallet template."""
    return PassTemplate(
        id="test-template-apple",
        name="Test Apple Template",
        description="A test Apple template",
        organization_id="test-org",
        pass_type=PassType.APPLE_GENERIC,
        structure=PassStructure(),
        style=PassStyle(
            background_color="#FFFFFF",
            foreground_color="#000000",
            label_color="#999999",
            logo_text="Test Pass"
        ),
        images=PassImages(),
        is_active=True
    )


@pytest.fixture
def google_template():
    """Create a test Google Wallet template."""
    return PassTemplate(
        id="test-template-google",
        name="Test Google Template",
        description="A test Google template",
        organization_id="test-org",
        pass_type=PassType.GOOGLE_OFFER,
        structure=PassStructure(),
        style=PassStyle(
            background_color="#FFFFFF",
            foreground_color="#000000",
            label_color="#999999",
            logo_text="Test Pass"
        ),
        images=PassImages(),
        is_active=True
    )


@pytest.fixture
def samsung_template():
    """Create a test Samsung Wallet template."""
    return PassTemplate(
        id="test-template-samsung",
        name="Test Samsung Template",
        description="A test Samsung template",
        organization_id="test-org",
        pass_type=PassType.SAMSUNG_COUPON,
        structure=PassStructure(),
        style=PassStyle(
            background_color="#FFFFFF",
            foreground_color="#000000",
            label_color="#999999",
            logo_text="Test Pass"
        ),
        images=PassImages(),
        is_active=True
    )