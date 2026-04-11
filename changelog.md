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
