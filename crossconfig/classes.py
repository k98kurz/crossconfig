from abc import ABC, abstractmethod
from typing import Protocol
import json
import platform
import os


class ConfigProtocol(Protocol):
    def __init__(self, app_name: str):
        """Initializes the config object."""
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

    def get(self, key: str, default: str|int|None = None) -> str|int|None:
        """Returns the value of a setting or the default value if the
            setting does not exist.
        """
        ...

    def set(self, key: str, value: str|int) -> None:
        """Updates the value of a setting."""
        ...

    def unset(self, key: str) -> None:
        """Removes a setting."""
        ...


class BaseConfig(ABC):
    app_name: str
    settings: dict[str, str|int]

    def __init__(self, app_name: str):
        """Initializes the config object."""
        self.app_name = app_name
        self.settings = {}
        os.makedirs(self.path(), exist_ok=True)

    @abstractmethod
    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This must return a valid path for the current
            platform and user, and it should be scoped to the app name.
            If file_or_subdir is a list, it will be interpreted as path
            parts and joined together with the appropriate path
            separator for the current platform.
        """
        pass

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

    def get(self, key: str, default: str|int|None=None) -> str|int|None:
        """Returns the value of a setting or the default value if the
            setting does not exist.
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: str|int) -> None:
        """Updates the value of a setting."""
        self.settings[key] = value

    def unset(self, key: str) -> None:
        """Removes a setting."""
        self.settings.pop(key, None)


class WindowsConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This will return a valid path for the current
            user in Windows, and it is scoped to the app name.
        """
        base = f"{os.path.expanduser('~')}\\AppData\\Local\\{self.app_name}"
        if file_or_subdir is None:
            return base
        if isinstance(file_or_subdir, list):
            return f"{base}\\" + '\\'.join(file_or_subdir)
        return f"{base}\\{file_or_subdir}"


class PortableWindowsConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This will return a valid path for the current
            user in Windows, and it is scoped to the app name.
        """
        base = f"{os.path.abspath(os.getcwd())}\\{self.app_name}"
        if file_or_subdir is None:
            return base
        if isinstance(file_or_subdir, list):
            return f"{base}\\" + '\\'.join(file_or_subdir)
        return f"{base}\\{file_or_subdir}"


class PosixConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This will return a valid path for the current
            user in Posix, and it is scoped to the app name.
        """
        base = f"{os.path.expanduser('~')}/.config/{self.app_name}"
        if file_or_subdir is None:
            return base
        if isinstance(file_or_subdir, list):
            return f"{base}/{'/'.join(file_or_subdir)}"
        return f"{base}/{file_or_subdir}"


class PortablePosixConfig(BaseConfig):
    def __init__(self, app_name: str):
        """Initializes the config object."""
        super().__init__(app_name)

    def path(self, file_or_subdir: str|list[str]|None = None) -> str:
        """Returns the path to the config folder or a file or subfolder
            within it. This will return a valid path for the current
            user in Posix, and it is scoped to the app name.
        """
        base = f"{os.path.abspath(os.getcwd())}/{self.app_name}"
        if file_or_subdir is None:
            return base
        if isinstance(file_or_subdir, list):
            return f"{base}/{'/'.join(file_or_subdir)}"
        return f"{base}/{file_or_subdir}"


_CONFIGS = {}

def get_config(app_name: str, portable: bool = False, replace: bool = False) -> ConfigProtocol:
    global _CONFIGS
    key = (app_name, portable)
    if key not in _CONFIGS or replace:
        if platform.system() == "Windows":
            _CONFIGS[key] = PortableWindowsConfig(app_name) if portable else WindowsConfig(app_name)
        else:
            _CONFIGS[key] = PortablePosixConfig(app_name) if portable else PosixConfig(app_name)
    return _CONFIGS[key]
