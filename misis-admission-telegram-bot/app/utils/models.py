from sqlalchemy import Column, Boolean, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class BotUser(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


