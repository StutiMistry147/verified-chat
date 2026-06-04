from abc import ABC, abstractmethod
from typing import AsyncGenerator
from domain.message import Message

class MessagePublisherPort(ABC):
    @abstractmethod
    async def publish(self, message: Message, channel_name: str)-> None:
        pass

    @abstractmethod
    async def subscribe(self, channel_name: str)-> AsyncGenerator[Message, None]:
        pass
