## 0.0.5

- Added list key syntax for nested configuration access
  - `get()` and `set()` now accept `list[str]` keys for hierarchical access
  - Example: `config.set(["parent", "child"], value)`
  - Intermediate dicts created automatically on `set()`
- Extended supported value types to include `list` and `dict`
- Migrated event system from string-based to tuple-based event keys
  - Automatic events now use tuple format: `('set', *key)` and `('unset', *key)`
  - Example: `config.set(["parent", "child"], value)` publishes `('set', 'parent', 'child')`
  - Hierarchical wildcard support: `('*', 'parent')` matches all events under 'parent'
  - Backward compatibility maintained for custom string events
- Added `load` and `save` events for file operations
  - `load` publishes `('load', settings)` on success, `('load', error)` on JSON
   decode error
  - `save` publishes `('save', None)` after writing to file
- Event delivery now maintains execution order with deduplication
  - Listeners called from most specific to least specific (exact match → parent
    levels → wildcards)
  - Events bubble to all parent listeners in hierarchy
- Custom hierarchical events now support bubbling to parent levels
  - Subscribe to `('do', 'something')` to receive `('do', 'something')`,
    `('do', 'something', 'more')`, etc.
  - Wildcards work with custom events: `('*', 'something')` matches any first
    element with 'something' as second

## 0.0.4

- Added publish/subscribe event system for configuration changes
- New methods: `subscribe()`, `unsubscribe()`, `publish()`
- Automatic events: `set_{key}` and `unset_{key}` fire on setting modifications
- Wildcard subscription support: `*_{key}`, `set_*`, `unset_*`, and `*`
- Listener exceptions are suppressed to prevent breaking the config system

## 0.0.3

- Corrections for type hints that were missed in 0.0.2
- Changed path handling logic to use `os.path.join`
- Consolidated portable configs to a single class since behavior is identical
across platforms
- Added forward compatibility for when Micro$lop inevitably rebrands their OS
to "Copilot"
- Updated docs.md

## 0.0.2

- Improved platform detection
- Improved type hints to all JSON basic value types

## 0.0.1

- Initial release.
- `PosixConfig` and `PortablePosixConfig` confirmed working on Linux.
- `WindowsConfig` and `PortableWindowsConfig` confirmed working on Windows.
