from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Annotated

from ports.channel_repository_port import ChannelRepositoryPort
from dependencies import get_channel_repository
from auth_utils import verify_jwt, extract_token_from_header

router = APIRouter(prefix="/channels", tags=["channels"])

async def get_current_user(authorization: str = Header(...)) -> str:
    token = extract_token_from_header(authorization)
    return verify_jwt(token)

@router.get("/")
async def get_channels(
    channel_repository: ChannelRepositoryPort = Depends(get_channel_repository),
    current_user: str = Depends(get_current_user)
):
    channels = await channel_repository.get_all()
    return [{"id": c.id, "name": c.name} for c in channels]

@router.get("/{channel_name}")
async def get_channel(
    channel_name: str,
    channel_repository: ChannelRepositoryPort = Depends(get_channel_repository),
    current_user: str = Depends(get_current_user)
):
    channel = await channel_repository.get_by_name(channel_name)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel '{channel_name}' not found"
        )
    return {"id": channel.id, "name": channel.name}
