def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_email_full(email_data: dict) -> str:
    body = email_data["body"]
    if len(body) > 2500:
        body = body[:2500] + "\n\n... (обрезано)"
    
    body = escape_html(body)
    subject = escape_html(email_data['subject'])
    sender = escape_html(email_data['sender'])
    
    attachments_info = ""
    if email_data.get("attachments"):
        attachments_info = f"\n\n📎 <b>Вложений:</b> {len(email_data['attachments'])}"
        for att in email_data["attachments"]:
            size_kb = att["size"] / 1024
            if size_kb > 1024:
                size_str = f"{size_kb/1024:.1f} МБ"
            else:
                size_str = f"{size_kb:.1f} КБ"
            att_name = escape_html(att["filename"])
            attachments_info += f"\n  • {att_name} ({size_str})"
    
    return f"""📧 <b>НОВОЕ ПИСЬМО</b>

📌 <b>Тема:</b> {subject}
👤 <b>От:</b> {sender}
📅 <b>Дата:</b> {email_data['date']}{attachments_info}

📝 <b>Содержимое:</b>
{body}"""


def format_email_short(email_data: dict) -> str:
    subject = escape_html(email_data['subject'])
    sender = escape_html(email_data['sender'])
    return f"📧 <b>{subject}</b>\n👤 {sender}"


def format_email_list(emails: list, page: int, total_pages: int, total_emails: int) -> str:
    if not emails:
        return "📭 Писем не найдено"
    
    lines = [f"📬 <b>Почта</b> (стр. {page + 1}/{total_pages}, всего: {total_emails})\n"]
    
    for i, em in enumerate(emails):
        num = page * 10 + i + 1
        subject = escape_html(em['subject'])
        if len(subject) > 40:
            subject = subject[:37] + "..."
        
        sender = em['sender']
        if '<' in sender:
            sender = sender.split('<')[0].strip().strip('"')
        sender = escape_html(sender)
        if len(sender) > 25:
            sender = sender[:22] + "..."
        
        att_icon = "📎" if em.get("attachments") else ""
        
        lines.append(f"<b>{num}.</b> {subject} {att_icon}\n    └ {sender}")
    
    lines.append("\n👆 Нажми на номер, чтобы открыть письмо")
    
    return "\n".join(lines)


WELCOME_MESSAGE = """👋 Привет! Я буду присылать тебе новые письма с Яндекс.Почты.

🔄 <b>/check</b> - проверить новые письма
📬 <b>/mail</b> - открыть почту"""

HELP_MESSAGE = """📋 <b>Команды:</b>

/check - проверить новые письма
/mail - открыть список писем
/help - помощь"""

AUTH_REQUIRED = "🔐 <b>Требуется авторизация</b>\n\nВведи пароль для доступа к боту:"
AUTH_SUCCESS = "✅ <b>Добро пожаловать!</b>\n\nТеперь у тебя есть доступ к почте."
AUTH_FAILED = "❌ <b>Неверный пароль</b>\n\nПопробуй ещё раз:"

NO_ACCESS_MESSAGE = "⛔ Нет доступа\n\nТвой Chat ID: <code>{chat_id}</code>"
NO_EMAILS_MESSAGE = "📭 Новых писем нет"
NO_EMAILS_FOUND = "📭 Писем не найдено"
EMAILS_FOUND = "📬 Найдено писем: {count}"
EMAILS_SHOWN = "✅ Показано писем: {count}"
QUEUE_STATUS = "📬 Писем в очереди: {count}"
MAIN_MENU = "📋 Главное меню"
USE_BUTTONS = "👆 Используй кнопки для навигации"
BACK_TO_LIST = "👆 Вернуться к списку"
