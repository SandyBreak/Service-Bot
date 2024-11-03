# -*- coding: UTF-8 -*-

from sqlalchemy import Column, String, Integer, Float, Boolean, ARRAY, TIMESTAMP, BigInteger, JSON

from .base import Base


class TemporaryRequestData(Base):
    __tablename__ = 'temporary_request_data'
    
    id = Column(Integer, primary_key=True)
    
    id_tg = Column(BigInteger, nullable=False)
    
    clinic_name = Column(String(length=512), nullable=True)
    city = Column(String(length=128), nullable=True)
    apparat_name = Column(String(length=512), nullable=True)
    description_problem = Column(String(length=4096), nullable=True)
    
    phone_number = Column(String(length=1024), nullable=True)
    
    mediafiles = Column(JSON, default={"photo": [], "video": []})
    company_details = Column(String(length=4096), nullable=True)
    location = Column(String(length=4096), nullable=True)
    maintenance_date = Column(String(length=512), nullable=True)