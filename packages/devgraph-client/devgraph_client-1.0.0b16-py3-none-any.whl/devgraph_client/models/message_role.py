from enum import Enum


class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    CHATBOT = "chatbot"
    DEVELOPER = "developer"
    FUNCTION = "function"
    MODEL = "model"
    SYSTEM = "system"
    TOOL = "tool"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
