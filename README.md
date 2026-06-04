# Verified Chat
A production-grade distributed messaging platform with formally verified WebSocket authentication and hexagonal architecture. Unlike standard chat applications, this system guarantees—proven mathematically via SPIN model checking—that no message is processed before authentication completes, across all possible concurrent execution paths.

## Why This Matters

Most chat systems handle authentication as an afterthought, leading to race conditions where messages slip through before a user is fully verified. This project embeds authentication as a first-class architectural constraint, formally verified at the model level, then implemented with strict separation between business logic and infrastructure.

## Architecture

The system uses hexagonal architecture (ports and adapters) to isolate core domain logic from external concerns:

```
                    ┌─────────────────────────────────────┐
                    │           Domain Layer              │
                    │  User | Message | Channel | AuthToken│
                    └─────────────────┬───────────────────┘
                                      │ (depends on)
                    ┌─────────────────▼───────────────────┐
                    │           Ports (Interfaces)         │
                    │  UserRepository | MessagePublisher   │
                    └─────────────────┬───────────────────┘
                                      │ (implemented by)
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
┌─────────▼─────────┐     ┌───────────▼───────────┐    ┌──────────▼──────────┐
│  SQLite Adapter   │     │  Redis Pub/Sub        │    │  Hardcoded          │
│  (User storage)   │     │  (Message broker)     │    │  Channel Adapter    │
└───────────────────┘     └───────────────────────┘    └─────────────────────┘
```

**Message Flow:**
1. Client sends message via WebSocket with JWT token
2. FastAPI validates token before accepting connection (SPIN-verified)
3. Message published to Redis pub/sub channel
4. Redis fans out to all subscribers on that channel
5. Each connected client receives the message in real-time

## Formal Verification with SPIN

The WebSocket authentication handshake was modeled in Promela and verified using the SPIN model checker. The verified property:

```
ltl { [] ( message_processed -> authenticated ) }
```

In plain English: **Always, if a message is processed, authentication has completed.**

This guarantees no message ever reaches processing logic before the WebSocket connection is fully authenticated, regardless of thread interleaving or concurrent execution paths. The guarantee holds at the port level and is therefore adapter-independent—swap SQLite for PostgreSQL or Redis for Kafka, and the property remains proven.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async web framework with native WebSocket support |
| **Redis Pub/Sub** | Lightweight message broker for real-time fan-out |
| **SQLite** | Embedded user storage, self-initializing on first run |
| **PyJWT + bcrypt** | Stateless authentication with password hashing |
| **SPIN Model Checker** | Formal verification of auth handshake safety |
| **Vanilla JS + CSS** | No frontend framework, minimal dependencies |

## Quick Start

### Prerequisites

- Python 3.9+
- Redis (any version 3.x or higher)

### Installing Redis on Windows

```powershell
# Option 1: Using WSL2 (recommended)
wsl --install
wsl
sudo apt update && sudo apt install redis-server
sudo service redis-server start

```

### Installing Redis on macOS

```bash
brew install redis
brew services start redis
```

### Installing Redis on Linux

```bash
sudo apt update && sudo apt install redis-server
sudo systemctl start redis
```

### Running the Application

```bash
# 1. Clone and enter directory
cd distributed-chat

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the backend
cd api
python main.py

# 6. In a new terminal, start the frontend
cd client
python -m http.server 3000

# 7. Open browser to http://localhost:3000
```

### Demo Users

| Username | Password |
|----------|----------|
| alice    | password123 |
| bob      | password123 |
| charlie  | password123 |

The SQLite database initializes automatically on first run with these three users.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Authenticate and receive JWT token |
| GET | `/channels/` | List all available channels |
| GET | `/channels/{name}` | Get channel details |
| WebSocket | `/ws/{channel}?token={jwt}` | Connect to channel (verified) |

## Project Structure

```
distributed-chat/
├── src/
│   ├── domain/          # Core entities (no dependencies)
│   │   ├── user.py
│   │   ├── message.py
│   │   ├── channel.py
│   │   └── auth_token.py
│   ├── ports/           # Abstract interfaces (ABCs)
│   │   ├── user_repository_port.py
│   │   ├── message_publisher_port.py
│   │   └── channel_repository_port.py
│   └── adapters/        # Concrete implementations
│       ├── sqlite_user_adapter.py
│       ├── redis_publisher_adapter.py
│       └── redis_channel_adapter.py
├── api/                 # FastAPI application layer
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── auth_router.py
│   ├── channel_router.py
│   ├── websocket_handler.py
│   └── auth_utils.py
├── client/              # Frontend (vanilla JS)
│   ├── index.html
│   ├── app.js
│   ├── auth.js
│   ├── chat.js
│   └── styles.css
├── spin/                # SPIN model files
│   └── auth_verification.pml
├── seed.py              # Database initializer
├── requirements.txt
└── README.md
```

## What's Not Here (And Why)

| Feature | Status | Reasoning |
|---------|--------|-----------|
| **Persistent message history** | Omitted | System is stateless by design; messages reset on restart for clean demos |
| **User registration** | Omitted | Hardcoded demo users simplify onboarding |
| **Horizontal scaling** | Not implemented | Single-node architecture sufficient for demo; design supports multi-node via port abstraction |
| **FAISS semantic search** | Removed | Original design included it; removed to eliminate external dependencies |

## What I'd Add With More Time

1. **Persistent message storage** — Add a message repository port with PostgreSQL adapter for history
2. **User registration flow** — Extend the user repository with create operations
3. **Horizontal scaling** — Multiple FastAPI workers sharing Redis pub/sub (already supported)
4. **Channel creation** — Dynamic channels beyond the hardcoded three
5. **Message reactions** — Emoji reactions as separate domain events
6. **End-to-end encryption** — Client-side encryption before publishing to Redis

## The Formal Verification Artifact

The SPIN model (`spin/auth_verification.pml`) models:

- WebSocket connection lifecycle
- JWT validation states
- Message processing after auth
- Concurrent connection attempts

To run the verification yourself (requires SPIN installed):

```bash
spin -a auth_verification.pml
gcc -o pan pan.c
./pan -a
```

