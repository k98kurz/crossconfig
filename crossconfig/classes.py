from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Protocol
from .errors import type_assert
import json
import logging
import platform
import os


class ConfigProtocol(Protocol):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        ...

    def base_path(self) -> Path:
        """Returns the base path to the config folder."""
        ...

    def path(self, file_or_subdir: str|list[str]|None = None) -> Path:
        """Returns the path to the config folder or a file or subfolder
            within it. This must return a valid path for the current
            platform and user, and it should be scoped to the app name.
            If file_or_subdir is a list, it will be interpreted as path
            parts and joined together with the appropriate path
            separator for the current platform.
        """
        ...

    def load(self) -> None|json.decoder.JSONDecodeError:
        """Loads the settings from the config folder if it exists. This
            does not produce an error if the file does not exist; it
            will instead just load an empty settings dictionary.
            Publishes 'load' event with data of `self.settings` or a
            JSONDecodeError.
        """
        ...

    def save(self) -> None:
        """Saves the settings to the config folder. Publishes 'save'
            event with data of None.
        """
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
            automatically. Triggers `('set', *key)` event, e.g.
            `('set', 'parent', 'child')`.
        """
        ...

    def unset(self, key: str|list[str]) -> None:
        """Removes a setting. For nested values, pass a list of key parts
            (e.g., ["parent", "child"]). Always publishes unset event
            of `('unset', *key)` even if the path does not exist.
        """
        ...

    def subscribe(
            self, event: str|tuple[str],
            listener: Callable[[str|tuple[str], Any], None]
        ) -> None:
        """Adds a subscription to the event. Automatic events include
            `('set', *key)`, `('unset', *key)`, 'save', and 'load'.
            Custom hierarchical events are supported and bubble properly.
            Wildcards: `('*', *key)`, `('set', '*')`, `('unset', '*')`,
            and `'*'`/`('*',)` (all). The listener receives
            `(event_key, data)`. Note that listeners subscribed to
            `'parent'` will receive the `('parent',)` event but will not
            receive any bubbled events, while listeners subscribed to
            `('parent',)` will receive `'parent'` and bubbled events,
            e.g. `('parent', 'child')`. Listeners are deduplicated
            before being called, and order of listeners is deterministic.
        """
        ...

    def unsubscribe(
            self, event: str|tuple[str],
            listener: Callable[[str|tuple[str], Any], None]
        ) -> None:
        """Removes a subscription to the event. Available events
            published automatically are 'save', 'load', `('set', *key)`,
            and `('unset', *key)`.
        """
        ...

    def publish(self, event: str|tuple[str], data: Any) -> None:
        """Publishes an event to the subscribers. Bubbles up from exact
            matches through parent levels and wildcards (i.e.
            `('*', *key)`, `('set', '*')`, `('unset', '*')`, `('*',)`).
            Nested events notify all parent listeners (e.g.,
            `set(['a', 'b'])` reaches `('set', 'a'`) and
            `('do', 'foo', 'bar')` reaches `('*', 'foo')`). Publishing
            `'parent'` triggers `('parent',)` listeners, and publishing
            `('parent,')` triggers `'parent'` listeners, but publishing
            `('parent', 'child')` does not trigger `'parent'` listeners.
            Deduplicates listeners to avoid calling the same listener
            more than once. Exceptions raised by listeners are
            suppressed by default.
        """
        ...

    def set_logger(self, logger: logging.Logger) -> None:
        """Configures a logger for listener error reporting."""
        ...

    def set_suppress_listener_errors(self, suppress: bool) -> None:
        """Enables/disables suppression of exceptions from listeners."""
        ...


class BaseConfig(ABC):
    app_name: str
    settings: dict[str, bool|str|int|float|list|dict]
    _subscriptions: dict[
        str|tuple[str],
        dict[Callable[[str|tuple[str], Any], None], None]
    ]
    _logger: logging.Logger | None
    _suppress_listener_errors: bool

    def __init__(self, app_name: str):
        """Initializes the config object."""
        self.app_name = app_name
        self.settings = {}
        self._subscriptions = {}
        self._logger = None
        self._suppress_listener_errors = True
        os.makedirs(self.path(), exist_ok=True)

    @abstractmethod
    def base_path(self) -> Path:
        """Returns the base path to the config folder."""
        pass

    def path(self, file_or_subdir: str|list[str]|None = None) -> Path:
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
        result = self.base_path()
        for part in file_or_subdir:
            result = result / part
        return result

    def load(self) -> None|json.decoder.JSONDecodeError:
        """Loads the settings from the config folder if it exists. This
            does not produce an error if the file does not exist; it
            will instead just load an empty settings dictionary.
            Publishes 'load' event with data of `self.settings` or a
            JSONDecodeError.
        """
        settings_path = self.path("settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                try:
                    self.settings = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    self.publish('load', e)
                    return e
            if not isinstance(self.settings, dict):
                self.settings = {}
        else:
            self.settings = {}
        self.publish('load', self.settings)

    def save(self) -> None:
        """Saves the settings to the config folder. Publishes 'save'
            event with data of None.
        """
        settings_path = self.path("settings.json")
        with open(settings_path, "w") as f:
            json.dump(self.settings, f)
        self.publish('save', None)

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
            automatically. Triggers `('set', *key)` event, e.g.
            `('set', 'parent', 'child')`.
        """
        if isinstance(key, str):
            self.settings[key] = value
            self.publish(("set", key), value)
        else:
            current = self.settings
            for part in key[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            current[key[-1]] = value
            self.publish(("set", *key), value)

    def unset(self, key: str|list[str]) -> None:
        """Removes a setting. For nested values, pass a list of key parts
            (e.g., ["parent", "child"]). Always publishes unset event
            of `('unset', *key)` even if the path does not exist.
        """
        if isinstance(key, str):
            self.settings.pop(key, None)
            self.publish(("unset", key), None)
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

            self.publish(("unset", *key), None)

    def subscribe(
            self, event: str|tuple[str],
            listener: Callable[[str|tuple[str], Any], None]
        ) -> None:
        """Adds a subscription to the event. Automatic events include
            `('set', *key)`, `('unset', *key)`, 'save', and 'load'.
            Custom hierarchical events are supported and bubble properly.
            Wildcards: `('*', *key)`, `('set', '*')`, `('unset', '*')`,
            and `'*'`/`('*',)` (all). The listener receives
            `(event_key, data)`. Note that listeners subscribed to
            `'parent'` will receive the `('parent',)` event but will not
            receive any bubbled events, while listeners subscribed to
            `('parent',)` will receive `'parent'` and bubbled events,
            e.g. `('parent', 'child')`. Listeners are deduplicated
            before being called, and order of listeners is deterministic.
        """
        event = tuple(event) if isinstance(event, list) else event
        type_assert(type(event) in (str, tuple), 'event must be str|tuple[str]')
        if type(event) is tuple:
            type_assert(
                all([type(t) is str for t in event]), 'event must be str|tuple[str]'
            )
        type_assert(callable(listener), 'listener must be callable')
        if event not in self._subscriptions:
            self._subscriptions[event] = {}
        if listener not in self._subscriptions[event]:
            self._subscriptions[event][listener] = None

    def unsubscribe(
            self, event: str|tuple[str],
            listener: Callable[[str|tuple[str], Any], None]
        ) -> None:
        """Removes a subscription to the event. Available events
            published automatically are 'save', 'load', `('set', *key)`,
            and `('unset', *key)`.
        """
        event = tuple(event) if isinstance(event, list) else event
        type_assert(type(event) in (str, tuple), 'event must be str|tuple[str]')
        if type(event) is tuple:
            type_assert(
                all([type(t) is str for t in event]), 'event must be str|tuple[str]'
            )
        type_assert(callable(listener), 'listener must be callable')
        if event not in self._subscriptions:
            return
        self._subscriptions[event].pop(listener, None)
        # reclaim some memory
        if not len(self._subscriptions[event]):
            self._subscriptions.pop(event)

    def publish(self, event: str|tuple[str], data: Any) -> None:
        """Publishes an event to the subscribers. Bubbles up from exact
            matches through parent levels and wildcards (i.e.
            `('*', *key)`, `('set', '*')`, `('unset', '*')`, `('*',)`).
            Nested events notify all parent listeners (e.g.,
            `set(['a', 'b'])` reaches `('set', 'a'`) and
            `('do', 'foo', 'bar')` reaches `('*', 'foo')`). Publishing
            `'parent'` triggers `('parent',)` listeners, and publishing
            `('parent,')` triggers `'parent'` listeners, but publishing
            `('parent', 'child')` does not trigger `'parent'` listeners.
            Deduplicates listeners to avoid calling the same listener
            more than once. Exceptions raised by listeners are
            suppressed by default.
        """
        event = tuple(event) if isinstance(event, list) else event
        type_assert(type(event) in (str, tuple), 'event must be str|tuple[str]')
        if type(event) is tuple:
            type_assert(
                all([type(t) is str for t in event]), 'event must be str|tuple[str]'
            )
        listeners = []
        listeners.extend(self._subscriptions.get(event, {}).keys())

        if type(event) is str:
            listeners.extend(self._subscriptions.get((event,), {}).keys())

        if type(event) is tuple:
            # trigger listeners for `'custom'` with event `('custom',)`
            if len(event) == 1:
                listeners.extend(self._subscriptions.get(event[0], {}).keys())

            # bubble up the event from deepest to shallowest listeners
            for i in range(len(event), 0, -1):
                listeners.extend(self._subscriptions.get(event[:i], {}).keys())

            # handle root wildcards, e.g. ('*', 'thing')
            key = event[1:]
            for i in range(len(key), -1, -1):
                listeners.extend(self._subscriptions.get(('*', *key[:i]), {}).keys())

            # handle ('set', '*'), ('unset', '*'), etc
            listeners.extend(self._subscriptions.get((event[0], '*'), {}).keys())

        listeners.extend(self._subscriptions.get('*', {}).keys())
        listeners.extend(self._subscriptions.get(('*',), {}).keys())

        called = set()
        for listener in listeners:
            if listener in called:
                continue
            called.add(listener)
            try:
                listener(event, data)
            except Exception as e:
                if self._logger:
                    self._logger.exception(f"Listener failed for event {event}")
                if not self._suppress_listener_errors:
                    raise

    def set_logger(self, logger: logging.Logger) -> None:
        """Configures a logger for listener error reporting."""
        type_assert(isinstance(logger, logging.Logger), 'logger must be logging.Logger')
        self._logger = logger

    def set_suppress_listener_errors(self, suppress: bool) -> None:
        """Enables/disables suppression of exceptions from listeners."""
        type_assert(type(suppress) is bool, 'suppress must be bool')
        self._suppress_listener_errors = suppress


class WindowsConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> Path:
        """Returns the path to the config folder. This will return a
            valid path for the current user in Windows, and it is scoped
            to the app name.
        """
        return Path(os.path.expanduser('~')) / "AppData" / "Local" / self.app_name


class PosixConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> Path:
        """Returns the path to the config folder. This will return a
            valid path for the current user in Posix, and it is scoped
            to the app name.
        """
        return Path(os.path.expanduser('~')) / '.config' / self.app_name


class PortableConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def base_path(self) -> Path:
        """Returns the path to the config folder. This will return a
            valid path for the current working directory, and it is
            scoped to the app name.
        """
        return Path(os.path.abspath(os.getcwd())) / self.app_name


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
