# -*- coding: UTF-8 -*-

import logging
import json

from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.types import Message, CallbackQuery
from aiogram import Router, Bot

from models.user_keyboards import UserKeyboards

from services.postgres.group_service import GroupService

from models.emojis_chats import Emojis

router = Router()
    
@router.my_chat_member()
async def my_chat_member_handler(message: Message, bot: Bot):
    if message.new_chat_member.status == ChatMemberStatus.MEMBER:
        member = message.new_chat_member
        if member.user.id == bot.id and message.from_user.id == 5890864355:  # Проверяем, добавлен ли бот
            await message.answer('Спасибо за добавление меня в группу! Для моей правильной работы назначьте меня администратором!')
            
            if message.chat.id != message.from_user.id:
                await GroupService.group_init(message.chat.id, 'primary')
            
            logging.warning(f'Bot was added in legal group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
        
        elif message.from_user.id != 5890864355:
            await GroupService.group_init(message.chat.id, 'secondary')
            
            if PRIMARY_GROUP_ID := await GroupService.get_group_id('primary'):
                access_keyboard= await UserKeyboards.group_activation_request(message.chat.id, False)
                await bot.send_message(chat_id=PRIMARY_GROUP_ID, text=f'{Emojis.ALLERT} Бот был добавлен в группу без разрешения!\nCHAT_ID: {message.chat.id}\nID: {message.from_user.id}\nАдрес: @{message.from_user.username}', reply_markup=access_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
            
            logging.warning(f'Bot was added in illegal group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
            
            await message.answer('Спасибо за добавление меня в группу! Для моей правильной работы назначьте меня администратором!')
    if message.new_chat_member.status == ChatMemberStatus.LEFT:
            logging.critical(f'Bot was kikked from group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, remover_addr: {message.from_user.username}')
            await GroupService.group_reset(message.chat.id)
    elif message.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        await message.answer('Теперь я администратор!')


@router.callback_query(lambda F: 'allow_access' in F.data or 'deny_access' in F.data)
async def access_request_processing(callback: CallbackQuery, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'allow_access':
        await GroupService.set_group_access_flag(data['value'], True)    
        await bot.send_message(chat_id=data['value'], text=f'{Emojis.SUCCESS} Группа активирована! {Emojis.SUCCESS}\n\n Теперь в нее будут приходить мои уведомления.')
        access_keyboard= await UserKeyboards.group_activation_request(data['value'], True)
    elif data['key'] == 'deny_access':
        await GroupService.set_group_access_flag(data['value'], False)
        await bot.send_message(chat_id=data['value'], text=f'{Emojis.ALLERT} Группа деактивирована! {Emojis.ALLERT} В нее не будут приходить мои уведомления.')
        access_keyboard= await UserKeyboards.group_activation_request(data['value'], False)
    
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=access_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    await callback.answer()
    