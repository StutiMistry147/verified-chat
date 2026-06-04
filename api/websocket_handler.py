import asyncio
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import traceback

from auth_utils import verify_jwt
from ports.message_publisher_port import MessagePublisherPort
from ports.channel_repository_port import ChannelRepositoryPort
from ports.user_repository_port import UserRepositoryPort
from dependencies import get_message_publisher, get_channel_repository, get_user_repository
from domain.message import Message

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{channel_name}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_name: str,
    message_publisher: MessagePublisherPort = Depends(get_message_publisher),
    channel_repository: ChannelRepositoryPort = Depends(get_channel_repository),
    user_repository: UserRepositoryPort = Depends(get_user_repository)
):
    # Step 1: Extract token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return
    
    # Step 2: Verify JWT - this is the critical auth step
    try:
        username = verify_jwt(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid authentication token")
        return
    
    # Step 3: Verify channel exists
    channel = await channel_repository.get_by_name(channel_name)
    if not channel:
        await websocket.close(code=1008, reason=f"Channel '{channel_name}' does not exist")
        return
    
    # Step 4: Verify user exists
    user = await user_repository.get_by_username(username)
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Step 5: Accept the connection after all auth checks pass
    await websocket.accept()
    
    # Step 6: Subscribe to Redis channel
    message_generator = message_publisher.subscribe(channel_name)
    
    # Track tasks for cleanup
    receive_task = None
    send_task = None
    
    async def receive_messages():
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    payload = json.loads(data)
                    content = payload.get("content", "")
                    if not content.strip():
                        continue
                    
                    # Unique message ID using UUID
                    message = Message(
                        id=str(uuid.uuid4()),
                        content=content,
                        username=username,
                        channel_name=channel_name,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Publish to Redis
                    await message_publisher.publish(message, channel_name)
                except json.JSONDecodeError:
                    # Invalid JSON, ignore
                    continue
        except WebSocketDisconnect:
            pass
        except Exception as e:
            # Log unexpected error, connection will be cleaned up
            print(f"Unexpected error in receive_messages: {e}")
            traceback.print_exc()
    
    async def send_messages():
        try:
            async for message in message_generator:
                # Redis subscription is already channel-scoped, no filter needed
                payload = {
                    "id": message.id,
                    "content": message.content,
                    "username": message.username,
                    "channel_name": message.channel_name,
                    "timestamp": message.timestamp.isoformat()
                }
                await websocket.send_json(payload)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Unexpected error in send_messages: {e}")
            traceback.print_exc()
    
    # Step 7: Run both tasks concurrently
    receive_task = asyncio.create_task(receive_messages())
    send_task = asyncio.create_task(send_messages())
    
    try:
        await asyncio.gather(receive_task, send_task)
    finally:
        # Cancel both tasks to ensure cleanup
        if receive_task and not receive_task.done():
            receive_task.cancel()
        if send_task and not send_task.done():
            send_task.cancel()
        
        # Wait for cancellation to complete
        await asyncio.gather(receive_task, send_task, return_exceptions=True)
