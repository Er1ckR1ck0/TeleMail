import os

from fastapi import FastAPI, Request, Header, HTTPException

from bot.services import TelegramService, MailService
from bot.handlers import handle_command, handle_callback, handle_text_message
from bot.keyboards import get_main_menu
from bot.templates.messages import format_email_full

app = FastAPI()


def get_services():
    return TelegramService(), MailService()


async def send_email_with_attachments(tg: TelegramService, chat_id: str, email_data: dict):
    formatted = format_email_full(email_data)
    await tg.send_email_with_attachments(chat_id, email_data, formatted)


async def handle_cron():
    tg, mail = get_services()
    allowed_chats = tg.get_allowed_chats()
    
    if not tg.token or not allowed_chats:
        return {"error": "Not configured"}
    
    new_emails = mail.get_all_emails(limit=10)
    
    if not new_emails:
        return {"status": "no new emails"}
    
    for chat_id in allowed_chats:
        for em in new_emails:
            await send_email_with_attachments(tg, chat_id, em)
        
        await tg.send_message(
            chat_id,
            f"📬 Новых писем: {len(new_emails)}",
            reply_markup=get_main_menu()
        )
    
    return {"status": "ok", "emails_sent": len(new_emails), "users": len(allowed_chats)}


async def handle_webhook(data: dict):
    tg, mail = get_services()
    email_queues = {}
    
    if not tg.token:
        return {"error": "Bot not configured"}
    
    if "callback_query" in data:
        callback = data["callback_query"]
        callback_id = callback["id"]
        chat_id = str(callback["message"]["chat"]["id"])
        callback_data = callback["data"]
        
        return await handle_callback(
            callback_data, callback_id, chat_id,
            tg, mail, email_queues
        )
    
    if "message" in data:
        message = data["message"]
        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")
        
        user = message.get("from", {})
        user_data = {
            "firstname": user.get("first_name", ""),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "username": user.get("username", ""),
        }
        
        if text.startswith("/"):
            return await handle_command(text, chat_id, tg, mail, email_queues, user_data)
        
        return await handle_text_message(text, chat_id, tg, user_data)
    
    return "OK"


@app.get("/")
async def root():
    return {"status": "ok", "service": "mail-bot"}


@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    result = await handle_webhook(data)
    return result


@app.post("/cron")
async def cron(authorization: str = Header(None)):
    cron_secret = os.getenv("CRON_SECRET", "")
    
    if cron_secret and authorization != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await handle_cron()
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}
