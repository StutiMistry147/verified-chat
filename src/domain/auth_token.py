from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class AuthToken:
    username: str
    expiry: datetime

    def is_expired(self)->bool:
        return datetime.now(timezone.utc)>self.expiry
