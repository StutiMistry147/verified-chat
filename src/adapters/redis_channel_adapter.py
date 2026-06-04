from typing import List, Optional
from ports.channel_repository_port import ChannelRepositoryPort
from domain.channel import Channel

class RedisChannelAdapter(ChannelRepositoryPort):
    def __init__(self):
        self.channels = [
            Channel(id=1, name="general"),
            Channel(id=2, name="random"),
            Channel(id=3, name="dev")
        ]
    
    async def get_all(self) -> List[Channel]:
        return self.channels
    
    async def get_by_name(self, name: str) -> Optional[Channel]:
        for channel in self.channels:
            if channel.name == name:
                return channel
        return None
