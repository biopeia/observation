"""Symbiont: the organism."""

__version__ = "0.90.0"

def __getattr__(name: str):
    """Load the public core package only when requested.

    Keeping package initialization inert lets leaf modules be imported directly
    and exposes dependency cycles instead of masking them with eager imports.
    """
    if name == "core":
        from importlib import import_module

        core = import_module("symbiont.core")
        globals()[name] = core
        return core
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["__version__", "core"]
