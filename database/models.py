
from typing import List, Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(primary_key=True)
    name: str
    firstname: str | None = Field(default=None)
    username: str | None = Field(default=None, index=True)
    is_registered: bool = Field(default=False)
    phone: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

__all__ = ["User"]
