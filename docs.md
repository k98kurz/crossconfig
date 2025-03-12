# crossconfig

## Classes

### `ConfigProtocol(Protocol)`

#### Methods

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

##### `get(key: str, default: str | int | None = None) -> str | int | None:`

Returns the value of a setting or the default value if the setting does not
exist.

##### `set(key: str, value: str | int):`

Updates the value of a setting.

##### `unset(key: str):`

Removes a setting.

### `BaseConfig(ABC)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, str | int]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

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

##### `get(key: str, default: str | int | None = None) -> str | int | None:`

Returns the value of a setting or the default value if the setting does not
exist.

##### `set(key: str, value: str | int):`

Updates the value of a setting.

##### `unset(key: str):`

Removes a setting.

### `WindowsConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, str | int]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
will return a valid path for the current user in Windows, and it is scoped to
the app name.

### `PortableWindowsConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, str | int]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
will return a valid path for the current user in Windows, and it is scoped to
the app name.

### `PosixConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, str | int]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
will return a valid path for the current user in Posix, and it is scoped to the
app name.

### `PortablePosixConfig(BaseConfig)`

#### Annotations

- app_name: <class 'str'>
- settings: dict[str, str | int]

#### Methods

##### `__init__(app_name: str):`

Initializes the config object.

##### `path(file_or_subdir: str | list[str] | None = None) -> str:`

Returns the path to the config folder or a file or subfolder within it. This
will return a valid path for the current user in Posix, and it is scoped to the
app name.

## Functions

### `get_config(app_name: str, portable: bool = False, replace: bool = False) -> ConfigProtocol:`

### `version() -> str:`

Returns the version of the crossconfig package.


