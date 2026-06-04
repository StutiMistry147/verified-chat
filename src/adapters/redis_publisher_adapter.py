import json
from datetime import datetime
import redis.asyncio as redis
from typing import AsyncGenerator
from ports.message_publisher_port import MessagePublisherPort
from domain.message import Message

class RedisPublisherAdapter(MessagePublisherPort):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def publish(self, message: Message, channel_name: str) -> None:
        payload = json.dumps({
            "id": message.id,
            "content": message.content,
            "username": message.username,
            "channel_name": message.channel_name,
            "timestamp": message.timestamp.isoformat()
        })
        await self.redis_client.publish(channel_name, payload)
    
    async def subscribe(self, channel_name: str) -> AsyncGenerator[Message, None]:
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel_name)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield Message(
                        id=data["id"],
                        content=data["content"],
                        username=data["username"],
                        channel_name=data["channel_name"],
                        timestamp=datetime.fromisoformat(data["timestamp"])
                    )
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()
