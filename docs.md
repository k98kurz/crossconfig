# crossconfig

## Classes

### `ConfigProtocol(Protocol)`

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> str:`

Returns the base path to the config folder.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
must return a valid path for the current platform and user, and it should be
scoped to the app name. If file_or_subdir is a list, it will be interpreted as
path parts and joined together with the appropriate path separator for the
current platform.

##### `load() -> None | json.decoder.JSONDecodeError:`

Loads the settings from the config folder.

##### `save():`

Saves the settings to the config folder.

##### `list() -> list[str]:`

Returns a list of all setting keys (names).

##### `get(key: str, default: bool | str | int | float | None = None) -> bool | str | int | float | None:`

Returns the value of a setting or the default value if the setting does not
exist.

##### `set(key: str, value: bool | str | int | float):`

Updates the value of a setting.

##### `unset(key: str):`

Removes a setting.

##### `subscribe(event: str, listener: Callable):`

Adds a subscription to the event. Available events published automatically are
`set_{key}` and `unset_{key}`. The listener will be called with the event name
and data.

##### `unsubscribe(event: str, listener: Callable):`

Removes a subscription to the event. Available events published automatically
are `set_{key}` and `unset_{key}`.

##### `publish(event: str, data: Any):`

Publishes an event to the subscribers.

### `BaseConfig(ABC)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, bool | str | int | float]
- _subscriptions: dict[str, list[typing.Callable[[str, typing.Any], NoneType]]]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> str:`

Returns the base path to the config folder.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
must return a valid path for the current platform and user, and it should be
scoped to the app name. If file_or_subdir is a list, it will be interpreted as
path parts and joined together with the appropriate path separator for the
current platform.

##### `load() -> None | json.decoder.JSONDecodeError:`

Loads the settings from the config folder if it exists. This does not produce an
error if the file does not exist; it will instead just load an empty settings
dictionary.

##### `save():`

Saves the settings to the config folder.

##### `list() -> list[str]:`

Returns a list of all setting keys (names).

##### `get(key: str, default: bool | str | int | float | None = None) -> bool | str | int | float | None:`

Returns the value of a setting or the default value if the setting does not
exist.

##### `set(key: str, value: bool | str | int | float):`

Updates the value of a setting.

##### `unset(key: str):`

Removes a setting.

##### `subscribe(event: str, listener: Callable):`

Adds a subscription to the event. Available events published automatically are
`set_{key}` and `unset_{key}`. The listener will be called with the event name
and data.

##### `unsubscribe(event: str, listener: Callable):`

Removes a subscription to the event. Available events published automatically
are `set_{key}` and `unset_{key}`.

##### `publish(event: str, data: Any):`

Publishes an event to the subscribers.

### `WindowsConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, bool | str | int | float]
- _subscriptions: dict[str, list[typing.Callable[[str, typing.Any], NoneType]]]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> str:`

Returns the path to the config folder. This will return a valid path for the
current user in Windows, and it is scoped to the app name.

### `PosixConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, bool | str | int | float]
- _subscriptions: dict[str, list[typing.Callable[[str, typing.Any], NoneType]]]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> str:`

Returns the path to the config folder. This will return a valid path for the
current user in Posix, and it is scoped to the app name.

### `PortableConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, bool | str | int | float]
- _subscriptions: dict[str, list[typing.Callable[[str, typing.Any], NoneType]]]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `base_path() -> str:`

Returns the path to the config folder. This will return a valid path for the
current working directory, and it is scoped to the app name.

## Functions

### `get_config(app_name: str, portable: bool = False, replace: bool = False) -> ConfigProtocol:`

Get the correct Config singleton. This is the primary/recommended way to use the
library.

### `version() -> str:`

Returns the version of the crossconfig package.


