from __future__ import annotations

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
            self, key: str|list[str],
            default: bool|str|int|float|list|dict|None = None
        ) -> bool|str|int|float|list|dict|None:
        """Returns the value of a setting or the default value if the
            setting does not exist. For nested access, pass a list of
            key parts (e.g., ["parent", "child"]) to traverse nested
            dicts; returns default if any path element is missing.
        """
        ...

    def set(self, key: str|list[str], value: bool|str|int|float|list|dict) -> None:
        """Updates the value of a setting. For nested access, pass a
            list of key parts (e.g., ["parent", "child"], value) to
            set values in nested dicts. Intermediate dicts are created
            automatically. Triggers 'set_{key}' event with '_' joined
            list keys (e.g., 'set_parent_child').
        """
        ...

    def unset(self, key: str|list[str]) -> None:
        """Removes a setting. For nested values, pass a list of key parts
            (e.g., ["parent", "child"]). Always publishes unset event
            even if the path does not exist.
        """
        ...

    def subscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Adds a subscription to the event. Automatic events include
            'set_{key}' and 'unset_{key}' for config changes. List keys
            generate events with parts joined by '_' (e.g., 'set_a_b_c').
            Wildcards: '*_{key}', 'set_*', 'unset_*', and '*' (all).
            The listener receives (event_name, data).
        """
        ...

    def unsubscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Removes a subscription to the event. Available events
            published automatically are `set_{key}` and `unset_{key}`.
        """
        ...

    def publish(self, event: str, data: Any) -> None:
        """Publishes an event to the subscribers. Fires exact matches,
            wildcards (*_{key}, set_*, unset_*, *), and deduplicates
            listeners before calling them. Exceptions raised by
            listeners are suppressed.
        """
        ...


class BaseConfig(ABC):
    app_name: str
    settings: dict[str, bool|str|int|float|list|dict]
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
            self, key: str|list[str],
            default: bool|str|int|float|list|dict|None = None
        ) -> bool|str|int|float|list|dict|None:
        """Returns the value of a setting or the default value if the
            setting does not exist. For nested access, pass a list of
            key parts (e.g., ["parent", "child"]) to traverse nested
            dicts; returns default if any path element is missing.
        """
        if isinstance(key, str):
            return self.settings.get(key, default)
        current = self.settings
        for part in key:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def set(self, key: str|list[str], value: bool|str|int|float|list|dict) -> None:
        """Updates the value of a setting. For nested access, pass a
            list of key parts (e.g., ["parent", "child"], value) to
            set values in nested dicts. Intermediate dicts are created
            automatically. Triggers 'set_{key}' event with '_' joined
            list keys (e.g., 'set_parent_child').
        """
        if isinstance(key, str):
            self.settings[key] = value
            self.publish(f"set_{key}", value)
        else:
            current = self.settings
            for part in key[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            current[key[-1]] = value
            self.publish(f"set_{'_'.join(key)}", value)

    def unset(self, key: str|list[str]) -> None:
        """Removes a setting. For nested values, pass a list of key parts
            (e.g., ["parent", "child"]). Always publishes unset event
            even if the path does not exist.
        """
        if isinstance(key, str):
            self.settings.pop(key, None)
            self.publish(f"unset_{key}", None)
        else:
            if not key:
                return

            current = self.settings
            for part in key[:-1]:
                if not isinstance(current, dict):
                    current = None
                    break
                current = current.get(part)

            if isinstance(current, dict) and key[-1] in current:
                del current[key[-1]]

            self.publish(f"unset_{'_'.join(key)}", None)

    def subscribe(self, event: str, listener: Callable[[str, Any], None]) -> None:
        """Adds a subscription to the event. Automatic events include
            'set_{key}' and 'unset_{key}' for config changes. List keys
            generate events with parts joined by '_' (e.g., 'set_a_b_c').
            Wildcards: '*_{key}', 'set_*', 'unset_*', and '*' (all).
            The listener receives (event_name, data).
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
        """Publishes an event to the subscribers. Fires exact matches,
            wildcards (*_{key}, set_*, unset_*, *), and deduplicates
            listeners before calling them. Exceptions raised by
            listeners are suppressed.
        """
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
