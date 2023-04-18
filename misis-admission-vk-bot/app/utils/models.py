from sqlalchemy import Column, Boolean, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class BotUser(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


