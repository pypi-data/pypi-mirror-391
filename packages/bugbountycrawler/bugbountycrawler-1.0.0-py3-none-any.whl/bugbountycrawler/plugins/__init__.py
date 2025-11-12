"""
Plugin system for BugBountyCrawler
Allows for extensible scanner architecture with sandboxing
"""

from .base import BasePlugin, PluginError, PluginResult
from .manager import PluginManager
from .sandbox import PluginSandbox

__all__ = ['BasePlugin', 'PluginError', 'PluginResult', 'PluginManager', 'PluginSandbox']
