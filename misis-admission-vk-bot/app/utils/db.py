from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound, PendingRollbackError

from typing import List
import time

from app import config
from app.utils.models import Base, BotUser, ButtonPress
from app.config import log

class DBManager:
    #region inner methods
    def __init__(self):
        self._connect()
        self._recreate_table()
        self.db_session()

    def _connect(self) -> None:
        self.engine = create_engine(
            f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DB}',
            echo=True
        )

    def _recreate_table(self) -> None:
        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def db_session(self) -> None:
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def close_connection(self) -> None:
        self.engine.dispose()

    def __del__(self) -> None:
        self.close_connection()

    def insert_bot_user(self, user_id: int) -> None:
        self.session.merge(BotUser(user_id=user_id))
        self.session.commit()

        log.info(f'bot_user had been inserted {user_id}')

    def insert_button_press(self, user_id: int, button_id: str) -> None:
        try:
            self.session.merge(ButtonPress(user_id=user_id, button_id=button_id))
            self.session.commit()
        except PendingRollbackError:
            self.session.rollback()
            self.session.merge(BotUser(user_id=user_id))
            self.session.merge(ButtonPress(user_id=user_id, button_id=button_id))
            self.session.commit()

        log.info(f'button_press had been inserted {user_id}, {button_id}')

    def is_admin(self, id: int) -> bool:
        try:
            self.session.query(BotUser).filter(BotUser.user_id == id, BotUser.is_admin == True).one()
            return True
        except NoResultFound:
            return False

    def insert_admin(self, user_id: int) -> None:
        self.session.merge(BotUser(user_id=user_id, is_admin=True))

    def get_statistics(self):
        data = [{
            'user_id': item.user_id,
            'platform': 'tg',
            'button_id': item.button_id,
            'timestamp': int(item.pressed_at.timestamp())
        } for item in self.session.query(ButtonPress).all()]

        self.session.query(ButtonPress).delete()

        return data

    def get_users(self) -> List[int]:
        return [user.user_id for user in self.session.query(BotUser).all()]

    #endregion
