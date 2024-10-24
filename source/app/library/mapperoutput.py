import json
from sqlite3 import Cursor


class MapperOutput:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def mapping_output_json(self, one=False):
        columns = [column[0] for column in self.cursor.description]
        if one:
            fetch = self.cursor.fetchone()
            if fetch:
                raw_dict = dict(zip(columns, fetch))
            else:
                raw_dict = dict()

        else:
            fetch = self.cursor.fetchall()
            if fetch:
                raw_dict = [dict(zip(columns, row)) for row in fetch]
            else:
                raw_dict = list()
        # result = json.dumps(raw_dict, indent=4)
        return raw_dict

    def mapping_output_list(self, index):
        return [row[index] for row in self.cursor.fetchall()]

    def mapping_output_str_one(self, index):
        return self.cursor.fetchone()[index]
