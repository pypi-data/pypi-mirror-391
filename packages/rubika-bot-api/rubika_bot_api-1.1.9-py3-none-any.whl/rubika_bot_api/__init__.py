"""Lightweight package entry for rubika_bot_api.

This module intentionally avoids importing heavy submodules at import time.
Access to exported symbols is provided lazily via __getattr__ so importing
``rubika_bot_api`` remains fast and lightweight.
"""

__version__ = "1.1.5"

# Public API names (available via lazy import)
__all__ = [
    "Robot",
    "InvalidTokenError",
    "Message",
    "InlineMessage",
    "APIRequestError",
    "filters",
]


def __getattr__(name: str):
    # Lazy-load common symbols on demand to keep top-level import cheap.
    if name in ("Robot", "InvalidTokenError"):
        from .api import Robot, InvalidTokenError

        return Robot if name == "Robot" else InvalidTokenError

    if name in ("Message", "InlineMessage"):
        from .update import Message, InlineMessage

        return Message if name == "Message" else InlineMessage

    if name == "APIRequestError":
        from .exceptions import APIRequestError

        return APIRequestError

    if name == "filters":
        # Import the submodule directly via importlib to avoid re-entering
        # package attribute resolution which would call __getattr__ again.
        import importlib

        _filters = importlib.import_module(__name__ + ".filters")
        return _filters

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + __all__)
