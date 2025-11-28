from abc import ABC, abstractmethod
from typing import List, Dict, Any
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,          # <- correct type for reply keyboards
    ReplyKeyboardMarkup,
    WebAppInfo,
)


class ButtonComponent(ABC):

    @abstractmethod
    def create_markup(self, buttons_data: List[Dict[str, Any]]) -> Any:
        pass


class InlineButtonComponent(ButtonComponent):

    def create_markup(self, buttons_data: List[Dict[str, Any]]) -> InlineKeyboardMarkup:

        buttons = []
        for button_info in buttons_data:
            row = []
            for button_dict in button_info:
                text = button_dict.get("text")
                callback_data = button_dict.get("callback_data") or button_dict.get("callback")
                url = button_dict.get("url")
                web_app = button_dict.get("web_app")
                
                if web_app:
                    # Web app button
                    if isinstance(web_app, str):
                        button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=web_app))
                    else:
                        button = InlineKeyboardButton(text=text, web_app=WebAppInfo(**web_app))
                elif url:
                    # Regular URL button
                    button = InlineKeyboardButton(text=text, url=url)
                elif callback_data:
                    # Callback button
                    button = InlineKeyboardButton(text=text, callback_data=callback_data)
                else:
                    # Fallback to text as callback
                    button = InlineKeyboardButton(text=text, callback_data=text)
                row.append(button)
            buttons.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class ReplyButtonComponent(ButtonComponent):

    def create_markup(self, buttons_data: List[Dict[str, Any]]) -> ReplyKeyboardMarkup:

        keyboard = []
        for button_info in buttons_data:
            row = []
            for button_dict in button_info:
                web_app_value = button_dict.get("web_app")
                if isinstance(web_app_value, str):
                    web_app_value = WebAppInfo(url=web_app_value)
                elif isinstance(web_app_value, dict):
                    web_app_value = WebAppInfo(**web_app_value)
                
                request_contact = button_dict.get("request_contact", False)
                request_location = button_dict.get("request_location", False)
                
                button = KeyboardButton(
                    text=button_dict["text"],
                    web_app=web_app_value,
                    request_contact=request_contact,
                    request_location=request_location,
                )
                row.append(button)
            keyboard.append(row)
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )


class ButtonFactory:    
    @staticmethod
    def create_button_component(button_type: str) -> ButtonComponent:

        if button_type.lower() == "inline":
            return InlineButtonComponent()
        elif button_type.lower() == "reply":
            return ReplyButtonComponent()
        else:
            raise ValueError(f"Неизвестный тип кнопки: {button_type}")


class ButtonFactoryExtended:
    
    _button_types = {
        "inline": InlineButtonComponent,
        "reply": ReplyButtonComponent
    }
    
    @classmethod
    def register_button_type(cls, type_name: str, component_class: type):
        cls._button_types[type_name] = component_class
    
    @classmethod
    def create_button_component(cls, button_type: str) -> ButtonComponent:
        component_class = cls._button_types.get(button_type.lower())
        if component_class:
            return component_class()
        else:
            raise ValueError(f"Неизвестный тип кнопки: {button_type}")
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        return list(cls._button_types.keys())
    
class ReplyButtonInterface:
    _component = ButtonFactory.create_button_component("reply")
    
    @classmethod
    def create_markup(cls, buttons_data: List[Dict[str, Any]]) -> ReplyKeyboardMarkup:
        return cls._component.create_markup(buttons_data)
    
    @classmethod
    def create_markup_dict(cls, buttons_data: List[Dict[str, Any]]) -> dict:
        markup = cls._component.create_markup(buttons_data)
        return markup.model_dump(exclude_none=True)
    
    
class InlineButtonInterface:
    _component = ButtonFactory.create_button_component("inline")
    
    @classmethod
    def create_markup(cls, buttons_data: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        return cls._component.create_markup(buttons_data)
    
    @classmethod
    def create_markup_dict(cls, buttons_data: List[Dict[str, Any]]) -> dict:
        markup = cls._component.create_markup(buttons_data)
        return markup.model_dump(exclude_none=True)



        

