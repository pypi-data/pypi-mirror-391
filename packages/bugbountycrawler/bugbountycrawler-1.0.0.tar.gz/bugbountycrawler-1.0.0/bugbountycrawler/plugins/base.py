"""
Base plugin class for BugBountyCrawler
Defines the interface for all plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class PluginStatus(Enum):
    """Plugin execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PluginResult:
    """Result of plugin execution."""
    plugin_name: str
    status: PluginStatus
    findings: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0

class PluginError(Exception):
    """Plugin execution error."""
    pass

class BasePlugin(ABC):
    """Base class for all BugBountyCrawler plugins."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "Base plugin"
        self.author = "Unknown"
        self.license = "MIT"
        
        # Plugin capabilities
        self.capabilities = {
            'scanning': False,
            'crawling': False,
            'analysis': False,
            'reporting': False
        }
        
        # Security restrictions
        self.restrictions = {
            'network_access': True,
            'file_system_access': False,
            'process_creation': False,
            'system_commands': False
        }
    
    @abstractmethod
    async def execute(self, target: str, context: Dict[str, Any] = None) -> PluginResult:
        """Execute the plugin with the given target and context."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'license': self.license,
            'capabilities': self.capabilities,
            'restrictions': self.restrictions
        }
    
    def check_permissions(self, required_permissions: List[str]) -> bool:
        """Check if plugin has required permissions."""
        for permission in required_permissions:
            if not self.restrictions.get(permission, False):
                return False
        return True
    
    def sanitize_input(self, input_data: Any) -> Any:
        """Sanitize input data to prevent injection attacks."""
        if isinstance(input_data, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
            for char in dangerous_chars:
                input_data = input_data.replace(char, '')
        elif isinstance(input_data, dict):
            return {k: self.sanitize_input(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        return input_data
