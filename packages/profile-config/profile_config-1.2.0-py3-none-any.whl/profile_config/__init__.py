"""
Profile Config - Hierarchical profile-based configuration management.

This package provides configuration resolution with:
- Hierarchical directory discovery
- Profile inheritance
- Configurable search patterns
- Multiple file format support
"""

from .discovery import ConfigDiscovery
from .exceptions import (
    CircularInheritanceError,
    ConfigNotFoundError,
    ProfileConfigError,
    ProfileNotFoundError,
)
from .merger import ConfigMerger
from .profiles import ProfileResolver
from .resolver import ProfileConfigResolver

__version__ = "1.2.0"
__all__ = [
    "ProfileConfigResolver",
    "ConfigDiscovery",
    "ProfileResolver",
    "ConfigMerger",
    "ProfileConfigError",
    "ConfigNotFoundError",
    "ProfileNotFoundError",
    "CircularInheritanceError",
]
