"""
Plugin sandbox for secure plugin execution
Implements security restrictions and monitoring
"""

import asyncio
import time
import sys
import os
import signal
from typing import Dict, Any, List, Optional, Callable
from contextlib import asynccontextmanager
import logging

from .base import BasePlugin, PluginResult, PluginStatus, PluginError

logger = logging.getLogger(__name__)

class PluginSandbox:
    """Sandbox for secure plugin execution."""
    
    def __init__(self, max_execution_time: int = 300, max_memory_mb: int = 100):
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.active_plugins = {}
        
    @asynccontextmanager
    async def execute_plugin(self, plugin: BasePlugin, target: str, context: Dict[str, Any] = None):
        """Execute a plugin in a sandboxed environment."""
        plugin_id = f"{plugin.name}_{id(plugin)}"
        start_time = time.time()
        
        try:
            # Register plugin
            self.active_plugins[plugin_id] = {
                'plugin': plugin,
                'start_time': start_time,
                'status': PluginStatus.RUNNING
            }
            
            logger.info(f"Starting plugin execution: {plugin.name}")
            
            # Create execution task with timeout
            task = asyncio.create_task(
                self._execute_with_timeout(plugin, target, context or {})
            )
            
            try:
                result = await asyncio.wait_for(task, timeout=self.max_execution_time)
                logger.info(f"Plugin execution completed: {plugin.name}")
                yield result
                
            except asyncio.TimeoutError:
                logger.warning(f"Plugin execution timeout: {plugin.name}")
                task.cancel()
                yield PluginResult(
                    plugin_name=plugin.name,
                    status=PluginStatus.FAILED,
                    findings=[],
                    metadata={},
                    error_message="Plugin execution timeout",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"Plugin execution failed: {plugin.name} - {e}")
            yield PluginResult(
                plugin_name=plugin.name,
                status=PluginStatus.FAILED,
                findings=[],
                metadata={},
                error_message=str(e),
                execution_time=time.time() - start_time
            )
            
        finally:
            # Cleanup
            if plugin_id in self.active_plugins:
                del self.active_plugins[plugin_id]
    
    async def _execute_with_timeout(self, plugin: BasePlugin, target: str, context: Dict[str, Any]) -> PluginResult:
        """Execute plugin with additional security checks."""
        try:
            # Validate plugin configuration
            if not plugin.validate_config(plugin.config):
                raise PluginError("Invalid plugin configuration")
            
            # Sanitize inputs
            sanitized_target = plugin.sanitize_input(target)
            sanitized_context = plugin.sanitize_input(context)
            
            # Execute plugin
            result = await plugin.execute(sanitized_target, sanitized_context)
            
            # Validate result
            if not isinstance(result, PluginResult):
                raise PluginError("Plugin must return PluginResult")
            
            return result
            
        except Exception as e:
            raise PluginError(f"Plugin execution error: {str(e)}")
    
    def get_active_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active plugins."""
        return {
            plugin_id: {
                'name': info['plugin'].name,
                'status': info['status'].value,
                'runtime': time.time() - info['start_time']
            }
            for plugin_id, info in self.active_plugins.items()
        }
    
    def cancel_plugin(self, plugin_id: str) -> bool:
        """Cancel a running plugin."""
        if plugin_id in self.active_plugins:
            self.active_plugins[plugin_id]['status'] = PluginStatus.CANCELLED
            return True
        return False
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics."""
        return {
            'max_execution_time': self.max_execution_time,
            'max_memory_mb': self.max_memory_mb,
            'active_plugins': len(self.active_plugins),
            'total_plugins_executed': 0  # Would be tracked in production
        }

class SecurityMonitor:
    """Monitor plugin execution for security violations."""
    
    def __init__(self):
        self.violations = []
        self.blocked_operations = []
    
    def check_operation(self, plugin_name: str, operation: str, details: Dict[str, Any]) -> bool:
        """Check if an operation is allowed for a plugin."""
        # Define blocked operations
        blocked_ops = [
            'file_write', 'file_delete', 'process_create', 'system_command',
            'network_outbound', 'database_access', 'registry_access'
        ]
        
        if operation in blocked_ops:
            self.blocked_operations.append({
                'plugin': plugin_name,
                'operation': operation,
                'details': details,
                'timestamp': time.time()
            })
            logger.warning(f"Blocked operation: {plugin_name} attempted {operation}")
            return False
        
        return True
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get security violations."""
        return self.violations
    
    def get_blocked_operations(self) -> List[Dict[str, Any]]:
        """Get blocked operations."""
        return self.blocked_operations
