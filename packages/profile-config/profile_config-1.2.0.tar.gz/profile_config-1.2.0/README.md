# Profile Config

[![Tests](https://github.com/bassmanitram/profile-config/actions/workflows/test.yml/badge.svg)](https://github.com/bassmanitram/profile-config/actions/workflows/test.yml)
[![Lint](https://github.com/bassmanitram/profile-config/actions/workflows/lint.yml/badge.svg)](https://github.com/bassmanitram/profile-config/actions/workflows/lint.yml)
[![Examples](https://github.com/bassmanitram/profile-config/actions/workflows/examples.yml/badge.svg)](https://github.com/bassmanitram/profile-config/actions/workflows/examples.yml)
[![Code Quality](https://github.com/bassmanitram/profile-config/actions/workflows/quality.yml/badge.svg)](https://github.com/bassmanitram/profile-config/actions/workflows/quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/profile-config.svg)](https://badge.fury.io/py/profile-config)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Profile-based configuration management for Python applications.

## What It Does

Profile Config manages application configuration using profiles (e.g., development, staging, production). It discovers configuration files in your project hierarchy, merges them with proper precedence, and resolves the requested profile.

### Configuration Flow

```
1. Discovery Phase
   Search locations (highest to lowest precedence):
   ./myapp/config.yaml          <- Current directory
   ../myapp/config.yaml         <- Parent directory
   ../../myapp/config.yaml      <- Grandparent directory
   ~/myapp/config.yaml         <- Home directory

2. Merge Phase
   Files are merged with closer files taking precedence

3. Profile Resolution
   defaults + profile + inherited profiles

4. Override Phase
   Apply runtime overrides (highest precedence)

5. Interpolation Phase
   Resolve ${variable} references
```

### Example

Given this configuration file at `myapp/config.yaml`:

```yaml
defaults:
  host: localhost
  port: 5432
  debug: false

profiles:
  development:
    debug: true
    database: myapp_dev

  production:
    host: prod-db.example.com
    database: myapp_prod
```

This code:

```python
from profile_config import ProfileConfigResolver

resolver = ProfileConfigResolver("myapp", profile="development")
config = resolver.resolve()
```

Produces this configuration:

```python
{
    "host": "localhost",      # from defaults
    "port": 5432,             # from defaults
    "debug": True,            # from development profile (overrides defaults)
    "database": "myapp_dev"   # from development profile
}
```

## Installation

```bash
pip install profile-config
```

For TOML support on Python < 3.11:
```bash
pip install profile-config[toml]
```

## Basic Usage

### 1. Create Configuration File

Create `myapp/config.yaml` in your project:

```yaml
defaults:
  timeout: 30
  retries: 3

profiles:
  development:
    debug: true
    log_level: DEBUG

  production:
    debug: false
    log_level: WARNING
```

### 2. Load Configuration

```python
from profile_config import ProfileConfigResolver

# Load development profile
resolver = ProfileConfigResolver("myapp", profile="development")
config = resolver.resolve()

# Access configuration values
print(config["timeout"])    # 30 (from defaults)
print(config["debug"])      # True (from development profile)
print(config["log_level"])  # DEBUG (from development profile)
```

## Configuration File Discovery

Profile Config searches for configuration files by walking up the directory tree from the current working directory, then checking the home directory.

### Search Pattern

Default pattern: `{config_name}/{profile_filename}.{extension}`

Examples:
- `myapp/config.yaml` (default)
- `myapp/settings.yaml` (custom filename)
- `myapp/app.json` (custom filename)

### Search Order (highest to lowest precedence)

```
Current directory:     ./myapp/config.yaml
Parent directory:      ../myapp/config.yaml
Grandparent directory: ../../myapp/config.yaml
...
Home directory:        ~/myapp/config.yaml
```

### File Extensions

Searches for files with these extensions (in order):
- `.yaml`
- `.yml`
- `.json`
- `.toml`

### Example Directory Structure

```
/home/user/projects/myapp/
├── backend/
│   └── myapp/
│       └── config.yaml      <- Project-specific config
└── myapp/
    └── config.yaml          <- Shared config

/home/user/myapp/
└── config.yaml              <- User-specific config
```

When running from `/home/user/projects/myapp/backend/`:
1. Finds `./myapp/config.yaml` (current directory)
2. Finds `../myapp/config.yaml` (parent directory)
3. Finds `~/myapp/config.yaml` (home directory)
4. Merges all three (current directory has highest precedence)

### Custom Profile Filename

Use a different filename instead of `config`:

```python
# Search for settings.yaml instead of config.yaml
resolver = ProfileConfigResolver(
    "myapp",
    profile="development",
    profile_filename="settings"
)
```

This searches for:
- `./myapp/settings.yaml`
- `../myapp/settings.yaml`
- `~/myapp/settings.yaml`

Use cases:
- Organization naming standards (e.g., `settings.yaml`)
- Multiple configuration types in same directory
- Legacy system compatibility
- More descriptive names (e.g., `database.yaml`, `api.yaml`)

## Configuration File Format

### Structure

```yaml
# Optional: specify which profile to use by default
default_profile: development

# Optional: values applied to all profiles
defaults:
  timeout: 30
  retries: 3

# Required: profile definitions
profiles:
  development:
    debug: true
    database: myapp_dev

  production:
    debug: false
    database: myapp_prod
```

### Supported Formats

#### YAML
```yaml
defaults:
  host: localhost
  port: 5432

profiles:
  development:
    debug: true
```

#### JSON
```json
{
  "defaults": {
    "host": "localhost",
    "port": 5432
  },
  "profiles": {
    "development": {
      "debug": true
    }
  }
}
```

#### TOML
```toml
[defaults]
host = "localhost"
port = 5432

[profiles.development]
debug = true
```

## Using the Default Profile

The "default" profile has special behavior that makes it easy to use only the defaults section without defining an explicit profile.

### Automatic Creation

When you request `profile="default"` and no "default" profile exists in your configuration, an empty profile is automatically created. This returns only the values from the `defaults` section.

```yaml
defaults:
  host: localhost
  port: 5432
  timeout: 30

profiles:
  development:
    debug: true
    port: 3000

  production:
    host: prod-db.com
    debug: false
```

```python
# No explicit "default" profile defined in config
resolver = ProfileConfigResolver("myapp", profile="default")
config = resolver.resolve()

# Returns only defaults:
# {
#     "host": "localhost",
#     "port": 5432,
#     "timeout": 30
# }
```

### Explicit Default Profile

If you define an explicit "default" profile, it takes precedence over the auto-creation:

```yaml
defaults:
  host: localhost
  port: 5432
  timeout: 30

profiles:
  default:
    timeout: 60      # Override default timeout
    custom: true     # Add custom setting

  development:
    debug: true
```

```python
resolver = ProfileConfigResolver("myapp", profile="default")
config = resolver.resolve()

# Returns defaults + default profile:
# {
#     "host": "localhost",
#     "port": 5432,
#     "timeout": 60,      # Overridden by default profile
#     "custom": True      # Added by default profile
# }
```

### Use Cases

**1. Base configuration without environment-specific overrides:**
```python
# Get base configuration only
resolver = ProfileConfigResolver("myapp", profile="default")
base_config = resolver.resolve()
```

**2. Fallback when no specific profile is needed:**
```python
import os

# Use environment-specific profile if set, otherwise use defaults
env = os.environ.get("ENV", "default")
resolver = ProfileConfigResolver("myapp", profile=env)
config = resolver.resolve()
```

**3. Testing with minimal configuration:**
```python
# Tests can use "default" profile for baseline behavior
def test_app_with_defaults():
    resolver = ProfileConfigResolver("myapp", profile="default")
    config = resolver.resolve()
    # Test with minimal config
```

## Profile Inheritance

Profiles can inherit from other profiles using the `inherits` key.

### Example

```yaml
profiles:
  base:
    host: localhost
    timeout: 30

  development:
    inherits: base
    debug: true
    database: myapp_dev

  staging:
    inherits: development
    debug: false
    host: staging-db.example.com
```

### Resolution Order

For profile `staging`:
1. Start with `base` profile
2. Merge `development` profile (overrides `base`)
3. Merge `staging` profile (overrides `development`)

Result:
```python
{
    "host": "staging-db.example.com",  # from staging (overrides base)
    "timeout": 30,                      # from base
    "debug": False,                     # from staging (overrides development)
    "database": "myapp_dev"             # from development
}
```

### Multi-Level Inheritance

```yaml
profiles:
  base:
    timeout: 30

  development:
    inherits: base
    debug: true

  development-team1:
    inherits: development
    team_id: team1

  development-team2:
    inherits: development
    team_id: team2
```

Circular inheritance is detected and raises an error.

## Variable Interpolation

Use `${variable}` syntax to reference other configuration values.

### Example

```yaml
defaults:
  app_name: myapp
  base_path: /opt/${app_name}
  data_path: ${base_path}/data
  log_path: ${base_path}/logs

profiles:
  development:
    base_path: /tmp/${app_name}
```

### Resolution

For profile `development`:
```python
{
    "app_name": "myapp",
    "base_path": "/tmp/myapp",           # interpolated
    "data_path": "/tmp/myapp/data",      # interpolated
    "log_path": "/tmp/myapp/logs"        # interpolated
}
```

Variables are resolved after profile inheritance is complete.

## Runtime Overrides

Apply configuration overrides at runtime with highest precedence.

### Dictionary Override

```python
resolver = ProfileConfigResolver(
    "myapp",
    profile="production",
    overrides={"debug": True, "host": "test-db.example.com"}
)
config = resolver.resolve()
```

### File Override

```python
resolver = ProfileConfigResolver(
    "myapp",
    profile="production",
    overrides="/path/to/overrides.yaml"
)
config = resolver.resolve()
```

Supported formats: `.yaml`, `.yml`, `.json`, `.toml`

### List of Overrides

Apply multiple overrides in order (later overrides take precedence):

```python
resolver = ProfileConfigResolver(
    "myapp",
    profile="production",
    overrides=[
        "/path/to/base-overrides.yaml",
        {"debug": True},
        "/path/to/final-overrides.json"
    ]
)
config = resolver.resolve()
```

### Precedence Order

```
1. Discovered config files (lowest)
2. Profile resolution
3. Override 1
4. Override 2
5. Override N (highest)
```

## Configuration Options

### Customize Search Behavior

```python
resolver = ProfileConfigResolver(
    config_name="myapp",
    profile="development",
    extensions=["yaml", "json"],  # Only search these formats
    search_home=False,            # Don't search home directory
)
```

### Custom Profile Filename

```python
# Use settings.yaml instead of config.yaml
resolver = ProfileConfigResolver(
    "myapp",
    profile="development",
    profile_filename="settings"
)
```

### Custom Inheritance Key

```python
# Use 'extends' instead of 'inherits'
resolver = ProfileConfigResolver(
    "myapp",
    profile="development",
    inherit_key="extends"
)
```

### Disable Variable Interpolation

```python
resolver = ProfileConfigResolver(
    "myapp",
    profile="development",
    enable_interpolation=False
)
```

## Utility Methods

### List Available Profiles

```python
resolver = ProfileConfigResolver("myapp")
profiles = resolver.list_profiles()
print(profiles)  # ['development', 'staging', 'production']
```

### Get Discovered Files

```python
resolver = ProfileConfigResolver("myapp")
files = resolver.get_config_files()
for file_path in files:
    print(file_path)
```

## Error Handling

Profile Config raises specific exceptions for different error conditions.

### Exception Types

```python
from profile_config.exceptions import (
    ConfigNotFoundError,      # No configuration files found
    ProfileNotFoundError,     # Requested profile doesn't exist
    CircularInheritanceError, # Circular inheritance detected
    ConfigFormatError         # Invalid configuration file format
)
```

### Example

```python
from profile_config import ProfileConfigResolver
from profile_config.exceptions import ProfileNotFoundError

try:
    resolver = ProfileConfigResolver("myapp", profile="nonexistent")
    config = resolver.resolve()
except ProfileNotFoundError as e:
    print(f"Profile not found: {e}")
    # Handle error (use default profile, exit, etc.)
```

## Common Patterns

### Environment-Based Configuration

```python
import os
from profile_config import ProfileConfigResolver

env = os.environ.get("ENV", "development")
resolver = ProfileConfigResolver("myapp", profile=env)
config = resolver.resolve()
```

### Team-Specific Configuration

```yaml
profiles:
  development:
    debug: true

  development-team1:
    inherits: development
    team_id: team1
    endpoint: "https://team1.internal.com"

  development-team2:
    inherits: development
    team_id: team2
    endpoint: "https://team2.internal.com"
```

```python
import os
from profile_config import ProfileConfigResolver

team = os.environ.get("TEAM_NAME", "")
env = os.environ.get("ENV", "development")
profile = f"{env}-{team}" if team else env

resolver = ProfileConfigResolver("myapp", profile=profile)
config = resolver.resolve()
```

### Configuration with Secrets

Store secrets separately and merge at runtime:

```python
import json
from pathlib import Path
from profile_config import ProfileConfigResolver

# Load base configuration
resolver = ProfileConfigResolver("myapp", profile="production")
config = resolver.resolve()

# Load secrets from secure location
secrets_file = Path("/etc/secrets/myapp.json")
if secrets_file.exists():
    with open(secrets_file) as f:
        secrets = json.load(f)
    config.update(secrets)
```

Or use overrides:

```python
resolver = ProfileConfigResolver(
    "myapp",
    profile="production",
    overrides="/etc/secrets/myapp.json"
)
config = resolver.resolve()
```

## Format Comparison

| Feature | YAML | JSON | TOML |
|---------|------|------|------|
| Comments | Yes | No | Yes |
| Multi-line strings | Yes | Escaped only | Yes |
| Type safety | Inferred | Limited | Native types |
| Nesting | Natural | Natural | Verbose for deep nesting |
| Readability | High | Medium | High |
| Ecosystem | Mature | Universal | Growing |

### When to Use Each Format

**YAML**: Complex nested configurations, human-edited files
**JSON**: API integration, machine-generated configs, data exchange
**TOML**: Application configuration with type safety, flat structures

## Examples

The `examples/` directory contains working examples:

- `basic_usage.py` - Basic configuration and profile usage
- `advanced_profiles.py` - Inheritance patterns and error handling
- `default_profile_usage.py` - Default profile auto-creation and use cases
- `web_app_config.py` - Web application configuration management
- `toml_usage.py` - TOML format features

Run examples:

```bash
cd examples
python basic_usage.py
```

## Development

### Setup

```bash
git clone https://github.com/bassmanitram/profile-config.git
cd profile-config
pip install -e ".[dev,toml]"
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=profile_config --cov-report=html
```

## API Reference

### ProfileConfigResolver

```python
ProfileConfigResolver(
    config_name: str,
    profile: str = "default",
    profile_filename: str = "config",
    overrides: Optional[Union[Dict, PathLike, List[Union[Dict, PathLike]]]] = None,
    extensions: Optional[List[str]] = None,
    search_home: bool = True,
    inherit_key: str = "inherits",
    enable_interpolation: bool = True,
)
```

**Parameters:**

- `config_name`: Name of configuration directory (e.g., "myapp")
- `profile`: Profile name to resolve (default: "default")
- `profile_filename`: Name of profile file without extension (default: "config")
- `overrides`: Override values (dict, file path, or list of dicts/paths)
- `extensions`: File extensions to search (default: ["yaml", "yml", "json", "toml"])
- `search_home`: Whether to search home directory (default: True)
- `inherit_key`: Key name for profile inheritance (default: "inherits")
- `enable_interpolation`: Whether to enable variable interpolation (default: True)

**Methods:**

- `resolve() -> Dict[str, Any]`: Resolve and return configuration
- `list_profiles() -> List[str]`: List available profiles
- `get_config_files() -> List[Path]`: Get discovered configuration files

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome. Please read CONTRIBUTING.md for guidelines.

## Links

- GitHub: https://github.com/bassmanitram/profile-config
- PyPI: https://pypi.org/project/profile-config/
- Issues: https://github.com/bassmanitram/profile-config/issues

## Changelog

See CHANGELOG.md for version history.
