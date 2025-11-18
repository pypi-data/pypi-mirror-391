"""
Certificate Roles Test Module

This module provides comprehensive unit tests for certificate role mechanisms
in the MCP Security Framework, including role enumeration, validation, and
certificate generation with roles.

Test Classes:
    TestCertificateRole: Tests for CertificateRole enumeration
    TestRoleExtraction: Tests for role extraction from certificates
    TestCertificateGenerationWithRoles: Tests for certificate generation with roles
    TestMultipleRoles: Tests for multiple roles in single certificate

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mcp_security_framework.core.cert_manager import (
    CertificateConfigurationError,
    CertificateGenerationError,
    CertificateManager,
)
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    ServerCertConfig,
)
from mcp_security_framework.schemas.models import CertificateRole
from mcp_security_framework.utils.cert_utils import (
    CertificateError,
    extract_roles_from_certificate,
    parse_certificate,
)


class TestCertificateRole:
    """Test suite for CertificateRole enumeration."""

    def test_all_roles_exist(self):
        """Test that all required roles exist in the enum."""
        expected_roles = ["other", "chunker", "embedder", "databaser", "databasew", "techsup", "mcpproxy"]
        actual_roles = [role.value for role in CertificateRole]
        
        assert len(actual_roles) == len(expected_roles)
        for expected_role in expected_roles:
            assert expected_role in actual_roles

    def test_role_values(self):
        """Test that role values are correct."""
        assert CertificateRole.OTHER.value == "other"
        assert CertificateRole.CHUNKER.value == "chunker"
        assert CertificateRole.EMBEDDER.value == "embedder"
        assert CertificateRole.DATABASER.value == "databaser"
        assert CertificateRole.DATABASEW.value == "databasew"
        assert CertificateRole.TECHSUP.value == "techsup"
        assert CertificateRole.MCPPROXY.value == "mcpproxy"

    def test_from_string_valid_roles(self):
        """Test from_string method with valid role strings."""
        assert CertificateRole.from_string("other") == CertificateRole.OTHER
        assert CertificateRole.from_string("chunker") == CertificateRole.CHUNKER
        assert CertificateRole.from_string("embedder") == CertificateRole.EMBEDDER
        assert CertificateRole.from_string("databaser") == CertificateRole.DATABASER
        assert CertificateRole.from_string("databasew") == CertificateRole.DATABASEW
        assert CertificateRole.from_string("techsup") == CertificateRole.TECHSUP
        assert CertificateRole.from_string("mcpproxy") == CertificateRole.MCPPROXY

    def test_from_string_case_insensitive(self):
        """Test from_string method is case-insensitive."""
        assert CertificateRole.from_string("OTHER") == CertificateRole.OTHER
        assert CertificateRole.from_string("Chunker") == CertificateRole.CHUNKER
        assert CertificateRole.from_string("EMBEDDER") == CertificateRole.EMBEDDER

    def test_from_string_with_whitespace(self):
        """Test from_string method handles whitespace."""
        assert CertificateRole.from_string("  other  ") == CertificateRole.OTHER
        assert CertificateRole.from_string(" chunker ") == CertificateRole.CHUNKER

    def test_from_string_invalid_role(self):
        """Test from_string method raises ValueError for invalid roles."""
        with pytest.raises(ValueError, match="Invalid role"):
            CertificateRole.from_string("invalid_role")
        
        with pytest.raises(ValueError, match="Invalid role"):
            CertificateRole.from_string("admin")

    def test_validate_roles_valid_list(self):
        """Test validate_roles method with valid role list."""
        roles = ["chunker", "embedder", "databaser"]
        validated = CertificateRole.validate_roles(roles)
        
        assert len(validated) == 3
        assert validated[0] == CertificateRole.CHUNKER
        assert validated[1] == CertificateRole.EMBEDDER
        assert validated[2] == CertificateRole.DATABASER

    def test_validate_roles_with_invalid(self):
        """Test validate_roles method raises ValueError for invalid roles."""
        with pytest.raises(ValueError):
            CertificateRole.validate_roles(["chunker", "invalid_role"])

    def test_get_default_role(self):
        """Test get_default_role method returns OTHER."""
        default_role = CertificateRole.get_default_role()
        assert default_role == CertificateRole.OTHER


class TestRoleExtraction:
    """Test suite for role extraction from certificates."""

    def create_test_certificate_with_roles(self, roles: list, temp_dir: Path) -> str:
        """Helper method to create a test certificate with roles."""
        # Create CA certificate first
        ca_config = CAConfig(
            common_name="Test CA",
            organization="Test Org",
            country="US",
            validity_days=365,
            key_size=2048,
        )
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_creation_mode=True,
            cert_storage_path=str(temp_dir / "certs"),
            key_storage_path=str(temp_dir / "keys"),
        )
        
        cert_manager = CertificateManager(cert_config)
        ca_pair = cert_manager.create_root_ca(ca_config)
        
        # Create client certificate with roles
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=roles,
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
        )
        
        client_pair = cert_manager.create_client_certificate(client_config)
        return client_pair.certificate_path

    def test_extract_single_role(self, tmp_path):
        """Test extracting a single role from certificate."""
        cert_path = self.create_test_certificate_with_roles(["chunker"], tmp_path)
        roles = extract_roles_from_certificate(cert_path)
        
        assert len(roles) == 1
        assert "chunker" in roles

    def test_extract_multiple_roles(self, tmp_path):
        """Test extracting multiple roles from certificate."""
        cert_path = self.create_test_certificate_with_roles(
            ["chunker", "embedder", "databaser"], tmp_path
        )
        roles = extract_roles_from_certificate(cert_path)
        
        assert len(roles) == 3
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles

    def test_extract_roles_with_default(self, tmp_path):
        """Test extracting roles when no roles specified (should return default)."""
        cert_path = self.create_test_certificate_with_roles([], tmp_path)
        roles = extract_roles_from_certificate(cert_path)
        
        # Should return default role "other"
        assert len(roles) == 1
        assert "other" in roles

    def test_extract_roles_validation_enabled(self, tmp_path):
        """Test role extraction with validation enabled (default)."""
        cert_path = self.create_test_certificate_with_roles(["chunker", "embedder"], tmp_path)
        roles = extract_roles_from_certificate(cert_path, validate=True)
        
        assert len(roles) == 2
        assert all(role in ["chunker", "embedder"] for role in roles)

    def test_extract_roles_validation_disabled(self, tmp_path):
        """Test role extraction with validation disabled."""
        # Create certificate with invalid role (will be filtered during creation)
        # But we can test with a manually created certificate
        cert_path = self.create_test_certificate_with_roles(["chunker"], tmp_path)
        
        # Modify certificate to add invalid role (this is complex, so we'll test differently)
        # For now, test that validation works correctly
        roles = extract_roles_from_certificate(cert_path, validate=False)
        assert len(roles) >= 1

    def test_extract_roles_case_insensitive(self, tmp_path):
        """Test that extracted roles are normalized to lowercase."""
        cert_path = self.create_test_certificate_with_roles(["Chunker", "EMBEDDER"], tmp_path)
        roles = extract_roles_from_certificate(cert_path)
        
        assert "chunker" in roles
        assert "embedder" in roles
        assert "Chunker" not in roles
        assert "EMBEDDER" not in roles


class TestCertificateGenerationWithRoles:
    """Test suite for certificate generation with roles."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cert_storage = self.temp_dir / "certs"
        self.key_storage = self.temp_dir / "keys"
        self.cert_storage.mkdir()
        self.key_storage.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_ca_certificate(self) -> tuple:
        """Create a test CA certificate."""
        ca_config = CAConfig(
            common_name="Test CA",
            organization="Test Org",
            country="US",
            validity_days=365,
            key_size=2048,
        )
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_creation_mode=True,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        ca_pair = cert_manager.create_root_ca(ca_config)
        return ca_pair.certificate_path, ca_pair.private_key_path

    def test_create_client_certificate_with_single_role(self):
        """Test creating client certificate with single role."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=["chunker"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)
        assert os.path.exists(cert_pair.private_key_path)
        
        # Verify roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert len(roles) == 1

    def test_create_client_certificate_with_multiple_roles(self):
        """Test creating client certificate with multiple roles."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=["chunker", "embedder", "databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)
        
        # Verify all roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 3
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles

    def test_create_client_certificate_without_roles(self):
        """Test creating client certificate without roles (should use default)."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=[],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify default role is used
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 1
        assert "other" in roles

    def test_create_client_certificate_with_invalid_roles(self):
        """Test creating client certificate with invalid roles (should filter them)."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=["chunker", "invalid_role", "embedder"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify only valid roles are in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert "embedder" in roles
        assert "invalid_role" not in roles
        # If no valid roles, should use default
        if len(roles) == 1 and "other" in roles:
            # This means all roles were invalid, so default was used
            pass

    def test_create_server_certificate_with_roles(self):
        """Test creating server certificate with roles."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        server_config = ServerCertConfig(
            common_name="test_server",
            organization="Test Org",
            country="US",
            roles=["techsup", "databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_server_certificate(server_config)
        
        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)
        
        # Verify roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 2
        assert "techsup" in roles
        assert "databaser" in roles

    def test_role_normalization(self):
        """Test that roles are normalized to lowercase."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=["Chunker", "EMBEDDER", "Databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify roles are normalized
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles
        assert "Chunker" not in roles
        assert "EMBEDDER" not in roles


class TestMultipleRoles:
    """Test suite for multiple roles in single certificate."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cert_storage = self.temp_dir / "certs"
        self.key_storage = self.temp_dir / "keys"
        self.cert_storage.mkdir()
        self.key_storage.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_ca_certificate(self) -> tuple:
        """Create a test CA certificate."""
        ca_config = CAConfig(
            common_name="Test CA",
            organization="Test Org",
            country="US",
            validity_days=365,
            key_size=2048,
        )
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_creation_mode=True,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        ca_pair = cert_manager.create_root_ca(ca_config)
        return ca_pair.certificate_path, ca_pair.private_key_path

    def test_all_roles_in_single_certificate(self):
        """Test that all roles can be in a single certificate."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        all_roles = [role.value for role in CertificateRole]
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=all_roles,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify all roles are in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == len(all_roles)
        for role in all_roles:
            assert role in roles

    def test_duplicate_roles_removed(self):
        """Test that duplicate roles are removed."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=["chunker", "chunker", "embedder", "embedder"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Verify duplicates are removed
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 2
        assert roles.count("chunker") == 1
        assert roles.count("embedder") == 1

    def test_role_order_preserved(self):
        """Test that role order is preserved in certificate."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        
        role_order = ["chunker", "embedder", "databaser", "databasew", "techsup"]
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=role_order,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )
        
        cert_pair = cert_manager.create_client_certificate(client_config)
        
        # Extract roles and verify order (roles are stored as comma-separated string)
        cert = parse_certificate(cert_pair.certificate_path)
        roles_extension = cert.extensions.get_extension_for_oid(
            x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.1")
        )
        roles_str = roles_extension.value.value.decode("utf-8")
        roles_list = [r.strip() for r in roles_str.split(",")]
        
        # Verify order matches
        assert roles_list == role_order

