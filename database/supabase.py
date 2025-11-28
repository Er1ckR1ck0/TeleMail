import os
from supabase import create_client, Client
from typing import Optional


class SupabaseClient:
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            
            cls._client = create_client(url, key)
        
        return cls._client
    
    @classmethod
    def table(cls, name: str):
        return cls.get_client().table(name)


class SupabaseSession:
    @classmethod
    def get_user(cls, user_id: int) -> Optional[dict]:
        response = SupabaseClient.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    def create_user(cls, user_data: dict) -> dict:
        response = SupabaseClient.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    def update_user(cls, user_id: int, data: dict) -> dict:
        response = SupabaseClient.table("users").update(data).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    def get_registered_users(cls) -> list[dict]:
        response = SupabaseClient.table("users").select("*").eq("is_registered", True).execute()
        return response.data
    
    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        response = SupabaseClient.table("users").delete().eq("user_id", user_id).execute()
        return len(response.data) > 0
