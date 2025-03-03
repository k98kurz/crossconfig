from .classes import *


__version__ = "0.0.1"

def version() -> str:
    """Returns the version of the crossconfig package."""
    return __version__


__all__ = [
    "BaseConfig",
    "WindowsConfig",
    "PortableWindowsConfig",
    "PosixConfig",
    "PortablePosixConfig",
    "get_config",
    "version",
]
