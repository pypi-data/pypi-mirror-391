"""Enums for rubika_bot_api.

This package re-exports the enums used across the library. It intentionally
combines the previously separate `enums.py` module and the `parse_mode` helper
so imports like `from .enums import ChatTypeEnum` continue to work.
"""

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


__all__ = [
	"STREnum",
	"ChatTypeEnum",
	"ChatKeypadTypeEnum",
	"UpdateTypeEnum",
	"MediaTypeEnum",
	"ParseMode",
]
