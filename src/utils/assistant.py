# -*- coding: UTF-8 -*-

from datetime import datetime
import logging

from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo

from services.postgres.user_service import UserService
from services.postgres.create_request_service import CreateRequestService


class MinorOperations:
	def __init__(self):
		pass

	@staticmethod
	async def save_mediafile(user_id: int, type_media: str, downloaded_media) -> str:
		"""
        Сохранение фото
        """
		media_extension_map = {
            'video': 'mp4',
			'photo': 'jpg'
		}
		try:
			path_table = f'./downloads/{type_media}/problem_{type_media}{user_id}{datetime.now()}.{media_extension_map[type_media]}'
			with open(path_table, 'wb') as f:
				f.write(downloaded_media.read())
			return path_table
		except Exception as e:
			logging.error(f'Ошибка сохранения {type_media}: {e}')
   
   
	@staticmethod
	async def build_request(user_id: int, type_request: str) -> str:
		"""
		Формирование сообщения и медиагруппы с файлами для отправки
        """
		request_data = await CreateRequestService.get_data(user_id, 'all')
		user_data = await UserService.get_user_data(user_id)
		
		required_part = f"""
<b>Телеграм имя:</b> {user_data.fullname}
<b>Телеграмм адрес:</b> {user_data.nickname}
<b>Номер телефона:</b> {request_data.phone_number}
<b>Название клинники:</b> {request_data.clinic_name}
<b>Город:</b> {request_data.city}
<b>Название аппарата:</b> {request_data.apparat_name}
<b>Описание проблемы:</b> {request_data.description_problem}
"""
		secondary_part = f"""
<b>Реквизиты:</b> {request_data.company_details}
<b>Местонахождение:</b> {request_data.location}
<b>Дата последнего ТО:</b> {request_data.maintenance_date}
		"""
		request_media = []
        
		photo_paths = request_data.mediafiles['photo']
		video_paths = request_data.mediafiles['video']
		for photo_path in photo_paths:
			request_media.append(InputMediaPhoto(media=FSInputFile(photo_path)))
		for video_path in video_paths:
			request_media.append(InputMediaVideo(media=FSInputFile(video_path)))
        
		request_types_map = {
			'short': required_part,
			'long': required_part+secondary_part
		}
   
		return request_types_map[type_request], request_media