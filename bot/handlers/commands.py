from bot.services import TelegramService, MailService, UserService
from bot.keyboards import get_main_menu, get_email_list_buttons
from bot.templates.messages import (
    format_email_full,
    format_email_list,
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    NO_ACCESS_MESSAGE,
    NO_EMAILS_MESSAGE,
    NO_EMAILS_FOUND,
    EMAILS_SHOWN,
    QUEUE_STATUS,
    AUTH_REQUIRED,
    AUTH_SUCCESS,
    AUTH_FAILED,
)

# Состояния ожидания пароля
awaiting_password: dict[str, bool] = {}


async def handle_command(
    command: str,
    chat_id: str,
    tg: TelegramService,
    mail: MailService,
    email_queues: dict,
    user_data: dict = None
) -> str:
    """Обрабатывает команды бота"""
    
    if not tg.is_allowed(chat_id):
        await tg.send_message(
            chat_id, 
            NO_ACCESS_MESSAGE.format(chat_id=chat_id)
        )
        return "OK"
    
    # Проверяем регистрацию пользователя
    user_service = UserService()
    
    if not user_service.is_registered(chat_id):
        # Создаём пользователя если его нет
        ud = user_data or {}
        user_service.create_unregistered_user(
            chat_id,
            name=ud.get("name", "User"),
            firstname=ud.get("firstname"),
            username=ud.get("username")
        )
        # Запрашиваем пароль
        awaiting_password[chat_id] = True
        await tg.send_message(chat_id, AUTH_REQUIRED)
        return "OK"
    
    if command == "/start":
        await tg.send_message(
            chat_id,
            WELCOME_MESSAGE,
            reply_markup=get_main_menu()
        )
    
    elif command == "/check":
        new_emails = mail.check_new_emails()
        if new_emails:
            for em in new_emails:
                formatted = format_email_full(em)
                await tg.send_email_with_attachments(chat_id, em, formatted)
            await tg.send_message(
                chat_id,
                EMAILS_SHOWN.format(count=len(new_emails)),
                reply_markup=get_main_menu()
            )
        else:
            await tg.send_message(
                chat_id,
                NO_EMAILS_MESSAGE,
                reply_markup=get_main_menu()
            )
    
    elif command == "/mail":
        emails, total, total_pages = mail.get_emails_page(page=0, per_page=10)
        if emails:
            text = format_email_list(emails, 0, total_pages, total)
            await tg.send_message(
                chat_id,
                text,
                reply_markup=get_email_list_buttons(emails, 0, total_pages)
            )
        else:
            await tg.send_message(
                chat_id,
                NO_EMAILS_FOUND,
                reply_markup=get_main_menu()
            )
    
    elif command == "/queue":
        count = len(email_queues.get(chat_id, []))
        await tg.send_message(
            chat_id,
            QUEUE_STATUS.format(count=count)
        )
    
    elif command == "/help":
        await tg.send_message(
            chat_id,
            HELP_MESSAGE,
            reply_markup=get_main_menu()
        )
    
    return "OK"


async def handle_text_message(
    text: str,
    chat_id: str,
    tg: TelegramService,
    user_data: dict = None
) -> str:
    """Обрабатывает текстовые сообщения (включая ввод пароля)"""
    
    if not tg.is_allowed(chat_id):
        return "OK"
    
    # Если пользователь вводит пароль
    if awaiting_password.get(chat_id):
        user_service = UserService()
        
        if user_service.check_password(text):
            # Пароль верный - регистрируем
            user_data = user_data or {}
            user_service.register_user(
                chat_id,
                name=user_data.get("name", "User"),
                firstname=user_data.get("firstname"),
                username=user_data.get("username")
            )
            awaiting_password.pop(chat_id, None)
            await tg.send_message(
                chat_id,
                AUTH_SUCCESS,
                reply_markup=get_main_menu()
            )
        else:
            # Неверный пароль
            await tg.send_message(chat_id, AUTH_FAILED)
        
        return "OK"
    
    return "OK"
