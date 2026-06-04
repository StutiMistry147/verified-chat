from abc import ABC, abstractmethod
from typing import List, Optional
from domain.channel import Channel

class ChannelRepositoryPort(ABC):
    @abstractmethod
    async def get_all(self) -> List[Channel]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Channel]:
        pass
