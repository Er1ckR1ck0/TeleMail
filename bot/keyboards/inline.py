from bot.components import InlineButtonInterface


def get_main_menu() -> dict:
    return InlineButtonInterface.create_markup_dict([
        [{"text": "🔄 Проверить новые", "callback_data": "check_mail"}],
        [{"text": "📬 Открыть почту", "callback_data": "mail_0"}]
    ])


def get_email_list_buttons(emails: list, page: int, total_pages: int) -> dict:
    buttons = []
    
    row = []
    for i, em in enumerate(emails):
        num = page * 10 + i + 1
        row.append({"text": str(num), "callback_data": f"email_{em['uid']}"})
        
        if len(row) == 5:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    nav_row = []
    if page > 0:
        nav_row.append({"text": "⬅️", "callback_data": f"mail_{page - 1}"})
    
    nav_row.append({"text": f"{page + 1}/{total_pages}", "callback_data": "noop"})
    
    if page < total_pages - 1:
        nav_row.append({"text": "➡️", "callback_data": f"mail_{page + 1}"})
    
    buttons.append(nav_row)
    buttons.append([{"text": "🔄 Обновить", "callback_data": f"mail_{page}"}])
    
    return InlineButtonInterface.create_markup_dict(buttons)


def get_email_view_buttons(page: int) -> dict:
    return InlineButtonInterface.create_markup_dict([
        [{"text": "📋 К списку", "callback_data": f"mail_{page}"}],
        [{"text": "🏠 Меню", "callback_data": "menu"}]
    ])


def get_next_button(count: int) -> dict | None:
    if count > 0:
        return InlineButtonInterface.create_markup_dict([
            [{"text": f"📬 Следующее письмо ({count})", "callback_data": "next_email"}]
        ])
    return None
