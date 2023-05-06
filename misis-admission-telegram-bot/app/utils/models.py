from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BOOLEAN, VARCHAR
from sqlalchemy.sql import func


Base = declarative_base()


class BotUser(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    is_admin = Column(BOOLEAN, default=False)
    first_name = Column(VARCHAR(20))
    last_name = Column(VARCHAR(20))
    city = Column(VARCHAR(50))
    phone = Column(VARCHAR(20))
    email = Column(VARCHAR(50))
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ButtonPress(Base):
    __tablename__ = "button_presses"

    id = Column(BigInteger, primary_key=True)
    button_id = Column(VARCHAR(20), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    pressed_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
