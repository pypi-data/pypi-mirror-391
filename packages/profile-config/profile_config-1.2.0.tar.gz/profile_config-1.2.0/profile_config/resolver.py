"""
Main profile configuration resolver.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .discovery import ConfigDiscovery
from .exceptions import ConfigFormatError, ConfigNotFoundError
from .loader import ConfigLoader
from .merger import ConfigMerger
from .profiles import ProfileResolver

logger = logging.getLogger(__name__)

# Type aliases for overrides
OverrideSource = Union[Dict[str, Any], str, Path, os.PathLike]
OverridesType = Optional[Union[OverrideSource, List[OverrideSource]]]


class ProfileConfigResolver:
    """
    Main interface for profile-based configuration resolution.

    Provides a unified interface for discovering configuration files,
    resolving profiles with inheritance, and merging configurations
    with proper precedence handling.
    """

    def __init__(
        self,
        config_name: str,
        profile: str = "default",
        profile_filename: str = "config",
        overrides: OverridesType = None,
        extensions: Optional[List[str]] = None,
        search_home: bool = True,
        inherit_key: str = "inherits",
        enable_interpolation: bool = True,
    ):
        """
        Initialize profile configuration resolver.

        Args:
            config_name: Name of configuration directory (e.g., "myapp")
            profile: Profile name to resolve (default: "default")
            profile_filename: Name of profile file without extension (default: "config")
            overrides: Override values (highest precedence). Can be:
                - Dict[str, Any]: Single override dictionary
                - PathLike: Path to override file (yaml/json/toml)
                - List[Union[Dict, PathLike]]: Multiple overrides applied in order
            extensions: File extensions to search for (default: yaml, yml, json, toml)
            search_home: Whether to search home directory
            inherit_key: Key name used for profile inheritance (default: "inherits")
            enable_interpolation: Whether to enable variable interpolation
        """
        self.config_name = config_name
        self.profile = profile
        self.profile_filename = profile_filename
        self.enable_interpolation = enable_interpolation

        # Initialize components
        self.discovery = ConfigDiscovery(
            config_name=config_name,
            profile_filename=profile_filename,
            extensions=extensions,
            search_home=search_home,
        )
        self.loader = ConfigLoader()
        self.profile_resolver = ProfileResolver(inherit_key=inherit_key)
        self.merger = ConfigMerger()

        # Process overrides into list of dictionaries
        self.override_list = self._process_overrides(overrides)

    def _process_overrides(self, overrides: OverridesType) -> List[Dict[str, Any]]:
        """
        Process overrides into a list of dictionaries.

        Args:
            overrides: Single dict, file path, or list of dicts/paths

        Returns:
            List of override dictionaries in application order

        Raises:
            ConfigFormatError: If file cannot be loaded or invalid type provided
        """
        if overrides is None:
            return []

        # Normalize to list
        if not isinstance(overrides, list):
            override_list = [overrides]
        else:
            override_list = overrides

        # Process each override source
        processed = []
        for override_source in override_list:
            if isinstance(override_source, dict):
                # Direct dictionary
                processed.append(override_source)
                logger.debug("Added dictionary override")
            elif isinstance(override_source, (str, Path, os.PathLike)):
                # File path - load it
                file_path = Path(override_source)
                try:
                    override_dict = self.loader.load_config_file(file_path)
                    processed.append(override_dict)
                    logger.debug(f"Loaded override from {file_path}")
                except FileNotFoundError:
                    raise ConfigFormatError(f"Override file not found: {file_path}")
                except Exception as e:
                    raise ConfigFormatError(
                        f"Failed to load override file {file_path}: {e}"
                    )
            else:
                raise ConfigFormatError(
                    f"Invalid override type: {type(override_source).__name__}. "
                    f"Expected dict, file path, or list of dicts/paths"
                )

        logger.debug(f"Processed {len(processed)} override sources")
        return processed

    def resolve(self) -> Dict[str, Any]:
        """
        Resolve configuration with full precedence handling.

        Resolution order:
        1. Discover configuration files (hierarchical search)
        2. Load and merge configuration files (most specific first)
        3. Resolve profile with inheritance
        4. Apply overrides in order (highest precedence)

        Returns:
            Resolved configuration dictionary

        Raises:
            ConfigNotFoundError: If no configuration files are found
            ProfileNotFoundError: If requested profile is not found
            CircularInheritanceError: If circular inheritance is detected
            ConfigFormatError: If override files cannot be loaded
        """
        # Step 1: Discover configuration files
        config_files = self.discovery.discover_config_files()
        logger.info(f"Found {len(config_files)} configuration files")

        # Step 2: Load configuration files
        config_data_list = []
        for config_file in reversed(config_files):  # Reverse for precedence order
            try:
                config_data = self.loader.load_config_file(config_file)
                config_data_list.append(config_data)
                logger.debug(f"Loaded config from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
                continue

        if not config_data_list:
            raise ConfigNotFoundError("No valid configuration files could be loaded")

        # Step 3: Merge configuration files
        merged_config = self.merger.merge_config_files(
            config_data_list,
            enable_interpolation=False,  # Defer interpolation until after profile resolution
        )

        # Step 4: Resolve profile
        profile_config = self.profile_resolver.resolve_profile(
            merged_config,
            self.profile,
            self.profile_resolver.get_default_profile(merged_config),
        )

        # Step 5: Apply overrides in order and final interpolation
        if self.override_list:
            # Apply each override in order (later overrides take precedence)
            final_config = self.merger.merge_configs(
                profile_config,
                *self.override_list,  # Unpack list to apply in order
                enable_interpolation=self.enable_interpolation,
            )
            logger.debug(f"Applied {len(self.override_list)} override sources")
        else:
            final_config = self.merger.merge_configs(
                profile_config, enable_interpolation=self.enable_interpolation
            )

        logger.info(
            f"Resolved configuration for profile '{self.profile}' with {len(final_config)} keys"
        )
        return final_config

    def list_profiles(self) -> List[str]:
        """
        List available profiles from discovered configuration.

        Returns:
            List of available profile names
        """
        try:
            config_files = self.discovery.discover_config_files()
        except ConfigNotFoundError:
            return []

        # Load and merge all config files to get complete profile list
        config_data_list = []
        for config_file in config_files:
            try:
                config_data = self.loader.load_config_file(config_file)
                config_data_list.append(config_data)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
                continue

        if not config_data_list:
            return []

        merged_config = self.merger.merge_config_files(
            config_data_list, enable_interpolation=False
        )
        return self.profile_resolver.list_profiles(merged_config)

    def get_config_files(self) -> List[Path]:
        """
        Get list of discovered configuration files.

        Returns:
            List of configuration file paths in precedence order
        """
        try:
            return self.discovery.discover_config_files()
        except ConfigNotFoundError:
            return []
