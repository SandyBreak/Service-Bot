# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, BOOLEAN
from sqlalchemy.orm import relationship

from .base import Base
from .created_requests import CreatedRequests

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False)
    
    id_tg = Column(BigInteger, nullable=True)
    nickname = Column(String(length=64), nullable=True)
    fullname = Column(String(length=64), nullable=True)
    
    date_reg = Column(DateTime, nullable=True)
    message_thread_id = Column(BigInteger, nullable=True)
    access_flag = Column(BOOLEAN, nullable=True)
    
    created_requests = relationship("CreatedRequests", back_populates="user")