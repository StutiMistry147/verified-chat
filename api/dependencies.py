import redis.asyncio as redis
from fastapi import Depends
from config import DATABASE_PATH, REDIS_URL

from ports.user_repository_port import UserRepositoryPort
from ports.message_publisher_port import MessagePublisherPort
from ports.channel_repository_port import ChannelRepositoryPort

from adapters.sqlite_user_adapter import SQLiteUserAdapter
from adapters.redis_publisher_adapter import RedisPublisherAdapter
from adapters.redis_channel_adapter import RedisChannelAdapter

# Singleton instances
_user_repository = None
_redis_client = None
_message_publisher = None
_channel_repository = None

async def get_user_repository() -> UserRepositoryPort:
    global _user_repository
    if _user_repository is None:
        _user_repository = SQLiteUserAdapter(DATABASE_PATH)
    return _user_repository

async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL)
    return _redis_client

async def get_message_publisher(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> MessagePublisherPort:
    global _message_publisher
    if _message_publisher is None:
        _message_publisher = RedisPublisherAdapter(redis_client)
    return _message_publisher

async def get_channel_repository() -> ChannelRepositoryPort:
    global _channel_repository
    if _channel_repository is None:
        _channel_repository = RedisChannelAdapter()
    return _channel_repository
