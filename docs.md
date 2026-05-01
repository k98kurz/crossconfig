# crossconfig

## Classes

### `ConfigProtocol(Protocol)`

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> Path:`

Returns the base path to the config folder.

##### `path(file_or_subdir: str | list[str] | None = None) -> Path:`

Returns the path to the config folder or a file or subfolder within it. This
must return a valid path for the current platform and user, and it should be
scoped to the app name. If file_or_subdir is a list, it will be interpreted as
path parts and joined together with the appropriate path separator for the
current platform.

##### `load() -> None | json.decoder.JSONDecodeError:`

Loads the settings from the config folder if it exists. This does not produce an
error if the file does not exist; it will instead just load an empty settings
dictionary. Publishes 'load' event with data of `self.settings` or a
JSONDecodeError.

##### `save() -> None:`

Saves the settings to the config folder. Publishes 'save' event with data of
None.

##### `list() -> list[str]:`

Returns a list of all setting keys (names).

##### `get(key: str | list[str], default: bool | str | int | float | list | dict | None = None) -> bool | str | int | float | list | dict | None:`

Returns the value of a setting or the default value if the setting does not
exist. For nested access, pass a list of key parts (e.g., ["parent", "child"])
to traverse nested dicts; returns default if any path element is missing.

##### `set(key: str | list[str], value: bool | str | int | float | list | dict) -> None:`

Updates the value of a setting. For nested access, pass a list of key parts
(e.g., ["parent", "child"], value) to set values in nested dicts. Intermediate
dicts are created automatically. Triggers `('set', *key)` event, e.g. `('set',
'parent', 'child')`.

##### `unset(key: str | list[str]) -> None:`

Removes a setting. For nested values, pass a list of key parts (e.g., ["parent",
"child"]). Always publishes unset event of `('unset', *key)` even if the path
does not exist.

##### `subscribe(event: str | tuple[str], listener: Callable[[str | tuple[str], Any], None]) -> None:`

Adds a subscription to the event. Automatic events include `('set', *key)`,
`('unset', *key)`, 'save', and 'load'. Custom hierarchical events are supported
and bubble properly. Wildcards: `('*', *key)`, `('set', '*')`, `('unset', '*')`,
and `'*'`/`('*',)` (all). The listener receives `(event_key, data)`. Note that
listeners subscribed to `'parent'` will receive the `('parent',)` event but will
not receive any bubbled events, while listeners subscribed to `('parent',)` will
receive `'parent'` and bubbled events, e.g. `('parent', 'child')`. Listeners are
deduplicated before being called, and order of listeners is deterministic.

##### `unsubscribe(event: str | tuple[str], listener: Callable[[str | tuple[str], Any], None]) -> None:`

Removes a subscription to the event. Available events published automatically
are 'save', 'load', `('set', *key)`, and `('unset', *key)`.

##### `publish(event: str | tuple[str], data: Any) -> None:`

Publishes an event to the subscribers. Bubbles up from exact matches through
parent levels and wildcards (i.e. `('*', *key)`, `('set', '*')`, `('unset',
'*')`, `('*',)`). Nested events notify all parent listeners (e.g., `set(['a',
'b'])` reaches `('set', 'a'`) and `('do', 'foo', 'bar')` reaches `('*',
'foo')`). Publishing `'parent'` triggers `('parent',)` listeners, and publishing
`('parent,')` triggers `'parent'` listeners, but publishing `('parent',
'child')` does not trigger `'parent'` listeners. Deduplicates listeners to avoid
calling the same listener more than once. Exceptions raised by listeners are
suppressed by default.

##### `set_logger(logger: logging.Logger) -> None:`

Configures a logger for listener error reporting.

##### `set_suppress_listener_errors(suppress: bool) -> None:`

Enables/disables suppression of exceptions from listeners.

### `BaseConfig(ABC)`

#### Annotations

- app_name: str
- settings: dict[str, bool | str | int | float | list | dict]
- _subscriptions: dict[str | tuple[str], dict[Callable[[str | tuple[str], Any],
None], None]]
- _logger: logging.Logger | None
- _suppress_listener_errors: bool

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> Path:`

Returns the base path to the config folder.

##### `path(file_or_subdir: str | list[str] | None = None) -> Path:`

Returns the path to the config folder or a file or subfolder within it. This
must return a valid path for the current platform and user, and it should be
scoped to the app name. If file_or_subdir is a list, it will be interpreted as
path parts and joined together with the appropriate path separator for the
current platform.

##### `load() -> None | json.decoder.JSONDecodeError:`

Loads the settings from the config folder if it exists. This does not produce an
error if the file does not exist; it will instead just load an empty settings
dictionary. Publishes 'load' event with data of `self.settings` or a
JSONDecodeError.

##### `save() -> None:`

Saves the settings to the config folder. Publishes 'save' event with data of
None.

##### `list() -> list[str]:`

Returns a list of all setting keys (names).

##### `get(key: str | list[str], default: bool | str | int | float | list | dict | None = None) -> bool | str | int | float | list | dict | None:`

Returns the value of a setting or the default value if the setting does not
exist. For nested access, pass a list of key parts (e.g., ["parent", "child"])
to traverse nested dicts; returns default if any path element is missing.

##### `set(key: str | list[str], value: bool | str | int | float | list | dict) -> None:`

Updates the value of a setting. For nested access, pass a list of key parts
(e.g., ["parent", "child"], value) to set values in nested dicts. Intermediate
dicts are created automatically. Triggers `('set', *key)` event, e.g. `('set',
'parent', 'child')`.

##### `unset(key: str | list[str]) -> None:`

Removes a setting. For nested values, pass a list of key parts (e.g., ["parent",
"child"]). Always publishes unset event of `('unset', *key)` even if the path
does not exist.

##### `subscribe(event: str | tuple[str], listener: Callable[[str | tuple[str], Any], None]) -> None:`

Adds a subscription to the event. Automatic events include `('set', *key)`,
`('unset', *key)`, 'save', and 'load'. Custom hierarchical events are supported
and bubble properly. Wildcards: `('*', *key)`, `('set', '*')`, `('unset', '*')`,
and `'*'`/`('*',)` (all). The listener receives `(event_key, data)`. Note that
listeners subscribed to `'parent'` will receive the `('parent',)` event but will
not receive any bubbled events, while listeners subscribed to `('parent',)` will
receive `'parent'` and bubbled events, e.g. `('parent', 'child')`. Listeners are
deduplicated before being called, and order of listeners is deterministic.

##### `unsubscribe(event: str | tuple[str], listener: Callable[[str | tuple[str], Any], None]) -> None:`

Removes a subscription to the event. Available events published automatically
are 'save', 'load', `('set', *key)`, and `('unset', *key)`.

##### `publish(event: str | tuple[str], data: Any) -> None:`

Publishes an event to the subscribers. Bubbles up from exact matches through
parent levels and wildcards (i.e. `('*', *key)`, `('set', '*')`, `('unset',
'*')`, `('*',)`). Nested events notify all parent listeners (e.g., `set(['a',
'b'])` reaches `('set', 'a'`) and `('do', 'foo', 'bar')` reaches `('*',
'foo')`). Publishing `'parent'` triggers `('parent',)` listeners, and publishing
`('parent,')` triggers `'parent'` listeners, but publishing `('parent',
'child')` does not trigger `'parent'` listeners. Deduplicates listeners to avoid
calling the same listener more than once. Exceptions raised by listeners are
suppressed by default.

##### `set_logger(logger: logging.Logger) -> None:`

Configures a logger for listener error reporting.

##### `set_suppress_listener_errors(suppress: bool) -> None:`

Enables/disables suppression of exceptions from listeners.

### `WindowsConfig(BaseConfig)`

#### Annotations

- app_name: str
- settings: dict[str, bool | str | int | float | list | dict]
- _subscriptions: dict[str | tuple[str], dict[Callable[[str | tuple[str], Any],
None], None]]
- _logger: logging.Logger | None
- _suppress_listener_errors: bool

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> Path:`

Returns the path to the config folder. This will return a valid path for the
current user in Windows, and it is scoped to the app name.

### `PosixConfig(BaseConfig)`

#### Annotations

- app_name: str
- settings: dict[str, bool | str | int | float | list | dict]
- _subscriptions: dict[str | tuple[str], dict[Callable[[str | tuple[str], Any],
None], None]]
- _logger: logging.Logger | None
- _suppress_listener_errors: bool

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> Path:`

Returns the path to the config folder. This will return a valid path for the
current user in Posix, and it is scoped to the app name.

### `PortableConfig(BaseConfig)`

#### Annotations

- app_name: str
- settings: dict[str, bool | str | int | float | list | dict]
- _subscriptions: dict[str | tuple[str], dict[Callable[[str | tuple[str], Any],
None], None]]
- _logger: logging.Logger | None
- _suppress_listener_errors: bool

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> Path:`

Returns the path to the config folder. This will return a valid path for the
current working directory, and it is scoped to the app name.

## Functions

### `get_config(app_name: str, portable: bool = False, replace: bool = False) -> ConfigProtocol:`

Get the correct Config singleton. This is the primary/recommended way to use the
library.

### `version() -> str:`

Returns the version of the crossconfig package.


