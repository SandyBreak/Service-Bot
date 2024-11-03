# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup


class CreateRequestStates(StatesGroup):
    """
    Состояния для создания новой конференции
    """
    #Обязательные поля
    get_clinic_name = State()
    get_city = State()
    get_apparat_name = State()
    get_description_problem = State()
    get_contact = State()
    
    get_user_choice = State()
    
    #Второстепенные поля
    get_detailed_description_mediafiles = State()
    get_company_details = State()
    get_location = State()
    get_nameplate = State()
    get_maintenance_date_and_send_request = State()