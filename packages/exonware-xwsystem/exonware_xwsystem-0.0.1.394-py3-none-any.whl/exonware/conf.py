#exonware/conf.py
"""
Public-facing configuration for all exonware packages.

This module is self-contained and can be imported without triggering
any library initialization. It provides lazy mode configuration that
works across all exonware packages (xwsystem, xwnode, xwdata, etc.).

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.394
Generation Date: 11-Nov-2025
"""

from __future__ import annotations

import sys
import types
from typing import Dict, Optional, Any


class _PackageConfig:
    """Per-package configuration wrapper."""
    
    def __init__(self, package_name: str, parent_conf):
        self._package_name = package_name
        self._parent_conf = parent_conf
        self._lazy_config = None
    
    @property
    def lazy_install(self) -> bool:
        """Get lazy install status for this package."""
        return self._get_lazy_config().lazy_import
    
    @lazy_install.setter
    def lazy_install(self, value: bool) -> None:
        """Set lazy install for this package."""
        self._get_lazy_config().lazy_import = value
    
    def lazy_install_status(self) -> dict:
        """Get detailed lazy install status for this package."""
        return self._get_lazy_config().get_lazy_status()
    
    def is_lazy_active(self) -> bool:
        """Check if lazy mode is active for this package."""
        return self._get_lazy_config().is_lazy_active()
    
    def _get_lazy_config(self):
        """Lazy import LazyConfig from xwsystem when needed."""
        if self._lazy_config is None:
            try:
                # Try to import - if xwsystem is already loaded, use it
                import importlib
                config_module = importlib.import_module('exonware.xwsystem.utils.lazy_package.config')
                LazyConfig = config_module.LazyConfig
                self._lazy_config = LazyConfig(packages=(self._package_name,))
            except (ImportError, AttributeError):
                # Fallback config that uses environment variables for early hook installation
                class _StandaloneConfig:
                    def __init__(self, pkg, parent):
                        self._pkg = pkg
                        self._parent = parent
                        import os
                        # Check environment variable for initial state
                        env_var = f"{pkg.upper()}_LAZY_INSTALL"
                        self._enabled = os.environ.get(env_var, '').lower() in ('true', '1', 'yes', 'on')
                    
                    @property
                    def lazy_import(self):
                        return self._enabled
                    
                    @lazy_import.setter
                    def lazy_import(self, value):
                        import os
                        self._enabled = value
                        # Set environment variable so bootstrap can read it
                        env_var = f"{self._pkg.upper()}_LAZY_INSTALL"
                        if value:
                            os.environ[env_var] = '1'
                            # Try to install hook if xwsystem is available
                            self._parent._try_install_hook(self._pkg)
                        else:
                            os.environ.pop(env_var, None)
                    
                    def get_lazy_status(self):
                        # Try to get real status if xwsystem is now available
                        try:
                            import importlib
                            config_module = importlib.import_module('exonware.xwsystem.utils.lazy_package.config')
                            LazyConfig = config_module.LazyConfig
                            real_config = LazyConfig(packages=(self._pkg,))
                            return real_config.get_lazy_status()
                        except (ImportError, AttributeError):
                            return {
                                'enabled': self._enabled,
                                'hook_installed': False,
                                'lazy_install_enabled': False,
                                'active': False,
                                'error': 'xwsystem not available'
                            }
                    
                    def is_lazy_active(self):
                        try:
                            import importlib
                            config_module = importlib.import_module('exonware.xwsystem.utils.lazy_package.config')
                            LazyConfig = config_module.LazyConfig
                            real_config = LazyConfig(packages=(self._pkg,))
                            return real_config.is_lazy_active()
                        except (ImportError, AttributeError):
                            return False
                
                self._lazy_config = _StandaloneConfig(self._package_name, self._parent_conf)
        return self._lazy_config
    
    def _try_install_hook(self, package_name: str):
        """Try to install hook if xwsystem is available."""
        try:
            import importlib
            lazy_core = importlib.import_module('exonware.xwsystem.utils.lazy_package.lazy_core')
            if hasattr(lazy_core, 'install_import_hook'):
                lazy_core.install_import_hook(package_name)
        except (ImportError, AttributeError):
            # xwsystem not available yet - bootstrap will install hook when it loads
            pass


class _ExonwareConfModule(types.ModuleType):
    """
    Configuration module for all exonware packages.
    
    Provides per-package lazy mode configuration without requiring
    any library to be initialized first.
    """
    
    def __init__(self, name, doc=None):
        super().__init__(name, doc)
        self._package_configs: Dict[str, _PackageConfig] = {}
    
    def __getattr__(self, name: str):
        # Per-package config access: conf.xwsystem.lazy_install
        if name in ('xwsystem', 'xwnode', 'xwdata', 'xwschema', 'xwaction', 'xwentity'):
            if name not in self._package_configs:
                self._package_configs[name] = _PackageConfig(name, self)
            return self._package_configs[name]
        
        # Global lazy_install (defaults to xwsystem for backward compatibility)
        if name == "lazy_install":
            return self.xwsystem.lazy_install
        elif name == "lazy_install_status":
            return self.xwsystem.lazy_install_status
        elif name == "is_lazy_active":
            return self.xwsystem.is_lazy_active
        
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    def __setattr__(self, name: str, value) -> None:
        # Internal attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Global lazy_install (defaults to xwsystem)
        if name == "lazy_install":
            self.xwsystem.lazy_install = value
        else:
            super().__setattr__(name, value)


# Replace module with custom class instance
_module_instance = _ExonwareConfModule(__name__, __doc__)
sys.modules[__name__] = _module_instance

