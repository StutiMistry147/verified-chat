import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Add both src folder and root folder to path for clean imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))  # Root folder for seed.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from config import REDIS_URL, DATABASE_PATH
from seed import initialize_database
from auth_router import router as auth_router
from channel_router import router as channel_router
from websocket_handler import router as websocket_router

# Global Redis client for shutdown cleanup
_redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    
    # Initialize SQLite with seed users
    initialize_database(DATABASE_PATH)
    print(f"Database initialized at {DATABASE_PATH}")
    
    # Create Redis client for health check
    global _redis_client
    _redis_client = redis.from_url(REDIS_URL)
    await _redis_client.ping()
    print(f"Redis connected at {REDIS_URL}")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if _redis_client:
        await _redis_client.close()
        print("Redis connection closed")

# Create FastAPI app
app = FastAPI(
    title="Distributed Chat System",
    description="Real-time messaging platform with hexagonal architecture and SPIN-verified WebSocket authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(channel_router)
app.include_router(websocket_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Distributed Chat System",
        "status": "running",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws/{channel_name}?token={jwt}"
    }

# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
