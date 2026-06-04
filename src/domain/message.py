from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    id: int
    content: str
    username: str
    channel_name: str
    timestamp: datetime
