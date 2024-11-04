# -*- coding: UTF-8 -*-

import logging
import json

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram import Router, F, Bot, suppress
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from admin.admin_logs import send_log_message

from services.postgres.create_request_service import CreateRequestService
from services.postgres.group_service import GroupService
from services.postgres.user_service import UserService

from models.user_keyboards import  UserKeyboards
from models.states import CreateRequestStates
from models.emojis_chats import Emojis

from utils.assistant import MinorOperations

from exceptions.errors import UserNotRegError, AccessDeniedError


router = Router()


@router.message(Command(commands=['create', 'reset']))
async def start_create_new_meeting(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Инициализация пользователя
    """
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    if message.chat.id == message.from_user.id:
        try:
            await UserService.check_user_exists(message.from_user.id)
        except UserNotRegError:
            PRIMARY_GROUP_ID = await GroupService.get_group_id('primary')

            await UserService.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

            new_topic = await bot.create_forum_topic(chat_id=PRIMARY_GROUP_ID, name=message.from_user.full_name)
            await GroupService.save_user_message_thread_id(message.from_user.id, new_topic.message_thread_id)

            user_data = await UserService.get_user_data(message.from_user.id)

            new_user_message = await bot.send_message(chat_id=PRIMARY_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nТелеграмм имя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}\nID темы: {new_topic.message_thread_id}', reply_to_message_id=new_topic.message_thread_id)
            await bot.pin_chat_message(chat_id=PRIMARY_GROUP_ID, message_id=new_user_message.message_id)

        except AccessDeniedError:
            delete_message = await message.answer(f"{Emojis.FAIL} Вы заблокированы администратором! {Emojis.FAIL}\nЕсли вы не совершали противоправных действий, обратитесь в @global_aide_bot")
            return
        
        await CreateRequestService.init_new_request(message.from_user.id)
        await CreateRequestService.delete_temporary_data(message.from_user.id)

        clinic_name_keyboard = await UserKeyboards.required_keyboard(message.from_user.id, 'clinic_name')
        delete_message = await message.answer(f"Введите название вашей клинники:", reply_markup=clinic_name_keyboard.as_markup(resize_keyboard=True))

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateRequestStates.get_clinic_name)
    



@router.callback_query(F.data, StateFilter(CreateRequestStates.get_clinic_name))    
async def get_clinic_name(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'memory':
        city_keyboard = await UserKeyboards.required_keyboard(callback.from_user.id, 'city')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите город в котором вы находитесь:", reply_markup=city_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateRequestStates.get_city)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_clinic_name))
async def get_clinic_name(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'clinic_name', message.text)

    city_keyboard = await UserKeyboards.required_keyboard(message.from_user.id, 'city')
    delete_message = await message.answer(f"Введите город в котором вы находитесь:", reply_markup=city_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_city)




@router.callback_query(F.data, StateFilter(CreateRequestStates.get_city))    
async def get_city(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        keyboard_type = 'clinic_name'
        text = "Введите название вашей клинники:"
        next_state = CreateRequestStates.get_clinic_name
        
    elif data['key'] == 'memory':
        keyboard_type = 'apparat_name'
        text = "Введите имя аппарата:"
        next_state = CreateRequestStates.get_apparat_name
    
    keyboard = await UserKeyboards.required_keyboard(callback.from_user.id, keyboard_type)
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_city))
async def get_city(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'city', message.text)

    apparat_name_keyboard = await UserKeyboards.required_keyboard(message.from_user.id, 'apparat_name')
    delete_message = await message.answer(f"Введите имя аппарата:", reply_markup=apparat_name_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_apparat_name)
    



@router.callback_query(F.data, StateFilter(CreateRequestStates.get_apparat_name))    
async def get_apparat_name(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        keyboard_type = 'city'
        text = 'Введите город в котором вы находитесь:'
        next_state = CreateRequestStates.get_city
        
    elif data['key'] == 'memory':
        keyboard_type = 'description_problem'
        text = 'Опишите вашу проблему:'
        next_state = CreateRequestStates.get_description_problem

    keyboard = await UserKeyboards.required_keyboard(callback.from_user.id, keyboard_type)
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_apparat_name))
async def get_apparat_name(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'apparat_name', message.text)

    description_keyboard = await UserKeyboards.required_keyboard(message.from_user.id, 'description_problem')
    delete_message = await message.answer("Опишите вашу проблему:", reply_markup=description_keyboard.as_markup(resize_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_description_problem)
    



@router.callback_query(F.data, StateFilter(CreateRequestStates.get_description_problem))    
async def get_description_problem(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        apparat_name_keyboard = await UserKeyboards.required_keyboard(callback.from_user.id, 'apparat_name')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите имя аппарата:", reply_markup=apparat_name_keyboard.as_markup(resize_keyboard=True))
        
        next_state = CreateRequestStates.get_apparat_name

    elif data['key'] == 'memory':
        with suppress(TelegramBadRequest):
            if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        
        phone_access_request_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await callback.message.answer("Отправьте свой номер телефона нажав на кнопку ниже или введя его вручную", reply_markup=phone_access_request_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        next_state = CreateRequestStates.get_contact
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_description_problem))
async def get_description_problem(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'description_problem', message.text)

    phone_access_request_keyboard = await UserKeyboards.phone_access_request()
    delete_message = await message.answer("Отправьте свой номер телефона нажав на кнопку ниже или введя его вручную", reply_markup=phone_access_request_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_contact)
    
        
        
        
@router.message(F.text | F.contact, StateFilter(CreateRequestStates.get_contact))
async def get_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)

    if message.text == f'{Emojis.ARROW_LEFT} Вернуться назад':
        description_keyboard = await UserKeyboards.required_keyboard(message.from_user.id, 'description_problem')
        delete_message = await message.answer("Опишите вашу проблему:", reply_markup=description_keyboard.as_markup(resize_keyboard=True))
        next_state = CreateRequestStates.get_description_problem
    else:
        if message.contact:
            contact = message.contact.phone_number
        else:
            contact = message.text
        await CreateRequestService.save_data(message.from_user.id, 'phone_number', contact)
        
        split_keyboard  = await UserKeyboards.split_keyboard()
        delete_message = await message.answer(f'Вы заполнили все обязательные данные для отправки заявки. Для заполнения дополнительных полей, таких как:\n\n1. Прикрепление фото и/или видео проблемы\n2. Реквизиты предприятия с ИНН\n3. Адрес вашего местонахождения\n4. Фото шильдика  аппарата\n5. Дата последнего  ТО аппарата\n\nНажмите кнопку {Emojis.ARROW_RIGHT} Далее. \nЕсли вы хотите отправить заявку без заполнения дополнительных данных нажмите кнопку {Emojis.SUCCESS} Отправить', reply_markup=split_keyboard.as_markup(resize_keyboard=True), parse_mode=ParseMode.HTML)
        next_state = CreateRequestStates.get_user_choice
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)




@router.callback_query(F.data, StateFilter(CreateRequestStates.get_user_choice))
async def get_user_choice(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        with suppress(TelegramBadRequest):
            if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)

        phone_access_request_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await callback.message.answer("Отправьте свой номер телефона нажав на кнопку ниже или введя его вручную:", reply_markup=phone_access_request_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateRequestStates.get_contact)
    elif data['key'] == 'send':
        try:
            request_message, request_media = await MinorOperations.build_request(callback.from_user.id, 'short')
            
            SECONDARY_GROUPS_IDS = await GroupService.get_group_id('secondary', True)

            for secondary_group in SECONDARY_GROUPS_IDS:
                request_message_reply = await bot.send_message(chat_id=secondary_group.group_id, text=request_message, parse_mode=ParseMode.HTML)

            if request_message_reply: await send_log_message(callback, bot, request_message_reply)
            
            delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.SUCCESS}Ваша заявка упешно отправлена! {Emojis.SUCCESS}\nСкоро с вами свяжется технический специалист.")
            await CreateRequestService.save_created_request(callback.from_user.id)
        except Exception as e:
            logging.error(f"Ошибка отправки заявки типа 1: {e}")
            log_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.FAIL} Что-то пошло не так и ваша заявка не отправлена! {Emojis.FAIL}")
            if log_message: await send_log_message(callback, bot, log_message)
            
        await state.clear()
    elif data['key'] == 'next':
        detailed_description_keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, 'detailed_description')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Отправьте фото или видео проблемы, если у вас несколько фото или видео, отправьте их по очереди", reply_markup=detailed_description_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(CreateRequestStates.get_detailed_description_mediafiles)




@router.callback_query(F.data, StateFilter(CreateRequestStates.get_detailed_description_mediafiles))    
async def get_detailed_description_mediafiles(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        keyboard  = await UserKeyboards.split_keyboard()
        text = f'Вы заполнили все обязательные данные для отправки заявки. Для заполнения дополнительных полей, таких как:\n\n1. Прикрепление фото и/или видео проблемы\n2. Реквизиты предприятия с ИНН\n3. Адрес вашего местонахождения\n4. Фото шильдика  аппарата\n5. Дата последнего  ТО аппарата\n\nНажмите кнопку {Emojis.ARROW_RIGHT} Далее. \nЕсли вы хотите отправить заявку без заполнения дополнительных данных нажмите кнопку {Emojis.SUCCESS} Отправить'
        await CreateRequestService.save_data(callback.from_user.id, 'mediafiles', {"photo": [], "video": []})
        next_state = CreateRequestStates.get_user_choice
        
    elif data['key'] == 'skip' or 'next':
        keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, 'company_details')
        text = 'Введите реквизиты предприятия включая ИНН:'
        next_state = CreateRequestStates.get_company_details
        
        if data['key'] == 'skip':
            await CreateRequestService.save_data(callback.from_user.id, 'mediafiles', {"photo": [], "video": []})
    
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True), parse_mode=ParseMode.HTML)

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)

@router.message(F.photo | F.video, StateFilter(CreateRequestStates.get_detailed_description_mediafiles))
async def get_detailed_description_mediafiles(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest): 
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        
    if message.photo:
        type_media = 'photo'
        file = await bot.get_file(message.photo[-1].file_id)
    elif message.video:
        type_media = 'video'
        file = await bot.get_file(message.video.file_id)
    
    quantity_media = await CreateRequestService.get_data(message.from_user.id, 'mediafiles')
    
    if (len(quantity_media['photo']) + len(quantity_media['video'])) < 9:
        file_path = file.file_path
        downloaded_photo = await bot.download_file(file_path)
        path_table = await MinorOperations.save_mediafile(message.from_user.id, type_media, downloaded_photo)
        
        quantity_media[type_media].append(path_table)
        
        await CreateRequestService.save_data(message.from_user.id, 'mediafiles', quantity_media)
        
        company_details_keyboard = await UserKeyboards.optional_keyboard(message.from_user.id, 'detailed_description_append')
        quantity_photo = len(quantity_media['photo'])
        quantity_video = len(quantity_media['video'])
        delete_message = await message.answer(f"Прикреплено фото: {quantity_photo} шт.\nПрикреплено видео: {quantity_video} шт.\nВсего файлов: {quantity_photo + quantity_video} из возможных 9 шт.", reply_markup=company_details_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    else:
        company_details_keyboard = await UserKeyboards.optional_keyboard(message.from_user.id, 'company_details')
        delete_message = await message.answer(f"{Emojis.ALLERT} Вы прикрепили максимум файлов! {Emojis.ALLERT}\nВведите реквизиты предприятия включая ИНН:", reply_markup=company_details_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)




@router.callback_query(F.data, StateFilter(CreateRequestStates.get_company_details))    
async def get_company_details(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        type_keyboard  = 'detailed_description'
        
        quantity_media = await CreateRequestService.get_data(callback.from_user.id, 'mediafiles')
        quantity_photo = len(quantity_media['photo'])
        quantity_video = len(quantity_media['video'])
        
        text = f'Отправьте фото или видео проблемы, если у вас несколько фото или видео, отправьте их по очереди.\n\nПрикреплено фото: {quantity_photo} шт.\nПрикреплено видео: {quantity_video} шт.\nВсего файлов: {quantity_photo + quantity_video} из возможных 9 шт.\n\nДля сброса всех прикрепленных файлов нажмите кнопку {Emojis.ARROW_LEFT} Вернуться назад'
        next_state = CreateRequestStates.get_detailed_description_mediafiles

    elif data['key'] == 'skip' or 'memory':
        type_keyboard  = 'location'
        text = 'Введите адрес вашего местонахождения:'
        next_state = CreateRequestStates.get_location
        
        await CreateRequestService.save_data(callback.from_user.id, 'company_details', '')

    keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, type_keyboard)
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_company_details))
async def get_company_details(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'company_details', message.text)

    location_keyboard = await UserKeyboards.optional_keyboard(message.from_user.id, 'location')
    delete_message = await message.answer("Введите адрес вашего местонахождения:", reply_markup=location_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_location)
    
    
    
    
@router.callback_query(F.data, StateFilter(CreateRequestStates.get_location))    
async def get_location(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        type_keyboard  = 'company_details'
        text = 'Введите реквизиты предприятия включая ИНН:'
        next_state = CreateRequestStates.get_company_details

    elif data['key'] == 'skip' or 'memory':
        type_keyboard  = 'nameplate'
        text = 'Отправьте 1 фото шильдика аппарата:'
        next_state = CreateRequestStates.get_nameplate
        
        await CreateRequestService.save_data(callback.from_user.id, 'location', '')
        
    keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, type_keyboard)
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.text, StateFilter(CreateRequestStates.get_location))
async def get_location(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'location', message.text)

    nameplate_keyboard = await UserKeyboards.optional_keyboard(message.from_user.id, 'nameplate')
    delete_message = await message.answer("Отправьте 1 фото шильдика аппарата:", reply_markup=nameplate_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_nameplate)




@router.callback_query(F.data, StateFilter(CreateRequestStates.get_nameplate))    
async def get_nameplate(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        type_keyboard  = 'location'
        text = 'Введите адрес вашего местонахождения:'
        next_state = CreateRequestStates.get_location

    elif data['key'] == 'skip':
        type_keyboard  = 'maintenance_date'
        text = 'Введите дату последнего ТО аппарата:'
        next_state = CreateRequestStates.get_maintenance_date_and_send_request
        
    keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, type_keyboard)
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(next_state)
        
@router.message(F.photo, StateFilter(CreateRequestStates.get_nameplate))
async def get_nameplate(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    if message.photo:
        type_media = 'photo'
        file = await bot.get_file(message.photo[-1].file_id)
    quantity_media = await CreateRequestService.get_data(message.from_user.id, 'mediafiles')
    
    if (len(quantity_media['photo']) + len(quantity_media['video'])) < 9:
        file_path = file.file_path
        downloaded_photo = await bot.download_file(file_path)
        path_table = await MinorOperations.save_mediafile(message.from_user.id, type_media, downloaded_photo)
        
        quantity_media[type_media].append(path_table)
        
        await CreateRequestService.save_data(message.from_user.id, 'mediafiles', quantity_media)
    
    maintenance_date_keyboard = await UserKeyboards.optional_keyboard(message.from_user.id, 'maintenance_date')
    delete_message = await message.answer("Введите дату последнего ТО аппарата", reply_markup=maintenance_date_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(CreateRequestStates.get_maintenance_date_and_send_request)
    
    
    
    
@router.callback_query(F.data, StateFilter(CreateRequestStates.get_maintenance_date_and_send_request))    
async def get_maintenance_date_and_send_request(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    
    if data['key'] == 'back':
        nameplate_keyboard = await UserKeyboards.optional_keyboard(callback.from_user.id, 'nameplate')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Отправьте 1 фото шильдика аппарата", reply_markup=nameplate_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateRequestStates.get_nameplate)
    
    elif data['key'] == 'skip':
        await CreateRequestService.save_data(callback.from_user.id, 'maintenance_date', '')
        try:
            request_message, request_media = await MinorOperations.build_request(callback.from_user.id, 'long')
            SECONDARY_GROUPS_IDS = await GroupService.get_group_id('secondary', True)

            for secondary_group in SECONDARY_GROUPS_IDS:
                request_message_reply = await bot.send_message(chat_id=secondary_group.group_id, text=request_message, parse_mode=ParseMode.HTML)
                request_media_group = await bot.send_media_group(chat_id=secondary_group.group_id, media=request_media, reply_to_message_id=request_message_reply.message_id)
        
            delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.SUCCESS}Ваша заявка упешно отправлена! {Emojis.SUCCESS}\nСкоро с вами свяжется технический специалист.")
            
            if request_message_reply: await send_log_message(callback, bot, request_message_reply)
            if request_media_group: await send_log_message(callback, bot, request_media_group[0])
            
            await state.clear()
        except Exception as e:
            logging.error(f"Ошибка отправки callback заявки 2: {e}")
            log_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.FAIL} Что-то пошло не так и ваша заявка не отправлена! {Emojis.FAIL}")
            if log_message: await send_log_message(callback, bot, log_message)
            await state.clear()
            
@router.message(F.text, StateFilter(CreateRequestStates.get_maintenance_date_and_send_request))
async def get_maintenance_date_and_send_request(message: Message, state: FSMContext, bot: Bot) -> None:
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    
    await CreateRequestService.save_data(message.from_user.id, 'maintenance_date', message.text)
    
    try:
        request_message, request_media = await MinorOperations.build_request(message.from_user.id, 'long')

        SECONDARY_GROUPS_IDS = await GroupService.get_group_id('secondary', True)

        for secondary_group in SECONDARY_GROUPS_IDS:
            request_message_reply = await bot.send_message(chat_id=secondary_group.group_id, text=request_message, parse_mode=ParseMode.HTML)
            request_media_group = await bot.send_media_group(chat_id=secondary_group.group_id, media=request_media, reply_to_message_id=request_message_reply.message_id)
        
        if request_message_reply: await send_log_message(message, bot, request_message_reply)
        if request_media_group: await send_log_message(message, bot, request_media_group[0])
        
        delete_message = await message.answer(f"{Emojis.SUCCESS}Ваша заявка упешно отправлена! {Emojis.SUCCESS}\nСкоро с вами свяжется технический специалист.")
    except Exception as e:
        logging.error(f"Ошибка отправки заявки типа 2: {e}")
        log_message = await message.answer(f"{Emojis.FAIL} Что-то пошло не так и ваша заявка не отправлена! {Emojis.FAIL}")
        if log_message: await send_log_message(message, bot, log_message)
    
    await state.clear()