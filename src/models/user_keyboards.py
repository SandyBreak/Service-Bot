# -*- coding: UTF-8 -*-

from typing import Optional
import json 

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton

from models.emojis_chats import Emojis

from services.postgres.create_request_service import CreateRequestService
from services.postgres.group_service import GroupService


class UserKeyboards:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    async def phone_access_request() -> ReplyKeyboardBuilder:
        """
        Клавиатура для отправки телефона при регистрации
        """
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text=f"{Emojis.ARROW_LEFT} Вернуться назад"))# Кнопка для возврата назад
        builder.row(KeyboardButton(text="Отправить свой номер телефона", request_contact=True))
        
        return builder
    
    
    @staticmethod
    async def required_keyboard(user_id: int, type_keyboard: Optional[str] = None) -> InlineKeyboardBuilder:
        """
        Клавиатура для заполнения обязательной части
        """
        builder = InlineKeyboardBuilder()
        if type_keyboard != 'clinic_name':
            builder.row(InlineKeyboardButton(text=f"{Emojis.ARROW_LEFT} Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        if type_keyboard != 'description_problem':
            memory_button = await CreateRequestService.get_data(user_id, type_keyboard)
            if memory_button:
                builder.row(InlineKeyboardButton(text=f"{memory_button}", callback_data=json.dumps({'key': 'memory'})))
        
        return builder


    @staticmethod
    async def split_keyboard() -> InlineKeyboardBuilder:
        """
        Клавиатура для перехода между частями
        """
        builder = InlineKeyboardBuilder()
        
        builder.row(InlineKeyboardButton(text=f"{Emojis.ARROW_LEFT} Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        builder.row(InlineKeyboardButton(text=f"{Emojis.ARROW_RIGHT} Далее", callback_data=json.dumps({'key': 'next'})))
        builder.row(InlineKeyboardButton(text=f"{Emojis.SUCCESS} Отправить", callback_data=json.dumps({'key': 'send'})))
        
        return builder
    
    
    @staticmethod
    async def optional_keyboard(user_id: int, type_keyboard: Optional[str] = None) -> InlineKeyboardBuilder:
        """
        Клавиатура для заполнения необязательной части
        """
        builder = InlineKeyboardBuilder()
        
        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        
        if type_keyboard != 'detailed_description' and 'detailed_description_append' and 'nameplate' and 'maintenance_date':
            memory_button = await CreateRequestService.get_data(user_id, type_keyboard)
            if memory_button:
                builder.row(InlineKeyboardButton(text=f"{memory_button}", callback_data=json.dumps({'key': 'memory'})))
                
        if type_keyboard == 'detailed_description_append':
            builder.row(InlineKeyboardButton(text=f"{Emojis.ARROW_RIGHT} Далее", callback_data=json.dumps({'key': 'next'})))
        else:
            builder.row(InlineKeyboardButton(text=f"{Emojis.ARROW_RIGHT} Пропустить", callback_data=json.dumps({'key': 'skip'}))) 
        
        return builder
    
    
    @staticmethod
    async def group_activation_request(group_id: int, type_acces: Optional[bool] = None) -> InlineKeyboardBuilder:
        """
        Клавиатура управления группами
        """
        builder = InlineKeyboardBuilder()
        
        SECONDARY_GROUPS_IDS = await GroupService.get_group_id('secondary', type_acces)
        
        for secondary_group in SECONDARY_GROUPS_IDS:
            if secondary_group.group_id==group_id:
                if secondary_group.access_flag:
                    builder.row(InlineKeyboardButton(text=f"{Emojis.FAIL} Деактивировать группу", callback_data=json.dumps({'key': 'deny_access', 'value': group_id})))
                else:
                    builder.row(InlineKeyboardButton(text=f"{Emojis.SUCCESS} Активировать группу", callback_data=json.dumps({'key': 'allow_access', 'value': group_id})))
        
        return builder