import requests
from pprint import pprint
from typing import List, Dict, Union, Optional
import json

from app.config import log



class Shit():

    def get_all_buttons(self) -> Union[Dict[str, str], None]:
        r = requests.get('https://misis-admission.seizure.icu/all/btns')
        try:
            data = r.json()
        except json.JSONDecodeError:
            return None
        self.buttons: Dict[str, str] = {}
        for btn in data:
            self.buttons[btn.get('text', '')] = btn.get('path', '')
        return self.buttons

    def get_reply(self, id: str) -> Union[str, None]:
        r = requests.get(f'https://misis-admission.seizure.icu/repls/{id}')
        r = r.json()
        try:
            reply = r[0].get('text', None)
            return reply
        except IndexError as e:
            log.error(f'ERROR: {e}, id: {id}')
            return None



    def get_btns(self, id: str) -> Union[Dict[str, str], None]:
        r = requests.get(f'https://misis-admission.seizure.icu/btns/{id}')
        r = r.json()
        buttons: Dict[str, str] = {}
        try:
            for btn in r:
                buttons[btn.get('text', '')] = btn.get('path', '')
        except ValueError as e:
            log.error(f'ERROR: {e}, id: {id}')
            return None
        finally:
            log.info(f'id={id}, buttons={buttons}')
            return buttons

if __name__ == '__main__':
    shit = Shit()
    pprint(shit.get_all_buttons())
