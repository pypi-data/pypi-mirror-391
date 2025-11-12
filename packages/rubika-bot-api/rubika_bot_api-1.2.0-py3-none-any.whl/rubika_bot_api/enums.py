"""Enum types for better type safety and code clarity."""
from enum import Enum


class STREnum(str, Enum):
    """Base string enum class."""
    pass


class ChatTypeEnum(STREnum):
    """Chat type enumeration."""
    USER = "User"
    BOT = "Bot"
    GROUP = "Group"
    CHANNEL = "Channel"


class ChatKeypadTypeEnum(STREnum):
    """Chat keypad type enumeration."""
    NONE = "None"
    NEW = "New"
    REMOVED = "Removed"


class UpdateTypeEnum(STREnum):
    """Update type enumeration."""
    NewMessage = "NewMessage"
    UpdatedMessage = "UpdatedMessage"
    RemovedMessage = "RemovedMessage"
    StartedBot = "StartedBot"
    StoppedBot = "StoppedBot"
    ReceiveQuery = "ReceiveQuery"


class MediaTypeEnum(STREnum):
    """Media type for file uploads."""
    File = "File"
    Image = "Image"
    Voice = "Voice"
    Music = "Music"
    Gif = "Gif"
    Video = "Video"


class ParseMode(str, Enum):
    """Text parse modes for message formatting."""
    HTML = 'html'
    MARKDOWN = 'markdown'

