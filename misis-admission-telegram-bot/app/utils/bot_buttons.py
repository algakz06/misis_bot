import requests
from typing import List, Dict, Union, Optional
import json

from app.config import log, DEFAULT_BASE_URL


class Layout:
    def __init__(self):
        self.buttons: Dict[str, str] = {}

    def get_all_buttons(self) -> Union[Dict[str, str], None]:
        r = requests.get(f"{DEFAULT_BASE_URL}/all/btns")
        try:
            data = r.json()
        except json.JSONDecodeError:
            return None
        self.buttons: Dict[str, str] = {}
        for btn in data:
            self.buttons[btn.get("path", "")] = btn.get("text", "")
        return self.buttons

    @staticmethod
    def get_reply(id: str) -> Union[str, None]:
        r = requests.get(f"{DEFAULT_BASE_URL}/repls/{id}")
        r = r.json()
        try:
            reply = r[0].get("text", None)
            return reply
        except IndexError as e:
            log.error(f"ERROR: {e}, id: {id}")
            return None

    @staticmethod
    def get_btns(id: str) -> Union[Dict[str, str], None]:
        r = requests.get(f"{DEFAULT_BASE_URL}/btns/{id}")
        r = r.json()
        buttons: Dict[str, str] = {}
        try:
            for btn in r:
                buttons[btn.get("path", "")] = btn.get("text", "")
        except ValueError as e:
            log.error(f"ERROR: {e}, id: {id}")
            return None
        finally:
            log.info(f"id={id}, buttons={buttons}")
            return buttons

    # @staticmethod
    # def send_stats(data: List[Dict[str, Union[str, int]]]) -> None:
    #     body = {"events": data}
    #
    #     r = requests.post(f"{DEFAULT_BASE_URL}/telemetry", json=body)
    #
    #     log.info(f"send_stats: {r.status_code}, data: {data}")

    # @staticmethod
    # def send_bot_user(
    #     user_id: str, username: str, first_name: str,
    #     last_name: str, city: str, email: str, phone: str
    # ) -> None:
    #     body = {
    #         "user_id": user_id,
    #         "username": username,
    #         "first_name": first_name,
    #         "last_name": last_name,
    #         "platform": "tg",
    #         "city": city,
    #         "email": email,
    #         "phone": phone,
    #     }
    #
    #     r = requests.post(
    #         f"{DEFAULT_BASE_URL}/user/register", json=body
    #     )
    #
    #     log.info(f"send_bot_user: {r.status_code}, data: {body}")
