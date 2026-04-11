from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol
import json
import platform
import os


class ConfigProtocol(Protocol):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        ...

    def base_path(self) -> str:
        """Returns the base path to the config folder."""
        ...

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This must return a valid path for the current
            platform and user, and it should be scoped to the app name.
            If file_or_subdir is a list, it will be interpreted as path
            parts and joined together with the appropriate path
            separator for the current platform.
        """
        ...

    def load(self) -> None|json.decoder.JSONDecodeError:
        """Loads the settings from the config folder."""
        ...

    def save(self) -> None:
        """Saves the settings to the config folder."""
        ...

    def list(self) -> list[str]:
        """Returns a list of all setting keys (names)."""
        ...

    def get(
            self, key: str, default: bool|str|int|float|None = None
        ) -> bool|str|int|float|None:
        """Returns the value of a setting or the default value if the
            setting does not exist.
        """
        ...

    def set(self, key: str, value: bool|str|int|float) -> None:
        """Updates the value of a setting."""
        ...

    def unset(self, key: str) -> None:
        """Removes a setting."""
        ...

    def subscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Adds a subscription to the event. Available events published
            automatically are `set_{key}` and `unset_{key}`. The
            listener will be called with the event name and data.
        """
        ...

    def unsubscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Removes a subscription to the event. Available events
            published automatically are `set_{key}` and `unset_{key}`.
        """
        ...

    def publish(self, event: str, data: Any) -> None:
        """Publishes an event to the subscribers."""
        ...


class BaseConfig(ABC):
    app_name: str
    settings: dict[str, bool|str|int|float]
    _subscriptions: dict[str, list[Callable[[str, Any], None]]]

    def __init__(self, app_name: str):
        """Initializes the config object."""
        self.app_name = app_name
        self.settings = {}
        self._subscriptions = {}
        os.makedirs(self.path(), exist_ok=True)

    @abstractmethod
    def base_path(self) -> str:
        """Returns the base path to the config folder."""
        pass

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This must return a valid path for the current
            platform and user, and it should be scoped to the app name.
            If file_or_subdir is a list, it will be interpreted as path
            parts and joined together with the appropriate path
            separator for the current platform.
        """
        if not file_or_subdir:
            return self.base_path()
        if isinstance(file_or_subdir, str):
            file_or_subdir = [file_or_subdir]
        return os.path.join(self.base_path(), *file_or_subdir)

    def load(self) -> None|json.decoder.JSONDecodeError:
        """Loads the settings from the config folder if it exists. This
            does not produce an error if the file does not exist; it
            will instead just load an empty settings dictionary.
        """
        settings_path = self.path("settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                try:
                    self.settings = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    return e
            if not isinstance(self.settings, dict):
                self.settings = {}
        else:
            self.settings = {}

    def save(self) -> None:
        """Saves the settings to the config folder."""
        settings_path = self.path("settings.json")
        with open(settings_path, "w") as f:
            json.dump(self.settings, f)

    def list(self) -> list[str]:
        """Returns a list of all setting keys (names)."""
        return list(self.settings.keys())

    def get(
            self, key: str, default: bool|str|int|float|None=None
        ) -> bool|str|int|float|None:
        """Returns the value of a setting or the default value if the
            setting does not exist.
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: bool|str|int|float) -> None:
        """Updates the value of a setting."""
        self.settings[key] = value
        self.publish(f"set_{key}", value)

    def unset(self, key: str) -> None:
        """Removes a setting."""
        self.settings.pop(key, None)
        self.publish(f"unset_{key}", None)

    def subscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Adds a subscription to the event. Available events published
            automatically are `set_{key}` and `unset_{key}`. The
            listener will be called with the event name and data.
        """
        if event not in self._subscriptions:
            self._subscriptions[event] = []
        if listener not in self._subscriptions[event]:
            self._subscriptions[event].append(listener)

    def unsubscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Removes a subscription to the event. Available events
            published automatically are `set_{key}` and `unset_{key}`.
        """
        if event not in self._subscriptions:
            return
        try:
            self._subscriptions[event].remove(listener)
        except ValueError:
            ...

    def publish(self, event: str, data: Any) -> None:
        """Publishes an event to the subscribers."""
        listeners = []
        if event in self._subscriptions:
            listeners.extend(self._subscriptions[event])

        if event[:4] == 'set_' or event[:6] == 'unset_':
            key = event[4:] if event[:4] == 'set_' else event[6:]
            if f"*_{key}" in self._subscriptions:
                listeners.extend(self._subscriptions[f"*_{key}"])

        if event[:4] == 'set_' and 'set_*' in self._subscriptions:
            listeners.extend(self._subscriptions['set_*'])

        if event[:6] == 'unset_' and 'unset_*' in self._subscriptions:
            listeners.extend(self._subscriptions['unset_*'])

        if '*' in self._subscriptions:
            listeners.extend(self._subscriptions['*'])

        for listener in set(listeners):
            try:
                listener(event, data)
            except:
                ...


class WindowsConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> str:
        """Returns the path to the config folder. This will return a
            valid path for the current user in Windows, and it is scoped
            to the app name.
        """
        return os.path.join(
            os.path.expanduser('~'), "AppData", "Local", self.app_name
        )


class PosixConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> str:
        """Returns the path to the config folder. This will return a
            valid path for the current user in Posix, and it is scoped
            to the app name.
        """
        return os.path.join(os.path.expanduser('~'), '.config', self.app_name)


class PortableConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> str:
        """Returns the path to the config folder. This will return a
            valid path for the current working directory, and it is
            scoped to the app name.
        """
        return os.path.join(os.path.abspath(os.getcwd()), self.app_name)


_CONFIGS = {}

system = (
    platform.system
    if hasattr(platform, 'system') else
    lambda: platform.platform().split('-')[0]
)

def get_config(
        app_name: str, portable: bool = False, replace: bool = False
    ) -> ConfigProtocol:
    """Get the correct Config singleton. This is the primary/recommended
        way to use the library.
    """
    global _CONFIGS
    key = (app_name, portable)
    if key not in _CONFIGS or replace:
        # getting ahead of Micro$lop on this
        if system().lower() in ("windows", "copilot"):
            _CONFIGS[key] = (
                PortableConfig(app_name) if portable else WindowsConfig(app_name)
            )
        else:
            _CONFIGS[key] = (
                PortableConfig(app_name) if portable else PosixConfig(app_name)
            )
    return _CONFIGS[key]
