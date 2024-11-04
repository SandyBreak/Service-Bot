# -*- coding: UTF-8 -*-

from typing import Optional, Tuple


class AdminOperations:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def parse_callback_data(data: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Получение данных из строки 

        Args:
            data (str): callback.data

        Returns:
            Tuple[str, Optional[str], Optional[str]]: callback.data parsed
        """
        if ',' in data:
            parts = data.split(',')
            action = parts[0]
            user_id = parts[1] if len(parts) > 1 else None
            user_tg_addr = ','.join(parts[2:]) if len(parts) > 2 else None
            return action, user_id, user_tg_addr
        else:
            return data, None, None