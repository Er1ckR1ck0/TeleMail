import os
import asyncio
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn

from bot.services import TelegramService, MailService
from bot.handlers import handle_command, handle_callback, handle_text_message
from bot.keyboards import get_next_button
from bot.templates.messages import format_email_full

load_dotenv()

tg: TelegramService = None
mail: MailService = None
email_queues: dict = {}


async def notify_new_emails(chat_id: str, emails: list):
    global email_queues, tg
    
    if chat_id not in email_queues:
        email_queues[chat_id] = deque()
    
    for em in emails:
        email_queues[chat_id].append(em)
    
    queue = email_queues[chat_id]
    count = len(queue)
    
    if count == 1:
        em = queue.popleft()
        formatted = format_email_full(em)
        await tg.send_email_with_attachments(chat_id, em, formatted)
    elif count > 1:
        em = queue.popleft()
        remaining = len(queue)
        formatted = format_email_full(em)
        await tg.send_message(
            chat_id,
            formatted,
            reply_markup=get_next_button(remaining)
        )


async def mail_polling_loop():
    global mail, tg
    
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    interval = int(os.getenv("POLL_INTERVAL", 30))
    
    print(f"📧 Проверка почты каждые {interval} сек")
    
    while True:
        try:
            new_emails = mail.check_new_emails()
            if new_emails:
                print(f"📬 Новых писем: {len(new_emails)}")
                await notify_new_emails(chat_id, new_emails)
        except Exception as e:
            print(f"Ошибка: {e}")
        
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tg, mail
    
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if tg_token and chat_id:
        tg = TelegramService(tg_token)
        mail = MailService()
        
        asyncio.create_task(mail_polling_loop())
        
        print(f"🚀 Бот запущен")
        print(f"📧 Почта: {os.getenv('YANDEX_EMAIL')}")
        print(f"💬 Telegram chat: {chat_id}")
        print("-" * 40)
    
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request):
    global tg, mail, email_queues
    
    data = await request.json()
    
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


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok", "service": "mail-bot"}


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
