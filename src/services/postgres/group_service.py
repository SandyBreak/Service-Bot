# -*- coding: UTF-8 -*-

from typing import Optional
import logging

from sqlalchemy import delete, select

from services.postgres.database import get_async_session

from models.table_models.admin_group import AdminGroup


class GroupService:
    def __init__(self):
        pass


    @staticmethod
    async def group_init(id_group: int) -> None:
        """
            Идентификация группы в которую добавлен бот и сохранение ее ID
        
        Args:
            id_group (int): Telegram Group ID
        """
        try:
            async for session in get_async_session():
                session.add(AdminGroup(group_id=id_group))
                await session.commit()
        except Exception as e:
            logging.error(f"Ошибка идентификации группы: {e}")
    
    
    @staticmethod
    async def group_reset() -> None:
        """
        Удаление ID группы при удалении бота из групыы
        """
        try:
            async for session in get_async_session():
                await session.execute(
                    delete(AdminGroup)
                )
                await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Ошибка сброса группы: {e}")
    
    
    @staticmethod
    async def get_group_id() -> Optional[str]:
        """
        Получение ID группы
        """
        try:
            async for session in get_async_session():
                get_group_id = await session.execute(
                    select(AdminGroup.group_id)
                )
                
                return get_group_id.scalar()
        except Exception as e:
            logging.error(f"Ошибка получения ID группы: {e}")