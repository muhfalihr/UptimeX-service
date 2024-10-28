import json
import aiosqlite


class MapperOutput:
    def __init__(self, cursor: aiosqlite.Cursor) -> None:
        self.cursor = cursor

    async def mapping_output_json(self, one=False):
        try:
            columns = [column[0] for column in self.cursor.description]
            
            if one:
                fetch = await self.cursor.fetchone()
                if fetch:
                    raw_dict = dict(zip(columns, fetch))
                else:
                    raw_dict = dict()
            else:
                fetch = await self.cursor.fetchall()
                if fetch:
                    raw_dict = [dict(zip(columns, row)) for row in fetch]
                else:
                    raw_dict = list()
                    
            return raw_dict
        except TypeError:
            return None

    async def mapping_output_list(self, index):
        rows = await self.cursor.fetchall()
        return [row[index] for row in rows]

    async def mapping_output_str_one(self, index):
        row = await self.cursor.fetchone()
        return row[index]