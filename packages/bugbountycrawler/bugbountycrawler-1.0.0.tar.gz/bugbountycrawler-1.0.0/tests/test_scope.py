"""Tests for scope validation."""

import pytest
from bugbountycrawler.core.scope import ScopeValidator, ScopeConfig, create_scope_validator


class TestScopeValidator:
    """Test scope validator functionality."""
    
    def test_domain_scope_validation(self):
        """Test domain scope validation."""
        scope_config = ScopeConfig(
            program_name="Test Program",
            domains=["example.com", "*.test.com"],
            exclusions=["admin.example.com"]
        )
        
        validator = ScopeValidator(scope_config)
        
        # Valid domains
        assert validator.is_in_scope("https://example.com")
        assert validator.is_in_scope("https://www.example.com")
        assert validator.is_in_scope("https://api.test.com")
        assert validator.is_in_scope("https://subdomain.test.com")
        
        # Invalid domains
        assert not validator.is_in_scope("https://other.com")
        assert not validator.is_in_scope("https://admin.example.com")  # Excluded
    
    def test_url_pattern_validation(self):
        """Test URL pattern validation."""
        scope_config = ScopeConfig(
            program_name="Test Program",
            urls=["https://example.com/api/*", "https://test.com/user/*"]
        )
        
        validator = ScopeValidator(scope_config)
        
        # Valid URLs
        assert validator.is_in_scope("https://example.com/api/users")
        assert validator.is_in_scope("https://example.com/api/v1/data")
        assert validator.is_in_scope("https://test.com/user/profile")
        
        # Invalid URLs
        assert not validator.is_in_scope("https://example.com/admin")
        assert not validator.is_in_scope("https://other.com/api")
    
    def test_ip_range_validation(self):
        """Test IP range validation."""
        scope_config = ScopeConfig(
            program_name="Test Program",
            ips=["192.168.1.0/24", "10.0.0.0/8"]
        )
        
        validator = ScopeValidator(scope_config)
        
        # Valid IPs
        assert validator.is_in_scope("https://192.168.1.100")
        assert validator.is_in_scope("https://10.0.0.1")
        
        # Invalid IPs
        assert not validator.is_in_scope("https://172.16.0.1")
        assert not validator.is_in_scope("https://8.8.8.8")
    
    def test_exclusion_validation(self):
        """Test exclusion validation."""
        scope_config = ScopeConfig(
            program_name="Test Program",
            domains=["example.com"],
            exclusions=["admin.example.com", "*.staging.example.com"]
        )
        
        validator = ScopeValidator(scope_config)
        
        # Valid domains
        assert validator.is_in_scope("https://example.com")
        assert validator.is_in_scope("https://api.example.com")
        
        # Excluded domains
        assert not validator.is_in_scope("https://admin.example.com")
        assert not validator.is_in_scope("https://test.staging.example.com")
    
    def test_scope_file_loading(self):
        """Test loading scope from file."""
        # This would test loading from YAML/JSON files
        # For now, just test the function exists
        assert callable(create_scope_validator)
    
    def test_scope_validation_issues(self):
        """Test scope validation issues detection."""
        scope_config = ScopeConfig(
            program_name="Test Program",
            domains=[],  # Empty scope
            exclusions=[".*"]  # Excludes everything
        )
        
        validator = ScopeValidator(scope_config)
        issues = validator.validate_scope_file()
        
        assert len(issues) > 0
        assert "No domains, IPs, or URLs defined in scope" in issues
        assert "Exclusion rule" in issues[1]  # Should detect wildcard exclusion




















