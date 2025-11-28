import os
from datetime import datetime
from typing import Optional

from database.supabase import SupabaseSession


class UserService:
    ACCESS_PASSWORD = os.getenv("BOT_PASSWORD", "secret123")
    
    @classmethod
    def get_user(cls, user_id: int) -> Optional[dict]:
        return SupabaseSession.get_user(int(user_id))
    
    @classmethod
    def is_registered(cls, user_id: int) -> bool:
        user = cls.get_user(user_id)
        return user is not None and user.get("is_registered", False)
    
    @classmethod
    def check_password(cls, password: str) -> bool:
        return password.strip() == cls.ACCESS_PASSWORD
    
    @classmethod
    def register_user(
        cls, 
        user_id: int, 
        name: str,
        firstname: str = None,
        username: str = None
    ) -> dict:
        user = cls.get_user(user_id)
        
        if user:
            return SupabaseSession.update_user(int(user_id), {
                "is_registered": True,
                "name": name,
                "firstname": firstname,
                "username": username
            })
        else:
            return SupabaseSession.create_user({
                "user_id": int(user_id),
                "name": name,
                "firstname": firstname,
                "username": username,
                "is_registered": True,
                "created_at": datetime.utcnow().isoformat()
            })
    
    @classmethod
    def create_unregistered_user(
        cls,
        user_id: int,
        name: str,
        firstname: str = None,
        username: str = None
    ) -> dict:
        user = cls.get_user(user_id)
        
        if user:
            return user
        
        return SupabaseSession.create_user({
            "user_id": int(user_id),
            "name": name,
            "firstname": firstname,
            "username": username,
            "is_registered": False,
            "created_at": datetime.utcnow().isoformat()
        })
    
    @classmethod
    def get_all_users(cls) -> list[dict]:
        return SupabaseSession.get_registered_users()
