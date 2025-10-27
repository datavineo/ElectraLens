from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Voter(Base):
    __tablename__ = 'voters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    constituency = Column(String(255), index=True)
    booth_no = Column(String(50))
    address = Column(Text)
    vote = Column(Boolean, default=False)  # Track if voter has voted or not
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
