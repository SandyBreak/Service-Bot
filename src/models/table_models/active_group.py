# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, BigInteger, String, BOOLEAN

from .base import Base


class ActiveGroup(Base):
    __tablename__ = 'active_groups'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, nullable=False)
    type_group =  Column(String(length=64), nullable=True)
    access_flag = Column(BOOLEAN, nullable=True)