"""
Kilowatts

This package name is reserved.
Visit https://kilowatts.io for more information.
"""

__version__ = "0.0.1"
__all__ = []


def _unavailable():
    """Raise an error indicating the package is not yet available."""
    raise NotImplementedError(
        "This package is reserved. Visit https://kilowatts.io for more information."
    )


class Client:
    """Reserved."""

    def __init__(self, *args, **kwargs):
        _unavailable()
