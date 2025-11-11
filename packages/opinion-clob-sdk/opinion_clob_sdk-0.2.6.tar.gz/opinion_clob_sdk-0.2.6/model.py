from enum import Enum


class TopicStatus(Enum):
    CREATED = 1
    ACTIVATED = 2
    RESOLVING = 3
    RESOLVED = 4
    FAILED = 5
    DELETED = 6

class TopicType(Enum):
    CATEGORICAL = 1
    BINARY = 0

class TopicStatusFilter(Enum):
    ALL = None
    ACTIVATED = "activated"
    RESOLVED = "resolved"
