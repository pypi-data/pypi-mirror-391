"""Tests for scanners."""

import pytest
from unittest.mock import Mock, AsyncMock
from bugbountycrawler.scanners.security_headers import SecurityHeadersScanner
from bugbountycrawler.scanners.cors import CORSScanner
from bugbountycrawler.core.config import Settings


class TestSecurityHeadersScanner:
    """Test security headers scanner."""
    
    @pytest.fixture
    def scanner(self):
        """Create scanner instance."""
        settings = Settings()
        return SecurityHeadersScanner(settings)
    
    @pytest.mark.asyncio
    async def test_missing_hsts_header(self, scanner):
        """Test detection of missing HSTS header."""
        # Mock response with missing HSTS header
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value="<html></html>")
        
        # Mock make_request method
        scanner.make_request = AsyncMock(return_value=mock_response)
        
        # Scan URL
        result = await scanner.scan_url("https://example.com")
        
        # Check findings
        assert len(result.findings) > 0
        assert any("Missing Strict-Transport-Security" in finding.title for finding in result.findings)
    
    @pytest.mark.asyncio
    async def test_missing_csp_header(self, scanner):
        """Test detection of missing CSP header."""
        # Mock response with missing CSP header
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value="<html></html>")
        
        # Mock make_request method
        scanner.make_request = AsyncMock(return_value=mock_response)
        
        # Scan URL
        result = await scanner.scan_url("https://example.com")
        
        # Check findings
        assert len(result.findings) > 0
        assert any("Missing Content-Security-Policy" in finding.title for finding in result.findings)
    
    @pytest.mark.asyncio
    async def test_insecure_csp_header(self, scanner):
        """Test detection of insecure CSP header."""
        # Mock response with insecure CSP header
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Security-Policy": "default-src 'unsafe-inline' *"
        }
        mock_response.text = AsyncMock(return_value="<html></html>")
        
        # Mock make_request method
        scanner.make_request = AsyncMock(return_value=mock_response)
        
        # Scan URL
        result = await scanner.scan_url("https://example.com")
        
        # Check findings
        assert len(result.findings) > 0
        assert any("Insecure Content-Security-Policy" in finding.title for finding in result.findings)


class TestCORSScanner:
    """Test CORS scanner."""
    
    @pytest.fixture
    def scanner(self):
        """Create scanner instance."""
        settings = Settings()
        return CORSScanner(settings)
    
    @pytest.mark.asyncio
    async def test_wildcard_origin(self, scanner):
        """Test detection of wildcard CORS origin."""
        # Mock response with wildcard CORS origin
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*"
        }
        mock_response.text = AsyncMock(return_value="<html></html>")
        
        # Mock make_request method
        scanner.make_request = AsyncMock(return_value=mock_response)
        
        # Scan URL
        result = await scanner.scan_url("https://example.com")
        
        # Check findings
        assert len(result.findings) > 0
        assert any("CORS Wildcard Origin" in finding.title for finding in result.findings)
    
    @pytest.mark.asyncio
    async def test_credentials_with_wildcard(self, scanner):
        """Test detection of credentials with wildcard origin."""
        # Mock response with credentials and wildcard origin
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
        mock_response.text = AsyncMock(return_value="<html></html>")
        
        # Mock make_request method
        scanner.make_request = AsyncMock(return_value=mock_response)
        
        # Scan URL
        result = await scanner.scan_url("https://example.com")
        
        # Check findings
        assert len(result.findings) > 0
        assert any("CORS Credentials with Wildcard Origin" in finding.title for finding in result.findings)




















