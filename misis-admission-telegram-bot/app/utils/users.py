#!/usr/bin/env python3

"""User-related utilities."""
import requests
from typing import List
from time import sleep
from app.config import log
from app.config import DEFAULT_BASE_URL


class BotUsers:
    class Admins:
        def __init__(self, base_url: str = 'https://misis-admission.seizure.icu'):
            self.base_url: str = base_url
            self.admins: List[int] = []

            self.fetch()

        def fetch(self):
            """Fetches admins from backend."""
            self.admins = [int(i) for i in requests.get(f'{self.base_url}/admins/tg').json()]

        def add(self, user_id: int, token) -> bool:
            """Add admin to backend."""
            r = requests.post(
                f'{self.base_url}/admin/enroll', json={"user_id": user_id, "platform": "tg", "token": token}
            )
            result = True if r.json()["status"] == 0 else False
            if result:
                log.warning(f"BotAdmins.add() [SUCCESS]: data: {user_id}, response: {r.json()}, token: {token}")
                self.admins.append(user_id)
            else:
                log.info(f"BotAdmins.add() [FAIL]: data: {user_id}, response: {r.json()}, token: {token}")
            return result

        def remove(self, user_id: int) -> bool:
            """Remove admin from backend."""
            r = requests.delete(
                f'{self.base_url}/admin/tg/{user_id}'
            )
            result = True if r.json().get("status", 0) else False
            if result:
                log.warning(f"BotAdmins.remove() [SUCCESS]: data: {user_id}, response: {r.json()}")
                self.admins.remove(user_id)
            else:
                log.info(f"BotAdmins.remove() [FAIL]: data: {user_id}, response: {r.json()}")
            return result

        def is_admin(self, user_id: int) -> bool:
            """Check if user is admin."""
            return user_id in self.admins

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url: str = base_url
        self._test_connection()
        self.users: dict = {}
        self.admins = BotUsers.Admins(base_url=base_url)

        self.fetch()

    def _test_connection(self):
        connected = False
        counter = 0
        while not connected and counter < 7:
            counter += 1
            r = requests.get(f'{self.base_url}/ping')
            try:
                j = r.json()
                decoded = True
            except requests.exceptions.JSONDecodeError:
                decoded = False
            if decoded:
                if r.json()["status"] == "pong":
                    connected = True
                    log.debug(f"Connection to the backend seems to be fine; status: {r.status_code}, response: {r.text}")
            if not connected:
                log.debug(f"Connection to the backend is not successful; status: {r.status_code}, response: {r.text}")
            sleep(4)
        if not connected:
            import sys
            log.error(f"Connection failed after {counter + 1} attempts; shutting down")
            sys.exit(1)
        log.debug(f"Successfully connected after {counter + 1} attempts")

    def fetch(self):
        """Fetch users from backend."""
        self.users = {int(k): v for k, v in requests.get(f'{self.base_url}/users/all/tg').json().items()}

    def add(
        self, user_id: str, username: str = None, first_name: str = None,
        last_name: str = None, city: str = None, email: str = None, phone: str = None
    ) -> None:
        body = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "platform": "tg",
            "city": city,
            "email": email,
            "phone_number": phone,
        }
        # Add user to local cache
        self.users[user_id] = body

        r = requests.post(
            f'{self.base_url}/user/register', json=body
        )

        log.info(f"BotUser.add(): {r.status_code}, data: {body}")

    def update(self, user_id: int, first_name: str = None, last_name: str = None, city: str = None, email: str = None, phone: str = None):
        """Update user info."""
        body = self.users[user_id]
        if first_name:
            body["first_name"] = first_name
        if last_name:
            body["last_name"] = last_name
        if city:
            body["city"] = city
        if email:
            body["email"] = email
        if phone:
            body["phone_number"] = phone
        body["platform"] = "tg"
        r = requests.put(
            f'{self.base_url}/user/update', json=body
        )
        log.info(f"BotUser.update(): {r.status_code}, data: {body}")
        is_updated = True if r.json()["status"] == 0 else False
        if is_updated:
            if first_name:
                self.users["first_name"] = first_name
            if last_name:
                self.users["last_name"] = last_name
            if city:
                self.users["city"] = city
            if email:
                self.users["email"] = email
            if phone:
                self.users["phone_number"] = phone
        return is_updated

    def get(self, user_id: int) -> dict:
        """Get user by id."""
        return self.users.get(user_id, {}) or {}

    def get_ids(self) -> list[int]:
        """Return list of user ids."""
        return list(self.users.keys())

    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return user_id in self.users
