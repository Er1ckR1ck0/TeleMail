import requests
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
print("=== Последние сообщения ===")
data = response.json()
if data.get("result"):
    for update in data["result"][-5:]:
        if "message" in update:
            msg = update["message"]
            print(f"Chat ID: {msg['chat']['id']}, From: {msg['from'].get('username', 'N/A')}, Text: {msg.get('text', '')}")
else:
    print("Нет сообщений. Напиши боту /start и запусти снова.")