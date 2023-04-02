import gspread
import json

class GSheet:
    def __init__(self, creds_file: str, sheet_name: str):
        # Create creds pseudo-file in memory with IO
        gc = gspread.service_account(filename=creds_file)
        self.sh = gc.open(sheet_name)
        self.ws0 = self.sh.get_worksheet(0)
        self.raw_data = self.ws0.get_all_values()[1:]
        self.fetch_columns()

    def fetch_columns(self) -> dict:
        # cols structure: {'0': {'text': 'abc', 'is_reply': 'y'}, '1': {'text': 'abc', 'is_reply': ''}, ...}
        # Get all columns from the second row, default blank is ''
        cols = self.ws0.get_all_values()
        # Convert to dict
        cols = {str(col[0]): col[1:] for col in cols}
        for key, value in cols.items():
            # Skip if text is empty
            if value[0] == '':
                continue
            dic = {}
            # Text mutation
            dic.update({'text': value[0]})
            # Description mutation
            try:
                if value[1] == '':
                    dic.update({'is_reply': False})
                else:
                    dic.update({'is_reply': True})
            except:
                print(f"ERROR on {key}! {value}")
            # Update value
            cols[key] = dic

        json_cols = {}
        for key, value in cols.items():
            # If the whole key contains nothing, skip
            if value['text'] == '' and not value['is_reply']:
                continue
            # splitting key to create nested dictionary
            key_list = list(map(str, key.split('.')))
            temp_dict = json_cols
            for k in key_list[:-1]:
                temp_dict = temp_dict.setdefault(k, {})
            temp_dict[key_list[-1]] = value
        self.columns = json_cols