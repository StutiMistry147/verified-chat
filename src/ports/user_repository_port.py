from abc import ABC, abstractmethod
from typing import Optional
from domain.user import User

class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int)-> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User)-> None:
        pass
