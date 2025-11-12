"""Scope validation and enforcement for BugBountyCrawler."""

import re
import ipaddress
from typing import List, Optional, Set, Union, Dict, Any
from urllib.parse import urlparse, urljoin
from pathlib import Path
import yaml
import json
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


class ScopeRule(BaseModel):
    """A single scope rule."""
    
    type: str = Field(..., description="Rule type: domain, ip, url, path")
    pattern: str = Field(..., description="Pattern to match")
    allowed: bool = Field(default=True, description="Whether this rule allows or denies")
    description: Optional[str] = Field(default=None, description="Rule description")
    
    @validator("type")
    def validate_type(cls, v: str) -> str:
        """Validate rule type."""
        valid_types = ["domain", "ip", "url", "path"]
        if v not in valid_types:
            raise ValueError(f"type must be one of {valid_types}")
        return v


class ScopeConfig(BaseModel):
    """Scope configuration for a bug bounty program."""
    
    program_name: str = Field(..., description="Name of the bug bounty program")
    program_url: Optional[str] = Field(default=None, description="Program URL")
    domains: List[str] = Field(default_factory=list, description="Allowed domains")
    ips: List[str] = Field(default_factory=list, description="Allowed IP ranges")
    urls: List[str] = Field(default_factory=list, description="Allowed URL patterns")
    exclusions: List[str] = Field(default_factory=list, description="Excluded patterns")
    rules: List[ScopeRule] = Field(default_factory=list, description="Custom rules")
    
    # Metadata
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    expires_at: Optional[str] = Field(default=None, description="Expiration timestamp")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    
    @validator("domains", "ips", "urls", "exclusions")
    def validate_patterns(cls, v: List[str]) -> List[str]:
        """Validate and normalize patterns."""
        normalized = []
        for pattern in v:
            if not pattern.strip():
                continue
            normalized.append(pattern.strip().lower())
        return normalized


class ScopeValidator:
    """Validates targets against bug bounty program scope."""
    
    def __init__(self, scope_config: ScopeConfig):
        """Initialize scope validator."""
        self.config = scope_config
        self._compiled_patterns = self._compile_patterns()
        self._allowed_domains = self._build_domain_set()
        self._allowed_ips = self._build_ip_set()
        
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficient matching."""
        patterns = {
            "domains": [],
            "urls": [],
            "exclusions": []
        }
        
        # Compile domain patterns
        for domain in self.config.domains:
            if domain.startswith("*."):
                # Wildcard domain
                pattern = domain[2:].replace(".", r"\.")
                regex = re.compile(f"^.*\\.{pattern}$", re.IGNORECASE)
            else:
                # Exact domain
                pattern = domain.replace(".", r"\.")
                regex = re.compile(f"^{pattern}$", re.IGNORECASE)
            patterns["domains"].append(regex)
        
        # Compile URL patterns
        for url in self.config.urls:
            # Convert URL pattern to regex
            pattern = url.replace("*", ".*").replace("?", "\\?")
            regex = re.compile(pattern, re.IGNORECASE)
            patterns["urls"].append(regex)
        
        # Compile exclusion patterns
        for exclusion in self.config.exclusions:
            pattern = exclusion.replace("*", ".*").replace("?", "\\?")
            regex = re.compile(pattern, re.IGNORECASE)
            patterns["exclusions"].append(regex)
        
        return patterns
    
    def _build_domain_set(self) -> Set[str]:
        """Build set of allowed domains for fast lookup."""
        domains = set()
        for domain in self.config.domains:
            if not domain.startswith("*"):
                domains.add(domain.lower())
        return domains
    
    def _build_ip_set(self) -> Set[ipaddress.IPv4Network]:
        """Build set of allowed IP networks."""
        networks = set()
        for ip_pattern in self.config.ips:
            try:
                if "/" in ip_pattern:
                    # CIDR notation
                    network = ipaddress.IPv4Network(ip_pattern, strict=False)
                else:
                    # Single IP
                    network = ipaddress.IPv4Network(f"{ip_pattern}/32", strict=False)
                networks.add(network)
            except ValueError as e:
                logger.warning(f"Invalid IP pattern: {ip_pattern} - {e}")
        return networks
    
    def is_in_scope(self, target: str) -> bool:
        """
        Check if a target is within scope.
        
        Args:
            target: URL, domain, or IP address to check
            
        Returns:
            True if target is in scope, False otherwise
        """
        try:
            # Parse the target
            parsed = urlparse(target if target.startswith(("http://", "https://")) else f"https://{target}")
            domain = parsed.hostname
            path = parsed.path
            
            if not domain:
                return False
            
            # Check exclusions first
            if self._is_excluded(target, domain, path):
                return False
            
            # Check IP addresses
            if self._is_ip_in_scope(domain):
                return True
            
            # Check domain patterns
            if self._is_domain_in_scope(domain):
                return True
            
            # Check URL patterns
            if self._is_url_in_scope(target):
                return True
            
            # Check custom rules
            if self._matches_custom_rules(target, domain, path):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking scope for {target}: {e}")
            return False
    
    def _is_excluded(self, target: str, domain: str, path: str) -> bool:
        """Check if target matches any exclusion patterns."""
        for pattern in self._compiled_patterns["exclusions"]:
            if pattern.search(target) or pattern.search(domain) or pattern.search(path):
                return True
        return False
    
    def _is_ip_in_scope(self, domain: str) -> bool:
        """Check if domain resolves to an allowed IP."""
        try:
            import socket
            ip = socket.gethostbyname(domain)
            ip_obj = ipaddress.IPv4Address(ip)
            
            for network in self._allowed_ips:
                if ip_obj in network:
                    return True
            return False
        except (socket.gaierror, ipaddress.AddressValueError):
            return False
    
    def _is_domain_in_scope(self, domain: str) -> bool:
        """Check if domain matches allowed patterns."""
        domain_lower = domain.lower()
        
        # Check exact matches
        if domain_lower in self._allowed_domains:
            return True
        
        # Check wildcard patterns
        for pattern in self._compiled_patterns["domains"]:
            if pattern.match(domain_lower):
                return True
        
        return False
    
    def _is_url_in_scope(self, url: str) -> bool:
        """Check if URL matches allowed patterns."""
        for pattern in self._compiled_patterns["urls"]:
            if pattern.search(url):
                return True
        return False
    
    def _matches_custom_rules(self, target: str, domain: str, path: str) -> bool:
        """Check if target matches custom rules."""
        for rule in self.config.rules:
            if rule.type == "domain" and re.search(rule.pattern, domain, re.IGNORECASE):
                return rule.allowed
            elif rule.type == "url" and re.search(rule.pattern, target, re.IGNORECASE):
                return rule.allowed
            elif rule.type == "path" and re.search(rule.pattern, path, re.IGNORECASE):
                return rule.allowed
        return False
    
    def get_scope_summary(self) -> Dict[str, Any]:
        """Get a summary of the scope configuration."""
        return {
            "program_name": self.config.program_name,
            "domains": len(self.config.domains),
            "ips": len(self.config.ips),
            "urls": len(self.config.urls),
            "exclusions": len(self.config.exclusions),
            "rules": len(self.config.rules),
            "expires_at": self.config.expires_at,
        }
    
    def validate_scope_file(self) -> List[str]:
        """Validate the scope configuration and return any issues."""
        issues = []
        
        # Check for empty scope
        if not any([self.config.domains, self.config.ips, self.config.urls]):
            issues.append("No domains, IPs, or URLs defined in scope")
        
        # Check for conflicting rules
        for rule in self.config.rules:
            if not rule.allowed and rule.type in ["domain", "url"]:
                # Check if this exclusion might block everything
                if rule.pattern == ".*":
                    issues.append(f"Exclusion rule '{rule.pattern}' might block all targets")
        
        # Check expiration
        if self.config.expires_at:
            from datetime import datetime, timezone
            try:
                exp_date = datetime.fromisoformat(self.config.expires_at)
                # Make both datetimes timezone-aware for comparison
                if exp_date.tzinfo is None:
                    exp_date = exp_date.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if exp_date < now:
                    issues.append("Scope has expired")
            except ValueError:
                issues.append("Invalid expiration date format")
        
        return issues


def load_scope_from_file(file_path: Union[str, Path]) -> ScopeConfig:
    """Load scope configuration from file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Scope file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        elif file_path.suffix.lower() == '.json':
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return ScopeConfig(**data)


def create_scope_validator(file_path: Union[str, Path]) -> ScopeValidator:
    """Create a scope validator from a file."""
    scope_config = load_scope_from_file(file_path)
    return ScopeValidator(scope_config)
