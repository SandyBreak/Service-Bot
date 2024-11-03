# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Optional
import logging

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.user import User

from services.postgres.database import get_async_session

from exceptions.errors import UserNotRegError, AccessDeniedError


class UserService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def check_user_exists(user_id: int) -> Optional[datetime]:
        """
        Проверка регистрации и получение даты регистрации.
        """
        async for session in get_async_session():
            try:
                user_data_query = await session.execute(select(User).where(User.id_tg == user_id))
                user_data = user_data_query.scalar()
                if user_data:
                    if user_data.date_reg:
                        if user_data.access_flag:
                            return user_data.date_reg
                        else:
                            raise AccessDeniedError
                    else:
                        raise UserNotRegError
                else:
                    raise UserNotRegError
            except SQLAlchemyError as e:
                logging.error(f"Ошибка проверки пользователя с id_tg {user_id}: {e}")
                raise e
    
    
    @staticmethod
    async def init_user(user_id: int, nickname: str, full_name: str) -> None:
        """
        Регистрация пользователя, сохранение:
            1. ID Аккаунта
            2. Адрес аккаунта
            3. Имя аккаунта
            4. ФИО
            5. Даты регистрации
        """
        async for session in get_async_session():
            try:
                user_exists_query = await session.execute(
                    select(func.count('*'))
                    .where(User.id_tg == user_id)
                )
                user_exists_flag = user_exists_query.scalar()
                
                if not user_exists_flag:
                    new_user = User(
                        id_tg=user_id,
                        nickname=f'@{nickname}',
                        fullname=full_name,
                        date_reg=datetime.now(),
                        access_flag=True
                    )

                    # Выполнение вставки
                    session.add(new_user)
                    await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка первичной регистрации пользователя с id_tg {user_id}: {e}")
    

    @staticmethod
    async def get_user_data(user_id: int) -> User:
        """
            Получение всех данных о пользователе

        Args:
            user_id (int): User telegram ID

        Returns:
            User: Данные о пользователе
        """
        async for session in get_async_session():
            try:
                get_user_data = await session.execute(select(User).where(User.id_tg == user_id))
                user_data = get_user_data.scalar()
                return user_data
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения данных пользователя с id_tg {user_id}: {e}")