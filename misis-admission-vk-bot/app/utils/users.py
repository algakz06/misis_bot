#!/usr/bin/env python3

"""User-related utilities."""
import requests
from typing import List
from app.config import log, DEFAULT_BASE_URL


class BotUsers:
    class Admins:
        def __init__(self, base_url: str = DEFAULT_BASE_URL):
            self.base_url: str = base_url
            self.admins: List[int] = []

            self.fetch()

        def fetch(self):
            """Fetches admins from backend."""
            self.admins = [int(i) for i in requests.get(f'{DEFAULT_BASE_URL}/admins/vk').json()]

        def add(self, user_id: int, token) -> bool:
            """Add admin to backend."""
            r = requests.post(
                f"{DEFAULT_BASE_URL}/admin/enroll",
                json={"user_id": user_id, "platform": "vk", "token": token},
            )
            result = True if r.json()["status"] == 0 else False
            if result:
                log.warning(
                    f"BotAdmins.add() [SUCCESS]: data: {user_id}, response: {r.json()}, token: {token}"
                )
                self.admins.append(user_id)
            else:
                log.info(
                    f"BotAdmins.add() [FAIL]: data: {user_id}, response: {r.json()}, token: {token}"
                )
            return result

        def remove(self, user_id: int) -> bool:
            """Remove admin from backend."""
            r = requests.delete(f"{DEFAULT_BASE_URL}/admin/tg/{user_id}")
            result = True if r.json().get("status", 0) else False
            if result:
                log.warning(
                    f"BotAdmins.remove() [SUCCESS]: data: {user_id}, response: {r.json()}"
                )
                self.admins.remove(user_id)
            else:
                log.info(
                    f"BotAdmins.remove() [FAIL]: data: {user_id}, response: {r.json()}"
                )
            return result

        def is_admin(self, user_id: int) -> bool:
            """Check if user is admin."""
            return user_id in self.admins

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url: str = base_url
        self.users: dict = {}
        self.admins = BotUsers.Admins(base_url=base_url)

        self.fetch()

    def fetch(self):
        """Fetch users from backend."""
        self.users = {
            int(k): v
            for k, v in requests.get(f"{DEFAULT_BASE_URL}/users/all/vk").json().items()
        }

    def add(
        self,
        user_id: str,
        username: str,
        first_name: str,
        last_name: str,
        city: str,
        email: str,
        phone: str,
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

        r = requests.post(f"{DEFAULT_BASE_URL}/user/register", json=body)

        log.info(f"BotUser.add(): {r.status_code}, data: {body}")

    def add_params(self, user_id: str, param: str, value: str) -> None:
        data = {
            "user_id": user_id,
            "platform": "vk",
            param: value,
        }
        log.info(f'user_id={user_id}')
        user = self.users.get(user_id, {})
        user[param] = value
        self.users[user_id] = user
        r = requests.put(f"{DEFAULT_BASE_URL}/user/update/partial", json=data)
        print(r.text)
        log.info(f"BotUser.add_params(): {r.status_code}, data: {data}")

    def get(self, user_id: int) -> dict:
        """Get user by id."""
        return self.users.get(user_id, {}) or {}

    def get_ids(self) -> list[int]:
        """Return list of user ids."""
        return list(self.users.keys())

    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return user_id in self.users.keys()
