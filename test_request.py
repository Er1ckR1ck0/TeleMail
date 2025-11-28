import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ Не найдены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в .env")
    print("Добавь их в .env файл:")
    print("  TELEGRAM_BOT_TOKEN=ваш_токен")
    print("  TELEGRAM_CHAT_ID=ваш_chat_id")
    exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"


def test_simple_message():
    """Простое сообщение без клавиатуры"""
    print("1. Тест: простое сообщение")
    resp = httpx.post(f"{API_URL}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": "Тест 1: Простое сообщение ✅",
        "parse_mode": "HTML"
    })
    print(f"   Статус: {resp.status_code}")
    print(f"   Ответ: {resp.json()}\n")


def test_inline_keyboard():
    """Сообщение с inline клавиатурой"""
    print("2. Тест: inline клавиатура")
    resp = httpx.post(f"{API_URL}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": "Тест 2: Inline клавиатура 🔘",
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Кнопка 1", "callback_data": "test1"}],
                [{"text": "Кнопка 2", "callback_data": "test2"}]
            ]
        }
    })
    print(f"   Статус: {resp.status_code}")
    print(f"   Ответ: {resp.json()}\n")


def test_aiogram_markup():
    """Тест с aiogram разметкой (как в боте)"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    print("3. Тест: aiogram клавиатура")
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить", callback_data="check")],
        [InlineKeyboardButton(text="📬 Почта", callback_data="mail")]
    ])
    
    # Сериализуем с exclude_none=True (как исправлено в TelegramService)
    markup_dict = markup.model_dump(exclude_none=True)
    
    print(f"   Сериализованная клавиатура: {markup_dict}")
    
    resp = httpx.post(f"{API_URL}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": "Тест 3: aiogram клавиатура 🎹",
        "parse_mode": "HTML",
        "reply_markup": markup_dict
    })
    print(f"   Статус: {resp.status_code}")
    print(f"   Ответ: {resp.json()}\n")


def test_bot_info():
    """Получить инфо о боте"""
    print("0. Инфо о боте:")
    resp = httpx.get(f"{API_URL}/getMe")
    print(f"   {resp.json()}\n")


if __name__ == "__main__":
    print(f"TOKEN: {TOKEN[:20]}...")
    print(f"CHAT_ID: {CHAT_ID}\n")
    print("=" * 50)
    
    test_bot_info()
    test_simple_message()
    test_inline_keyboard()
    test_aiogram_markup()
    
    print("=" * 50)
    print("Готово!")
