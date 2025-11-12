import enum


class CancellationType(str, enum.Enum):
    """Type of cancellation used by the backend"""

    EDGE = "edge"
    LEVEL = "level"
