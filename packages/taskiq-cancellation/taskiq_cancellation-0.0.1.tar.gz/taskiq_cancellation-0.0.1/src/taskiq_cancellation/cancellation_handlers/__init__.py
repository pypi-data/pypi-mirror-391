import sys

from .cancellation_type import CancellationType
from .level import LevelCancellationHandler

if sys.version_info >= (3, 11):
    from .edge_3_11 import EdgeCancellationHandler
else:
    from .edge_non_supported import EdgeCancellationHandler


__all__ = ["CancellationType", "LevelCancellationHandler", "EdgeCancellationHandler"]
