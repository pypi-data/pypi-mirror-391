import json
from pathlib import Path
from datetime import datetime
from typing import Any

class Chat:
	"""
	An exported Telegram chat.
	"""

	def __init__(self, data: Any):
		self.name: str = data["name"]
		self.type: str = data["type"]
		self.id: int = data["id"]
		self.messages: list[Message] = list(map(Message, data["messages"]))

	@classmethod
	def from_singlechat_export(cls, path: Path) -> "Chat":
		"""
		Create a :class:`Chat` object from a single-chat Telegram GDPR export.
		"""
		with path.open("r", encoding="utf-8") as file_:
			data = json.load(file_)
		return cls(data)

class Message:
	"""
	An exported Telegram message.

	Only interesting fields are kept.
	"""

	def __init__(self, data: Any):
		self.id = data["id"]
		self.type = data["type"]

		try:
			self.date = datetime.fromtimestamp(int(data["date_unixtime"]))
		except KeyError:
			self.date = None
		except ValueError:
			self.date = None
		
		self.actor = data.get("actor")
		self.actor_id = data.get("actor_id")
		self.action = data.get("action")

		self.from_ = data.get("from")
		self.from_id = data.get("from_id")
		self.text = data.get("text")


__all__ = (
	"Chat",
	"Message",
)