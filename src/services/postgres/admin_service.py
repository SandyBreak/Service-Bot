# -*- coding: UTF-8 -*-

from typing import Union
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from services.postgres.database import get_async_session

from models.table_models.user import User

from exceptions.errors import EpmtyTableError


class AdminService:
    def __init__(self):
        pass
        
    
    @staticmethod
    async def get_table(table_name:str) -> Union[User]:
        """
        Получение данных из таблицы
        """
        async for session in get_async_session():
            try:
                match table_name:
                    case 'user':
                        result = await session.execute(select(User))
                        return_data = result.scalars().all()
                
                if return_data:
                    return return_data 
                else:
                    raise EpmtyTableError
                    
            except SQLAlchemyError as e:
                logging.error(f"Ошибка при получении данных из таблицы {table_name}: {e}")
                raise e
        
        
        
        