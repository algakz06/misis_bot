import requests
from pprint import pprint
from typing import List, Dict
import json



class Shit():

    def get_all_buttons(self) -> List:
        r = requests.get('https://misis-admission.seizure.icu/all/btns')
        try:
            data = r.json()
        except json.JSONDecodeError:
            return None
        self.buttons: Dict[str, str] = {}
        for btn in data:
            self.buttons[btn.get('text', '')] = btn.get('path', '')
        return self.buttons

    def get_reply(self, id: str) -> str:
        r = requests.get(f'https://misis-admission.seizure.icu/repls/{id}')
        r = r.json()
        print(f'response: {r}, id: {id}')
        return r[0].get('text', None)

    def get_btns(self, id: str) -> List[str]:
        r = requests.get(f'https://misis-admission.seizure.icu/btns/{id}')
        r = r.json()
        buttons: List[str] = []
        try:
            for btn in r:
                buttons.append(btn.get('text', None))
        except ValueError:
            return None
        return buttons

if __name__ == '__main__':
    shit = Shit()
    pprint(shit.get_all_buttons())
