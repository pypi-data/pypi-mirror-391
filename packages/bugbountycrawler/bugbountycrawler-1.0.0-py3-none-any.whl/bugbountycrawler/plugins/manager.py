"""
Plugin Manager for BugBountyCrawler
Handles plugin loading, registration, and execution
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import json
import logging

from .base import BasePlugin, PluginResult, PluginStatus
from .sandbox import PluginSandbox, SecurityMonitor

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugins for BugBountyCrawler."""
    
    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = Path(plugin_directory)
        self.plugins: Dict[str, Type[BasePlugin]] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.sandbox = PluginSandbox()
        self.security_monitor = SecurityMonitor()
        
        # Plugin allowlist/denylist
        self.allowlist: List[str] = []
        self.denylist: List[str] = []
        
        # Load plugins on initialization
        self.load_plugins()
    
    def load_plugins(self) -> None:
        """Load all plugins from the plugin directory."""
        if not self.plugin_directory.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_directory}")
            return
        
        for plugin_file in self.plugin_directory.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    def _load_plugin_file(self, plugin_file: Path) -> None:
        """Load a single plugin file."""
        module_name = plugin_file.stem
        
        # Add plugin directory to Python path
        if str(self.plugin_directory.parent) not in sys.path:
            sys.path.insert(0, str(self.plugin_directory.parent))
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    
                    plugin_name = obj.__name__
                    
                    # Check allowlist/denylist
                    if self.denylist and plugin_name in self.denylist:
                        logger.info(f"Plugin {plugin_name} is in denylist, skipping")
                        continue
                    
                    if self.allowlist and plugin_name not in self.allowlist:
                        logger.info(f"Plugin {plugin_name} not in allowlist, skipping")
                        continue
                    
                    # Register plugin
                    self.plugins[plugin_name] = obj
                    logger.info(f"Loaded plugin: {plugin_name}")
                    
        except Exception as e:
            logger.error(f"Failed to load plugin file {plugin_file}: {e}")
    
    def register_plugin(self, plugin_class: Type[BasePlugin], config: Dict[str, Any] = None) -> bool:
        """Register a plugin class."""
        try:
            plugin_name = plugin_class.__name__
            
            # Check allowlist/denylist
            if self.denylist and plugin_name in self.denylist:
                logger.warning(f"Plugin {plugin_name} is in denylist")
                return False
            
            if self.allowlist and plugin_name not in self.allowlist:
                logger.warning(f"Plugin {plugin_name} not in allowlist")
                return False
            
            self.plugins[plugin_name] = plugin_class
            self.plugin_configs[plugin_name] = config or {}
            logger.info(f"Registered plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin."""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_configs:
                del self.plugin_configs[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Type[BasePlugin]]:
        """Get a plugin class by name."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins."""
        plugins_info = []
        for name, plugin_class in self.plugins.items():
            try:
                # Create instance to get info
                instance = plugin_class(self.plugin_configs.get(name, {}))
                plugins_info.append(instance.get_info())
            except Exception as e:
                logger.error(f"Failed to get info for plugin {name}: {e}")
                plugins_info.append({
                    'name': name,
                    'error': str(e)
                })
        return plugins_info
    
    async def execute_plugin(self, plugin_name: str, target: str, context: Dict[str, Any] = None) -> PluginResult:
        """Execute a plugin."""
        plugin_class = self.get_plugin(plugin_name)
        if not plugin_class:
            return PluginResult(
                plugin_name=plugin_name,
                status=PluginStatus.FAILED,
                findings=[],
                metadata={},
                error_message=f"Plugin not found: {plugin_name}"
            )
        
        try:
            # Create plugin instance
            config = self.plugin_configs.get(plugin_name, {})
            plugin_instance = plugin_class(config)
            
            # Execute in sandbox
            async with self.sandbox.execute_plugin(plugin_instance, target, context) as result:
                return result
                
        except Exception as e:
            logger.error(f"Failed to execute plugin {plugin_name}: {e}")
            return PluginResult(
                plugin_name=plugin_name,
                status=PluginStatus.FAILED,
                findings=[],
                metadata={},
                error_message=str(e)
            )
    
    async def execute_all_plugins(self, target: str, context: Dict[str, Any] = None) -> List[PluginResult]:
        """Execute all registered plugins."""
        results = []
        
        for plugin_name in self.plugins:
            try:
                result = await self.execute_plugin(plugin_name, target, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute plugin {plugin_name}: {e}")
                results.append(PluginResult(
                    plugin_name=plugin_name,
                    status=PluginStatus.FAILED,
                    findings=[],
                    metadata={},
                    error_message=str(e)
                ))
        
        return results
    
    def set_allowlist(self, plugin_names: List[str]) -> None:
        """Set plugin allowlist."""
        self.allowlist = plugin_names
        logger.info(f"Set plugin allowlist: {plugin_names}")
    
    def set_denylist(self, plugin_names: List[str]) -> None:
        """Set plugin denylist."""
        self.denylist = plugin_names
        logger.info(f"Set plugin denylist: {plugin_names}")
    
    def get_security_violations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get security violations from the security monitor."""
        return {
            'violations': self.security_monitor.get_violations(),
            'blocked_operations': self.security_monitor.get_blocked_operations()
        }
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics."""
        return self.sandbox.get_sandbox_stats()
    
    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Save plugin configuration."""
        try:
            self.plugin_configs[plugin_name] = config
            
            # Save to file
            config_file = self.plugin_directory / f"{plugin_name}_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved config for plugin {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config for plugin {plugin_name}: {e}")
            return False
    
    def load_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Load plugin configuration."""
        try:
            config_file = self.plugin_directory / f"{plugin_name}_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.plugin_configs[plugin_name] = config
                return config
        except Exception as e:
            logger.error(f"Failed to load config for plugin {plugin_name}: {e}")
        
        return None
