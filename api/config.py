# Configuration for the distributed chat system
# Hardcoded for demo purposes - change as needed

DATABASE_PATH = "chat.db"

JWT_SECRET = "dev-secret-do-not-use-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

REDIS_URL = "redis://localhost:6379"
