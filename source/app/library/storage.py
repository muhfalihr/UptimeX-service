import sqlite3
from typing import List, Any, Dict
from .mapperoutput import MapperOutput as mapperoutput
from app.config.crsconfig import BaseConfig as parseconfig

class CRStorage:
    def __init__(self) -> None:
        self.config = parseconfig()
        self.connection = sqlite3.connect("/home/sre-muhfalih/Documents/DEVOPS/CheckingResource/" + self.config.SQLITE_DATABASE)
        self.cursor = self.connection.cursor()
        self.mapper_output = mapperoutput(self.cursor)

    def get_all_servers(self, out_type: str) -> Any:
        self.cursor.execute("SELECT * FROM servers")
        if out_type == "list":
            return self.mapper_output.mapping_output_list(1)
        elif out_type == "dict":
            return self.mapper_output.mapping_output_json()

    def insert_server(self, servers: list) -> None:
        values = ",".join(f"('{server}')" for server in servers)
        self.cursor.execute(f"INSERT INTO servers (ip_address) VALUES {values}")
        self.connection.commit()

    def get_all_passwords(self) -> List[Any]:
        self.cursor.execute("SELECT * FROM passwords")
        return self.mapper_output.mapping_output_list(1)

    def insert_password(self, passwords: list) -> None:
        values = ",".join(f"('{password}')" for password in passwords)
        self.cursor.execute(f"INSERT INTO passwords (password) VALUES {values}")
        self.connection.commit()

    def get_auth_server(self) -> List[Any]:
        self.cursor.execute(
            # f"SELECT * FROM server_configurations WHERE ip_address = '{ip_address}'"
            f"SELECT * FROM server_configurations"
        )
        return self.mapper_output.mapping_output_json()

    def insert_auth_server(self, ip_address: str, password: str) -> None:
        self.cursor.execute(
            f"INSERT INTO server_configurations (ip_address, password) VALUES ('{ip_address}', '{password}')"
        )
        self.connection.commit()

    def get_latest_version(self) -> str:
        self.cursor.execute("SELECT * FROM versions ORDER BY created_at DESC LIMIT 1")
        return self.mapper_output.mapping_output_str_one(1)

    def insert_version(self, version) -> None:
        self.cursor.execute(f"INSERT INTO versions (version) VALUES ('{version}')")
        self.connection.commit()

    def get_server_status(self):
        self.cursor.execute("SELECT * FROM server_status")
        return self.mapper_output.mapping_output_json()

    def insert_server_status(self, inserts: List[dict]):
        datas = [
            (data.get('ip_address'), data.get('label', None), data.get('status'), data.get('message')) for data in inserts
        ]
        self.cursor.executemany("INSERT INTO server_status (ip_address, label, status, message) VALUES (?, ?, ?, ?)", datas)
        self.connection.commit()