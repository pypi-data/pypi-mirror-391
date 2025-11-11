from enum import Enum


class NullBooleanEnum(str, Enum):
    FALSE = "false"
    NULL = "null"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
