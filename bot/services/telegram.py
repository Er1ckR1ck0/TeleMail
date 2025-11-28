import os
import httpx


class TelegramService:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    async def send_message(
        self, 
        chat_id: str | int, 
        text: str, 
        reply_markup: dict = None,
        parse_mode: str = "HTML"
    ) -> dict:
        max_length = 4000
        if len(text) > max_length:
            text = text[:max_length - 50] + "\n\n... (обрезано)"
        
        data = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.api_url}/sendMessage", json=data)
            return resp.json()
    
    async def answer_callback(self, callback_id: str, text: str = "") -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.api_url}/answerCallbackQuery",
                json={
                    "callback_query_id": callback_id,
                    "text": text
                }
            )
            return resp.json()
    
    async def send_document(
        self, 
        chat_id: str | int, 
        file_data: bytes, 
        filename: str, 
        caption: str = None
    ) -> dict:
        """Отправляет документ"""
        files = {"document": (filename, file_data, "application/octet-stream")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_url}/sendDocument",
                    data=data,
                    files=files
                )
                return resp.json()
        except Exception as e:
            print(f"Telegram sendDocument error: {e}")
            return None
    
    async def send_email_with_attachments(
        self, 
        chat_id: str | int, 
        email_data: dict,
        formatted_text: str
    ):
        await self.send_message(chat_id, formatted_text)
        
        for att in email_data.get("attachments", []):
            caption = f"📎 {att['filename']}"
            await self.send_document(chat_id, att["data"], att["filename"], caption)
    
    def get_allowed_chats(self) -> list:
        chat_ids = os.getenv("TELEGRAM_CHAT_ID", "")
        return [cid.strip() for cid in chat_ids.split(",") if cid.strip()]
    
    def is_allowed(self, chat_id: str | int) -> bool:
        return str(chat_id) in self.get_allowed_chats()
