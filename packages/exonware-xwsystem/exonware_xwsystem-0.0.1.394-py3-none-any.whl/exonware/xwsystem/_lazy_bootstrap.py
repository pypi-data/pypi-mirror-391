#exonware/xwsystem/src/exonware/xwsystem/_lazy_bootstrap.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.394
Generation Date: 11-Nov-2025

Early bootstrap for lazy mode - installs import hook before any imports occur.

This module runs before any other imports to detect [lazy] extra installation
or environment variable and install the import hook immediately. This ensures
the hook is active before serialization modules are imported, enabling automatic
installation of missing dependencies like PyYAML.

Priority alignment:
- Usability (#2): Zero-config lazy mode with pip install package[lazy]
- Performance (#4): Zero overhead when lazy is disabled
- Maintainability (#3): Clean, minimal bootstrap logic
"""

import os
import sys


def _should_enable_lazy_mode() -> bool:
    """
    Detect if lazy mode should be enabled before package initialization.
    
    Checks:
    1. Environment variable XWSYSTEM_LAZY_INSTALL (set by exonware.conf or user)
    2. [lazy] extra via importlib.metadata
    
    Returns:
        True if lazy mode should be enabled, False otherwise
    """
    # Check environment variable (can be set by exonware.conf before xwsystem import)
    env_var = os.environ.get('XWSYSTEM_LAZY_INSTALL', '').lower()
    if env_var in ('true', '1', 'yes', 'on'):
        return True
    
    # Check [lazy] extra (lightweight check)
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
            
            package_names_to_try = [
                'exonware-xwsystem',
                'xwsystem',
                'exonware.xwsystem'
            ]
            
            for pkg_name in package_names_to_try:
                try:
                    dist = metadata.distribution(pkg_name)
                    if dist.requires:
                        for req in dist.requires:
                            if 'extra == "lazy"' in str(req) or "extra == 'lazy'" in str(req):
                                return True
                except metadata.PackageNotFoundError:
                    continue
    except Exception:
        # Fail silently - detection is best-effort
        pass
    
    return False


# Auto-install hook if lazy mode detected
if _should_enable_lazy_mode():
    try:
        # Lazy import to avoid circular dependency
        # Import here since lazy_package may not be imported yet when bootstrap runs
        from .utils.lazy_package.lazy_core import install_import_hook, is_import_hook_installed
        
        # Only install if not already installed
        if not is_import_hook_installed('xwsystem'):
            install_import_hook('xwsystem')
            # Log at debug level to avoid noise (users can enable debug logging if needed)
            # The hook installation itself logs at info level
    except Exception:
        # Fail silently - package should still load even if hook installation fails
        # This ensures backward compatibility
        pass

