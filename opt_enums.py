from enum import Enum

class LongNames(Enum):
    NOFIX = 1
    TRUNCATE = 2
    RANDOM = 3

class NameChars(Enum):
    NOFIX = 1
    WINDOWS = 2

class ReservedNames(Enum):
    NOFIX = 1
    WINDOWS = 2

class Structure(Enum):
    SITE = 1
    EXTENSION = 2
    TWODIR = 3
    ONEDIR = 4

class MaxRequests(Enum):
    NOLIMIT = -1