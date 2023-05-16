#!/usr/bin/env python3

"""Statistics-related utilities."""

import requests
from typing import List
from datetime import datetime
from app.config import log, DEFAULT_BASE_URL


class Statistics:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url: str = base_url
        self.storage: List[dict] = []

    def send(self):
        """Send all stored statistics to backend."""
        body = {"events": self.storage}
        r = requests.post("https://misis-admission.seizure.icu/telemetry", json=body)
        log.debug(f"Statistics.send(): {r.status_code}, data: {body}")
        self.storage = []

    def store(self, user_id: int, button_id: str):
        """Store button press in-memory."""
        self.storage.append(
            {
                "user_id": user_id,
                "platform": "tg",
                "button_id": button_id,
                "timestamp": int(datetime.now().timestamp()),
            }
        )

        if len(self.storage) >= 20:
            self.send()
