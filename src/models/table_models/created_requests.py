# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, ForeignKey, String, JSON, DateTime
from sqlalchemy.orm import relationship

from .base import Base

class CreatedRequests(Base):
    __tablename__ = 'created_requests'
    
    id = Column(Integer, primary_key=True, nullable=False)
    
    creator_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="created_requests")
    
    date_creation = Column(DateTime, nullable=True)
    
    clinic_name = Column(String(length=512), nullable=True)
    city = Column(String(length=128), nullable=True)
    apparat_name = Column(String(length=512), nullable=True)
    description_problem = Column(String(length=4096), nullable=True)
    
    phone_number = Column(String(length=1024), nullable=True)
    
    mediafiles = Column(JSON, default={"photo": [], "video": []})
    company_details = Column(String(length=4096), nullable=True)
    location = Column(String(length=4096), nullable=True)
    maintenance_date = Column(String(length=512), nullable=True)