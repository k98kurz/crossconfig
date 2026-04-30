---
name: crossconfig
description: Manage cross-platform application configuration with the crossconfig library. Supports nested settings, event subscriptions, and automatic platform detection (Windows/POSIX). TRIGGER when: user asks about configuration management, settings storage, app config, user preferences, or mentions crossconfig.
license: ISC LICENSE
---

# CrossConfig: Cross-Platform Configuration Management

This skill teaches you how to manage application configuration across platforms using the `crossconfig` library. Configuration is automatically stored in the appropriate platform-specific location:

- **Windows**: `~\AppData\Local\{app_name}\settings.json`
- **POSIX/macOS**: `~/.config/{app_name}/settings.json`
- **Portable**: Current working directory: `{cwd}/{app_name}/settings.json`

## Getting Started

Always use `get_config()` as the primary entry point:

```python
from crossconfig import get_config

# Get config for your app (auto-detects platform)
config = get_config("my_app")

# Load existing settings (creates empty dict if file doesn't exist)
config.load()

# Basic operations
config.set("theme", "dark")           # Set a value
theme = config.get("theme")           # Get value (returns None if not found)
font_size = config.get("font_size", 12)  # Get with default
config.unset("theme")                 # Remove a value
keys = config.list()                  # List all keys

# Save to disk
config.save()
```

`get_config()` returns a **singleton** - the same instance for the same `app_name` and `portable` mode within a process. This ensures consistent behavior across your application. Use `replace=True` to force recreation (primarily for testing).

## Path Utilities

CrossConfig provides utilities for working with paths in your configuration directory.

- `config.path(file_or_subdir: str|list[str]|None = None) -> Path`

### Getting Configuration Paths

```python
# Get the config folder path
folder = config.path()

# Get path to a specific file
log_path = config.path("app.log")               # .../app.log

# Get path to nested directories/files using list of strs
data_file = config.path(["cache", "data.db"])   # .../cache/data.db
```

**Key Features:**
- **Platform-appropriate separators**: Lists are joined with correct OS separators (`/` or `\`)
- **Scoped to app_name**: All paths are within your app's config directory
- **Does not create files**: Only returns paths; doesn't create files or directories

### Common Path Use Cases

```python
# Access database paths
database_path = config.path("app.db")
migrations_path = config.path("migrations")
os.makedirs(migrations_path, exist_ok=True)

# Access custom directories
chunks_dir = config.path(["sync", "chunks"])
os.makedirs(chunks_dir, exist_ok=True)

# Working with cache items
cache_path = config.path("cache")
files = []
if os.path.exists(cache_path):
    for filename in os.listdir(cache_path):
        with open(config.path(["cache", filename]), 'r') as f:
            files.append(f.read())
```

## Nested Configuration

Use list keys for hierarchical settings. CrossConfig automatically creates intermediate dictionaries:

```python
# Set nested values (creates intermediate dicts automatically)
config.set(["database", "host"], "localhost")
config.set(["database", "port"], 5432)
config.set(["ui", "theme", "dark"], True)

# Get nested values
host = config.get(["database", "host"])           # "localhost"
db_config = config.get("database")                # {"host": "localhost", "port": 5432}
missing = config.get(["database", "missing"], "default")  # "default"
```

Supported value types: `bool`, `str`, `int`, `float`, `list`, `dict`.

## Event System

CrossConfig has a publish/subscribe event system for reacting to configuration changes.

### Automatic Events
- `('set', *key)` - Fired when a value is set
- `('unset', *key)` - Fired when a value is unset
- `'save'` - Fired after saving to disk
- `'load'` - Fired after loading from disk

```python
def on_setting_change(event, data):
    print(f"Event: {event}, Data: {data}")

# Subscribe to specific events
config.subscribe(("set", "theme"), on_setting_change)
config.subscribe("save", lambda e, d: print("Saved!"))

config.set("theme", "dark")  # Event: ('set', 'theme'), Data: dark
config.save()                # Saved!
```

### Wildcard Subscriptions
Use wildcards to match multiple events:

```python
# Listen to ALL set/unset events
config.subscribe(("set", "*"), lambda e, d: print(f"Set: {e}"))
config.subscribe(("unset", "*"), lambda e, d: print(f"Unset: {e}"))

# Listen to ANY event on a specific key
config.subscribe(("*", "theme"), lambda e, d: print(f"Theme: {e}"))

# Listen to ALL events
config.subscribe("*", lambda e, d: print(f"Any: {e}"))
```

### Nested Key Events
```python
# Listen to changes under "database" section
config.subscribe(("*", "database"), lambda e, d: print(f"DB: {e}"))

config.set(["database", "host"], "192.168.1.1")  # DB: ('set', 'database', 'host')
config.unset(["database", "port"])               # DB: ('unset', 'database', 'port')
```

### Custom Events
Publish and subscribe to custom events:

```python
config.subscribe("custom_event", lambda e, d: print(f"Custom: {d}"))
config.publish("custom_event", {"data": "value"})
```

### Unsubscribing
```python
listener = lambda e, d: print(f"Event: {e}")
config.subscribe("save", listener)
config.unsubscribe("save", listener)
```

## Platform Selection

```python
# Automatic platform detection (recommended)
config = get_config("my_app")

# For portable configs (current working directory)
config = get_config("my_app", portable=True)

# Force recreation of singleton (useful for testing)
config = get_config("my_app", replace=True)
```

The `replace` parameter forces creation of a new config instance even if one already exists for the same `app_name`. This is primarily useful for testing to ensure a clean state.

Portable mode stores config in the project directory instead of user's config folder.

## Common Patterns

```python
# Initialize config with defaults
config = get_config("my_app")
config.load()
if config.get("initialized") is None:
    config.set("initialized", True)
    config.set("version", "1.0.0")
    config.save()

# Atomic updates
config.load()
old_value = config.get("counter", 0)
config.set("counter", old_value + 1)
config.save()

# Configuration migration
config.load()
old_host = config.get("db_host")
if old_host:
    config.set(["database", "host"], old_host)
    config.unset("db_host")
    config.save()
```

## Utility Functions

### `version()`

Get the installed version of crossconfig:

```python
from crossconfig import get_config, version

print(f"CrossConfig version: {version()}")
# Output: CrossConfig version: 0.0.6
```

## Important Notes

- **JSON format**: Configuration is stored as JSON in `settings.json`
- **Thread safety**: No locking - avoid concurrent `save()`/`load()` in multi-threaded environments
- **Load errors**: `load()` returns `JSONDecodeError` on failure, publishes `'load'` event with error, leaves in-memory settings unchanged
- **Overwrites**: `load()` completely replaces in-memory settings with file contents

## Error Handling

```python
# load() returns None on success, JSONDecodeError on failure
result = config.load()

if isinstance(result, Exception):
    print(f"Invalid JSON: {result}")
else:
    print(f"Loaded {len(config.list())} settings")
```

## Testing

Consider:
- Platform-specific paths (use `portable=True` for tests)
- Clean slate between tests (use `replace=True` or use fresh app_name)
- Event listener cleanup (unsubscribe listeners to avoid cross-test pollution)
- Path utility usage (use `config.path()` for test file paths)
