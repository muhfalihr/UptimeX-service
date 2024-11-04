import aiosqlite
from typing import List, Any
from .mapperoutput import MapperOutput as mapperoutput
# from app.helpers.errorhandler import async_error_handler_sqlite
from app.config.crsconfig import BaseConfig as parseconfig
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

class CRStorage:
    def __init__(self) -> None:
        self.config = parseconfig()
        self.database_path = "/home/sre-muhfalih/Documents/DEVOPS/CheckingResource/" + self.config.SQLITE_DATABASE
        self.mapper_output = None
        self.connection = None
        self.cursor = None

    async def connect(self):
        self.connection = await aiosqlite.connect(self.database_path)
        self.cursor = await self.connection.cursor()
        self.mapper_output = mapperoutput(self.cursor)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_all_servers(self, out_type: str) -> Any:
        try:
            await self.cursor.execute("SELECT * FROM servers")
            if out_type == "list":
                return await self.mapper_output.mapping_output_list(1)
            elif out_type == "dict":
                return await self.mapper_output.mapping_output_json()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def insert_server(self, servers: list) -> None:
        try:
            values = ",".join(f"(\'{server['ip_address']}\', \'{server['label']}\')" for server in servers)
            await self.cursor.execute(f"INSERT INTO servers (ip_address, label) VALUES {values}")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def update_server(self, servers: dict) -> None:
        id = servers.get("id", None)
        ip_address = servers.get("ip_address", None)
        label = servers.get("label", None)
        try:
            if ip_address and label:
                await self.cursor.execute(f"UPDATE servers SET ip_address = '{ip_address}', label = '{label}' WHERE id = '{id}'")
                await self.connection.commit()
            elif ip_address:
                await self.cursor.execute(f"UPDATE servers SET ip_address = '{ip_address}' WHERE id = '{id}'")
                await self.connection.commit()
            elif label:
                await self.cursor.execute(f"UPDATE servers SET label = '{label}' WHERE id = '{id}'")
                await self.connection.commit()
            else:
                ...
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def delete_server(self, id: str) -> None:
        try:
            await self.cursor.execute(f"DELETE FROM servers WHERE id = '{id}'")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_all_passwords(self) -> List[Any]:
        try:
            await self.cursor.execute("SELECT * FROM passwords")
            return await self.mapper_output.mapping_output_list(1)
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def insert_password(self, passwords: list) -> None:
        try:
            values = ",".join(f"('{password}')" for password in passwords)
            await self.cursor.execute(f"INSERT INTO passwords (password) VALUES {values}")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_auth_server(self) -> List[Any]:
        try:
            await self.cursor.execute("SELECT * FROM server_management")
            return await self.mapper_output.mapping_output_json()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise
        
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_auth_specific_server(self, ip_address: str):
        try:
            await self.cursor.execute(f"SELECT * FROM server_management WHERE ip_address = '{ip_address}'")
            return await self.mapper_output.mapping_output_json(True)
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def insert_auth_server(self, servers: list) -> None:
        try:
            values = ",".join(
                f"(\'{server['ip_address']}\', \'{server['label']}\', \'{server['password']}\', (SELECT id FROM servers WHERE ip_address = '{server['ip_address']}'))" 
                for server in servers
            )
            await self.cursor.execute(f"INSERT INTO server_management (ip_address, label, password, server_id) VALUES {values}")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def update_auth_server(self, servers: dict) -> None:
        id = servers.get("id", None)
        ip_address = servers.get("ip_address", None)
        label = servers.get("label", None)
        try:
            if ip_address and label:
                await self.cursor.execute(
                    f"UPDATE server_management SET ip_address = '{ip_address}', label = '{label}'"
                    f"WHERE server_id = (SELECT id FROM servers WHERE id = '{id}');"
                )
                await self.connection.commit()
            elif ip_address:
                await self.cursor.execute(
                    f"UPDATE server_management SET ip_address = '{ip_address}'"
                    f"WHERE server_id = (SELECT id FROM servers WHERE id = '{id}');"
                )
                await self.connection.commit()
            elif label:
                await self.cursor.execute(
                    f"UPDATE server_management SET label = '{label}'"
                    f"WHERE server_id = (SELECT id FROM servers WHERE id = '{id}');"
                )
                await self.connection.commit()
            else:
                ...
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def delete_auth_server(self, id: str) -> None:
        try:
            await self.cursor.execute(f"DELETE FROM server_management WHERE server_id = '{id}'")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_latest_version(self) -> str:
        try:
            await self.cursor.execute("SELECT * FROM versions ORDER BY created_at DESC LIMIT 1")
            return await self.mapper_output.mapping_output_str_one(1)
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def insert_version(self, version) -> None:
        try:
            await self.cursor.execute(f"INSERT INTO versions (version) VALUES ('{version}')")
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def get_server_status(self):
        try:
            await self.cursor.execute("SELECT * FROM server_status")
            return await self.mapper_output.mapping_output_json()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiosqlite.OperationalError)
    )
    async def insert_server_status(self, inserts: List[dict]):
        try:
            datas = [
                (data.get('ip_address'), data.get('label', None), data.get('status'), data.get('message')) for data in inserts
            ]
            await self.cursor.executemany("INSERT INTO server_status (ip_address, label, status, message) VALUES (?, ?, ?, ?)", datas)
            await self.connection.commit()
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else: raise

    async def close(self):
        await self.connection.close()
