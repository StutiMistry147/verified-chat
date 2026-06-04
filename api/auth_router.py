from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import bcrypt

from ports.user_repository_port import UserRepositoryPort
from dependencies import get_user_repository
from auth_utils import create_jwt

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    user_repository: UserRepositoryPort = Depends(get_user_repository)
):
    user = await user_repository.get_by_username(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not bcrypt.checkpw(request.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_jwt(user.username)
    return TokenResponse(access_token=token, token_type="bearer")
