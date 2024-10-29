# -*- coding: UTF-8 -*-

import logging

from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.types import Message
from aiogram import Router, Bot

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
                await GroupService.group_init(message.chat.id)
            
            logging.warning(f'Bot was added in group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
        
        elif message.from_user.id != 5890864355:
            await bot.send_message(5890864355, text=f'{Emojis.ALLERT} Бот был добавлен в группу без разрешения!\nCHAT_ID: {message.chat.id}\nID: {message.from_user.id}\nАдрес: @{message.from_user.username}')
            await message.answer('У вас нету прав чтобы добавлять меня в эту группу, до свидания!')
            await bot.leave_chat(message.chat.id)
    if message.new_chat_member.status == ChatMemberStatus.LEFT:
        if message.from_user.id == bot.id:
            logging.critical(f'Bot was illegally added to the group!')
        else:
            logging.critical(f'Bot was kikked from group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
            await GroupService.group_reset()
    elif message.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        await message.answer('Теперь я администратор!')

           