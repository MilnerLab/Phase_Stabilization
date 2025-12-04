# stream_io/__init__.py
"""
Client-side streaming utilities to receive spectrometer data
from the 32-bit acquisition process.
"""

from .stream_client import (
    SpectrometerStreamClient,
    StreamMeta,
    StreamFrame,
)

__all__ = [
    "SpectrometerStreamClient",
    "StreamMeta",
    "StreamFrame",
]
