"""
Certificate Role Serialization Tests Module

This module provides comprehensive tests for serialization and deserialization
of CertificateRole enumeration, including JSON and dictionary formats.

Test Classes:
    TestCertificateRoleJSONSerialization: Tests for JSON serialization
    TestCertificateRoleDictSerialization: Tests for dictionary serialization
    TestCertificateRoleListSerialization: Tests for list serialization
    TestCertificateRoleEdgeCases: Tests for edge cases

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import json
import pytest

from mcp_security_framework.schemas.models import CertificateRole


class TestCertificateRoleJSONSerialization:
    """Test suite for CertificateRole JSON serialization."""

    def test_single_role_to_json(self):
        """Test serializing a single role to JSON."""
        role = CertificateRole.CHUNKER
        json_str = role.to_json()
        
        assert isinstance(json_str, str)
        assert json_str == '"chunker"'
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed == "chunker"

    def test_single_role_from_json(self):
        """Test deserializing a single role from JSON."""
        json_str = '"chunker"'
        role = CertificateRole.from_json(json_str)
        
        assert role == CertificateRole.CHUNKER
        assert role.value == "chunker"

    def test_all_roles_json_roundtrip(self):
        """Test JSON roundtrip for all roles."""
        for role in CertificateRole:
            json_str = role.to_json()
            deserialized = CertificateRole.from_json(json_str)
            assert deserialized == role

    def test_from_json_invalid_role(self):
        """Test deserializing invalid role from JSON."""
        json_str = '"invalid_role"'
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.from_json(json_str)
        
        assert "Invalid role" in str(exc_info.value)

    def test_from_json_invalid_type(self):
        """Test deserializing non-string value from JSON."""
        json_str = '123'
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.from_json(json_str)
        
        assert "Expected string" in str(exc_info.value)

    def test_from_json_invalid_json(self):
        """Test deserializing invalid JSON."""
        json_str = 'invalid json'
        
        with pytest.raises(json.JSONDecodeError):
            CertificateRole.from_json(json_str)


class TestCertificateRoleListJSONSerialization:
    """Test suite for CertificateRole list JSON serialization."""

    def test_roles_list_to_json(self):
        """Test serializing a list of roles to JSON."""
        roles = [CertificateRole.CHUNKER, CertificateRole.EMBEDDER, CertificateRole.DATABASER]
        json_str = CertificateRole.roles_to_json(roles)
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed == ["chunker", "embedder", "databaser"]

    def test_roles_list_from_json(self):
        """Test deserializing a list of roles from JSON."""
        json_str = '["chunker", "embedder", "databaser"]'
        roles = CertificateRole.roles_from_json(json_str)
        
        assert len(roles) == 3
        assert roles[0] == CertificateRole.CHUNKER
        assert roles[1] == CertificateRole.EMBEDDER
        assert roles[2] == CertificateRole.DATABASER

    def test_roles_list_json_roundtrip(self):
        """Test JSON roundtrip for list of roles."""
        original_roles = [
            CertificateRole.CHUNKER,
            CertificateRole.EMBEDDER,
            CertificateRole.DATABASER,
            CertificateRole.DATABASEW,
            CertificateRole.TECHSUP,
            CertificateRole.MCPPROXY,
        ]
        
        json_str = CertificateRole.roles_to_json(original_roles)
        deserialized_roles = CertificateRole.roles_from_json(json_str)
        
        assert deserialized_roles == original_roles

    def test_roles_list_from_json_empty_list(self):
        """Test deserializing empty list from JSON."""
        json_str = '[]'
        roles = CertificateRole.roles_from_json(json_str)
        
        assert roles == []

    def test_roles_list_from_json_invalid_role(self):
        """Test deserializing list with invalid role from JSON."""
        json_str = '["chunker", "invalid_role"]'
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.roles_from_json(json_str)
        
        assert "Invalid role" in str(exc_info.value)

    def test_roles_list_from_json_invalid_type(self):
        """Test deserializing non-array from JSON."""
        json_str = '"chunker"'
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.roles_from_json(json_str)
        
        assert "Expected array" in str(exc_info.value)

    def test_roles_list_from_json_invalid_json(self):
        """Test deserializing invalid JSON."""
        json_str = 'invalid json'
        
        with pytest.raises(json.JSONDecodeError):
            CertificateRole.roles_from_json(json_str)


class TestCertificateRoleDictSerialization:
    """Test suite for CertificateRole dictionary serialization."""

    def test_single_role_to_dict(self):
        """Test serializing a single role to dictionary."""
        role = CertificateRole.CHUNKER
        role_dict = role.to_dict()
        
        assert isinstance(role_dict, dict)
        assert role_dict == {"CHUNKER": "chunker"}

    def test_single_role_from_dict_by_value(self):
        """Test deserializing a single role from dictionary by value."""
        role_dict = {"role": "chunker"}
        role = CertificateRole.from_dict(role_dict)
        
        assert role == CertificateRole.CHUNKER

    def test_single_role_from_dict_by_name(self):
        """Test deserializing a single role from dictionary by name."""
        role_dict = {"CHUNKER": "chunker"}
        role = CertificateRole.from_dict(role_dict)
        
        assert role == CertificateRole.CHUNKER

    def test_all_roles_dict_roundtrip(self):
        """Test dictionary roundtrip for all roles."""
        for role in CertificateRole:
            role_dict = role.to_dict()
            deserialized = CertificateRole.from_dict(role_dict)
            assert deserialized == role

    def test_from_dict_empty_dict(self):
        """Test deserializing from empty dictionary."""
        role_dict = {}
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.from_dict(role_dict)
        
        assert "cannot be empty" in str(exc_info.value)

    def test_from_dict_invalid_type(self):
        """Test deserializing from non-dictionary."""
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.from_dict("not a dict")
        
        assert "Expected dictionary" in str(exc_info.value)

    def test_from_dict_invalid_role(self):
        """Test deserializing invalid role from dictionary."""
        role_dict = {"role": "invalid_role"}
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.from_dict(role_dict)
        
        assert "Could not find valid role" in str(exc_info.value)


class TestCertificateRoleListDictSerialization:
    """Test suite for CertificateRole list dictionary serialization."""

    def test_roles_list_to_dict(self):
        """Test serializing a list of roles to dictionary."""
        roles = [CertificateRole.CHUNKER, CertificateRole.EMBEDDER]
        roles_dict = CertificateRole.roles_to_dict(roles)
        
        assert isinstance(roles_dict, dict)
        assert roles_dict == {"roles": ["chunker", "embedder"]}

    def test_roles_list_from_dict_with_roles_key(self):
        """Test deserializing list of roles from dictionary with 'roles' key."""
        roles_dict = {"roles": ["chunker", "embedder"]}
        roles = CertificateRole.roles_from_dict(roles_dict)
        
        assert len(roles) == 2
        assert roles[0] == CertificateRole.CHUNKER
        assert roles[1] == CertificateRole.EMBEDDER

    def test_roles_list_from_dict_with_other_key(self):
        """Test deserializing list of roles from dictionary with other key."""
        roles_dict = {"role_list": ["chunker", "embedder"]}
        roles = CertificateRole.roles_from_dict(roles_dict)
        
        assert len(roles) == 2
        assert roles[0] == CertificateRole.CHUNKER
        assert roles[1] == CertificateRole.EMBEDDER

    def test_roles_list_from_dict_single_role_string(self):
        """Test deserializing single role string from dictionary."""
        roles_dict = {"role": "chunker"}
        roles = CertificateRole.roles_from_dict(roles_dict)
        
        assert len(roles) == 1
        assert roles[0] == CertificateRole.CHUNKER

    def test_roles_list_dict_roundtrip(self):
        """Test dictionary roundtrip for list of roles."""
        original_roles = [
            CertificateRole.CHUNKER,
            CertificateRole.EMBEDDER,
            CertificateRole.DATABASER,
        ]
        
        roles_dict = CertificateRole.roles_to_dict(original_roles)
        deserialized_roles = CertificateRole.roles_from_dict(roles_dict)
        
        assert deserialized_roles == original_roles

    def test_roles_list_from_dict_empty_list(self):
        """Test deserializing empty list from dictionary."""
        roles_dict = {"roles": []}
        roles = CertificateRole.roles_from_dict(roles_dict)
        
        assert roles == []

    def test_roles_list_from_dict_invalid_type(self):
        """Test deserializing from non-dictionary."""
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.roles_from_dict("not a dict")
        
        assert "Expected dictionary" in str(exc_info.value)

    def test_roles_list_from_dict_invalid_role(self):
        """Test deserializing list with invalid role from dictionary."""
        roles_dict = {"roles": ["chunker", "invalid_role"]}
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.roles_from_dict(roles_dict)
        
        assert "Invalid role" in str(exc_info.value)

    def test_roles_list_from_dict_no_valid_data(self):
        """Test deserializing dictionary without valid role data."""
        roles_dict = {"other_data": 123}
        
        with pytest.raises(ValueError) as exc_info:
            CertificateRole.roles_from_dict(roles_dict)
        
        assert "Could not find valid roles" in str(exc_info.value)


class TestCertificateRoleEdgeCases:
    """Test suite for edge cases in CertificateRole serialization."""

    def test_case_insensitive_json_deserialization(self):
        """Test that JSON deserialization handles case-insensitive role values."""
        # This should work through from_string which is case-insensitive
        json_str = '"CHUNKER"'
        role = CertificateRole.from_json(json_str)
        assert role == CertificateRole.CHUNKER

    def test_case_insensitive_dict_deserialization(self):
        """Test that dict deserialization handles case-insensitive role values."""
        role_dict = {"role": "CHUNKER"}
        role = CertificateRole.from_dict(role_dict)
        assert role == CertificateRole.CHUNKER

    def test_whitespace_handling_json(self):
        """Test that JSON deserialization handles whitespace."""
        json_str = '"  chunker  "'
        role = CertificateRole.from_json(json_str)
        assert role == CertificateRole.CHUNKER

    def test_whitespace_handling_dict(self):
        """Test that dict deserialization handles whitespace."""
        role_dict = {"role": "  chunker  "}
        role = CertificateRole.from_dict(role_dict)
        assert role == CertificateRole.CHUNKER

    def test_multiple_roles_all_formats(self):
        """Test serialization/deserialization of all roles in all formats."""
        all_roles = list(CertificateRole)
        
        # Test JSON
        json_str = CertificateRole.roles_to_json(all_roles)
        json_roles = CertificateRole.roles_from_json(json_str)
        assert json_roles == all_roles
        
        # Test Dict
        roles_dict = CertificateRole.roles_to_dict(all_roles)
        dict_roles = CertificateRole.roles_from_dict(roles_dict)
        assert dict_roles == all_roles

    def test_single_role_all_formats(self):
        """Test serialization/deserialization of single role in all formats."""
        role = CertificateRole.MCPPROXY
        
        # Test JSON
        json_str = role.to_json()
        json_role = CertificateRole.from_json(json_str)
        assert json_role == role
        
        # Test Dict
        role_dict = role.to_dict()
        dict_role = CertificateRole.from_dict(role_dict)
        assert dict_role == role

    def test_mixed_case_roles_list(self):
        """Test handling of mixed case roles in list."""
        json_str = '["Chunker", "EMBEDDER", "databaser"]'
        roles = CertificateRole.roles_from_json(json_str)
        
        assert len(roles) == 3
        assert roles[0] == CertificateRole.CHUNKER
        assert roles[1] == CertificateRole.EMBEDDER
        assert roles[2] == CertificateRole.DATABASER

