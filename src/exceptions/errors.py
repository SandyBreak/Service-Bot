# -*- coding: UTF-8 -*-

class EpmtyTableError(Exception):
    """
    Ошибка пустой таблицы при выгрузке данных
    """
    pass


class UserNotRegError(Exception):
    """
    Ошибка из-за того, что пользователь не зарегистиррован в боте
    """
    pass


class AccessDeniedError(Exception):
    """
    Ошибка отказано в доступе
    """
    pass