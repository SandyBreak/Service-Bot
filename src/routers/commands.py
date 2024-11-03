# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot, suppress
from aiogram.filters import Command

from models.long_messages import HELP_MESSAGE, MENU_MESSAGE

router = Router()

@router.message(Command('cancel'))
async def bot_menu_and_start_message(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await message.answer(MENU_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.clear()

    
@router.message(Command('help'))
async def bot_help(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await  message.answer(HELP_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.clear()