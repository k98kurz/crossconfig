from .classes import (
    ConfigProtocol,
    BaseConfig,
    WindowsConfig,
    PortableWindowsConfig,
    PosixConfig,
    PortablePosixConfig,
    get_config,
)


__version__ = "0.0.1"

def version() -> str:
    """Returns the version of the crossconfig package."""
    return __version__


__all__ = [
    "ConfigProtocol",
    "BaseConfig",
    "WindowsConfig",
    "PortableWindowsConfig",
    "PosixConfig",
    "PortablePosixConfig",
    "get_config",
    "version",
]
