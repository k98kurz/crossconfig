from .classes import (
    ConfigProtocol,
    BaseConfig,
    WindowsConfig,
    PosixConfig,
    PortableConfig,
    get_config,
)


__version__ = "0.0.3"

def version() -> str:
    """Returns the version of the crossconfig package."""
    return __version__


__all__ = [
    "ConfigProtocol",
    "BaseConfig",
    "WindowsConfig",
    "PosixConfig",
    "PortableConfig",
    "get_config",
    "version",
]
