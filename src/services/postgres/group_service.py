# -*- coding: UTF-8 -*-

from typing import Union, Optional
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from services.postgres.database import get_async_session

from models.table_models.active_group import ActiveGroup
from models.table_models.user import User


class GroupService:
    def __init__(self):
        pass


    @staticmethod
    async def group_init(group_id: int, type_group: str) -> None:
        """
            Идентификация группы в которую добавлен бот и сохранение ее ID
        
        Args:
            id_group (int): Telegram Group ID
        """
        try:
            async for session in get_async_session():
                access_flag = (type_group == 'primary')
                session.add(
                    ActiveGroup(
                        group_id=group_id,
                        type_group=type_group,
                        access_flag=access_flag
                    )
                )
                await session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Ошибка идентификации группы: {e}")
    
    
    @staticmethod
    async def set_group_access_flag(group_id: int, access_flag: bool) -> None:
        """
        Активаци и деактивация группы
        """
        async for session in get_async_session():
            try:
                await session.execute(
                    update(ActiveGroup)
                    .where(ActiveGroup.group_id == group_id)
                    .values(access_flag=access_flag)
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"SET group error: {e} group_ID: {group_id} access_flag: {access_flag}")


    @staticmethod
    async def group_reset(group_id: int) -> None:
        """
        Удаление ID группы при удалении бота из групыы
        """
        try:
            async for session in get_async_session():
                await session.execute(
                    delete(ActiveGroup)
                    .where(ActiveGroup.group_id == group_id)
                )
                await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Ошибка сброса группы {group_id}: {e}")
    
    
    @staticmethod
    async def get_group_id(type_group: str, type_acces: Optional[bool] = None) -> Union[str, ActiveGroup]:
        """
        Получение ID группы
        """
        try:
            async for session in get_async_session():
                if type_group == 'primary':
                    get_primary_group_id = await session.execute(
                        select(ActiveGroup.group_id)
                        .where(ActiveGroup.type_group=='primary')
                    )
                    return get_primary_group_id.scalar()
                else:
                    get_secondary_groups_ids = await session.execute(
                        select(ActiveGroup)
                        .where(
                            ActiveGroup.type_group=='secondary',
                            ActiveGroup.access_flag==type_acces
                        )
                    )
                    return get_secondary_groups_ids.scalars()
        except SQLAlchemyError as e:
            logging.error(f"Ошибка получения {type_group} группы: {e}")
            
            
            
            
            
    @staticmethod
    async def get_user_message_thread_id(user_id: int) -> Optional[int]:
        """
        Получение id чата с пользователем в группе
        """
        try:
            async for session in get_async_session():
                get_user_message_thread_id = await session.execute(
                    select(User.message_thread_id)
                    .select_from(User)
                    .where(User.id_tg == user_id)
                )
                return get_user_message_thread_id.scalar()
        except Exception as e:
            logging.error(f"Ошибка получения id чата в группе для пользователя с id_tg {user_id}: {e}")

    
    @staticmethod
    async def save_user_message_thread_id(user_id: int, message_thread_id: int) -> None:
        """
        Сохрранение id чата с пользователем в группе
        """
        try:
            async for session in get_async_session():
                await session.execute(
                    update(User)
                    .where(User.id_tg==user_id)
                    .values(
                        message_thread_id=message_thread_id
                    )
                )
                await session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Ошибка сохранения id чата в группе для пользователя с id_tg {user_id}: {e}")
            
    
    @staticmethod
    async def get_user_id(message_thread_id: int) -> Optional[int]:
        """
        Получение user_id пользователя у которого id чата в группе равно message_thread_id
        """
        try:
            async for session in get_async_session():
                get_user_id_query = await session.execute(
                    select(User.id_tg)
                    .select_from(User)
                    .where(User.message_thread_id == message_thread_id)
                )
                return get_user_id_query.scalar()
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении id пользователя по message_thread_id: {e}")
    