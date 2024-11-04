# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Union
import logging

from sqlalchemy import select, func, update, insert
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.temporary_requests_data import TemporaryRequestData
from models.table_models.created_requests import CreatedRequests
from models.table_models.user import User

from services.postgres.database import get_async_session


class CreateRequestService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def init_new_request(user_id: int) -> None:
        """
        Создание новой записи с данными о заявке
        """
        async for session in get_async_session():
            try:
                request_exist_query = await session.execute(
                    select(func.count('*'))
                    .where(TemporaryRequestData.id_tg == user_id)
                )
                if not(request_exist_query.scalar()):
                    new_request = TemporaryRequestData(
                        id_tg=user_id
                    )
                    session.add(new_request)
                    await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка инициализации новой заявки пользователя с id_tg {user_id}: {e}")


    @staticmethod
    async def save_created_request(user_id: int) -> None:
        """
        Добавдение записи о созданной заявке
        """
        async for session in get_async_session():
            try:
                get_user_id = await session.execute(
                    select(User.id)
                    .where(User.id_tg == user_id)
                )
                creator_id = get_user_id.scalar()
                get_request_data = await session.execute(
                    select(TemporaryRequestData)
                    .where(TemporaryRequestData.id_tg == user_id)
                )
                request_data = get_request_data.scalars().all()[0]
                await session.execute(
                    insert(CreatedRequests)
                    .values(
                        creator_id=creator_id,
                        date_creation=datetime.now(),
                        clinic_name=request_data.clinic_name,
                        city=request_data.city,
                        apparat_name=request_data.apparat_name,
                        description_problem=request_data.description_problem,
                        phone_number=request_data.phone_number,
                        mediafiles=request_data.mediafiles,
                        company_details=request_data.company_details,
                        location=request_data.location,
                        maintenance_date=request_data.maintenance_date
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения созданной заявки пользователя с id_tg {user_id}: {e}")
    
    
    @staticmethod
    async def delete_temporary_data(user_id: int) -> None:
        """
        Очистка данных которые меняются для каждой заявки
        """
        async for session in get_async_session():
            try:
                await session.execute(
                    update(TemporaryRequestData)
                    .where(TemporaryRequestData.id_tg == user_id)
                    .values(
                        {
                            TemporaryRequestData.apparat_name: None,
                            TemporaryRequestData.description_problem: None,
                            TemporaryRequestData.mediafiles: {"photo": [], "video": []},
                            TemporaryRequestData.maintenance_date: None
                        }
                    )
                )
                
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка удаления данных о создаваемой заявки пользователя с id_tg {user_id}: {e}")
            
            
    @staticmethod
    async def get_data(user_id: int, type_data: str) -> Union[int, str, dict, TemporaryRequestData]:
        """
        Получение данных о создаваемой заявке
        """
        async for session in get_async_session():
            try:
                get_temporary_data = await session.execute(
                    select(TemporaryRequestData)
                    .where(TemporaryRequestData.id_tg == user_id)
                )
                temporary_data = get_temporary_data.scalars().all()
                if type_data == 'all':
                    return temporary_data[0]

                data_mapping = {
                    'clinic_name': temporary_data[0].clinic_name,
                    'city': temporary_data[0].city,
                    'apparat_name': temporary_data[0].apparat_name,
                    'phone_number': temporary_data[0].phone_number,
                    'description_problem': temporary_data[0].description_problem,
                    'mediafiles': temporary_data[0].mediafiles,
                    'company_details': temporary_data[0].company_details,
                    'location': temporary_data[0].location,
                    'maintenance_date': temporary_data[0].maintenance_date,
                }
                
                return data_mapping.get(type_data)
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения '{type_data}': {e}")
    
    
    @staticmethod
    async def save_data(user_id: int, type_data: str, insert_value: Union[str, dict, list]) -> None:
        """
        Сохранение данных о создаваемой заявке
        """
        async for session in get_async_session():
            try:
                await session.execute(
                    update(TemporaryRequestData)
                    .where(TemporaryRequestData.id_tg == user_id)
                    .values(
                        {
                            type_data: insert_value
                        }
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения '{type_data}': {e}")
