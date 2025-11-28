from bot.services import TelegramService, MailService, UserService
from bot.keyboards import get_main_menu, get_email_list_buttons, get_email_view_buttons
from bot.keyboards.inline import get_next_button
from bot.templates.messages import (
    format_email_full,
    format_email_list,
    NO_EMAILS_MESSAGE,
    NO_EMAILS_FOUND,
    EMAILS_FOUND,
    MAIN_MENU,
    AUTH_REQUIRED,
)
from .commands import awaiting_password

user_pages: dict[str, int] = {}


async def handle_callback(
    callback_data: str,
    callback_id: str,
    chat_id: str,
    tg: TelegramService,
    mail: MailService,
    email_queues: dict
) -> str:
    
    if not tg.is_allowed(chat_id):
        await tg.answer_callback(callback_id, "⛔ Нет доступа")
        return "OK"
    
    # Проверяем регистрацию
    user_service = UserService()
    if not user_service.is_registered(chat_id):
        awaiting_password[chat_id] = True
        await tg.answer_callback(callback_id, "🔐 Требуется авторизация")
        await tg.send_message(chat_id, AUTH_REQUIRED)
        return "OK"
    
    if callback_data == "check_mail":
        new_emails = mail.check_new_emails()
        if new_emails:
            for em in new_emails:
                formatted = format_email_full(em)
                await tg.send_email_with_attachments(chat_id, em, formatted)
            await tg.answer_callback(callback_id, EMAILS_FOUND.format(count=len(new_emails)))
        else:
            await tg.answer_callback(callback_id, NO_EMAILS_MESSAGE)
    
    # Открыть список писем (страница)
    elif callback_data.startswith("mail_"):
        page = int(callback_data.split("_")[1])
        user_pages[chat_id] = page
        
        emails, total, total_pages = mail.get_emails_page(page=page, per_page=10)
        
        if emails:
            text = format_email_list(emails, page, total_pages, total)
            await tg.send_message(
                chat_id,
                text,
                reply_markup=get_email_list_buttons(emails, page, total_pages)
            )
            await tg.answer_callback(callback_id)
        else:
            await tg.answer_callback(callback_id, NO_EMAILS_FOUND)
    
    # Открыть конкретное письмо по UID
    elif callback_data.startswith("email_"):
        uid = callback_data.split("_", 1)[1]
        email_data = mail.get_email_by_uid(uid)
        
        if email_data:
            formatted = format_email_full(email_data)
            current_page = user_pages.get(chat_id, 0)
            await tg.send_email_with_attachments(chat_id, email_data, formatted)
            await tg.send_message(
                chat_id,
                "👆 Письмо выше",
                reply_markup=get_email_view_buttons(current_page)
            )
            await tg.answer_callback(callback_id)
        else:
            await tg.answer_callback(callback_id, "❌ Письмо не найдено")
    
    elif callback_data == "menu":
        await tg.send_message(
            chat_id,
            MAIN_MENU,
            reply_markup=get_main_menu()
        )
        await tg.answer_callback(callback_id)
    
    elif callback_data == "next_email":
        if chat_id in email_queues and email_queues[chat_id]:
            em = email_queues[chat_id].popleft()
            remaining = len(email_queues[chat_id])
            
            formatted = format_email_full(em)
            await tg.send_message(
                chat_id,
                formatted,
                reply_markup=get_next_button(remaining) if remaining > 0 else None
            )
            await tg.answer_callback(callback_id)
        else:
            await tg.answer_callback(callback_id, NO_EMAILS_MESSAGE)
    
    elif callback_data == "noop":
        await tg.answer_callback(callback_id)
    
    return "OK"
