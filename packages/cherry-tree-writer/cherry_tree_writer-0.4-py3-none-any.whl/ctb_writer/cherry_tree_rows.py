from dataclasses import dataclass

@dataclass(frozen=True)
class _NodeRow:
    NODE_ID = 0
    NAME = 1
    TXT = 2
    SYNTAX = 3
    TAGS = 4
    IS_RO = 5
    IS_RICHTEXT = 6
    HAS_CODEBOX = 7
    HAS_TABLE = 8
    HAS_IMAGE = 9

@dataclass(frozen=True)
class _ImageRow:
    NODE_ID = 0
    OFFSET = 1
    JUSTIFICATION = 2
    ANCHOR = 3
    PNG = 4

@dataclass(frozen=True)
class _TableRow:
    NODE_ID = 0
    OFFSET = 1
    JUSTIFICATION = 2
    TXT = 3
    COL_MIN = 4
    COL_MAX = 5

@dataclass(frozen=True)
class _CodeboxRow:
    NODE_ID = 0
    OFFSET = 1
    JUSTIFICATION = 2
    TXT = 3
    SYNTAX = 4
    WIDTH = 5
    HEIGHT = 6
    IS_WIDTH_PIX = 7
    HIGHLIGHT_BRACKETS = 8
    SHOW_LINE_NUMBERS = 9
