import ast
import os
import json
import logging
import asyncio

from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.config.crsconfig import BaseConfig as parseconfig
from app.library.remotexec import RemoteEXec as remoteexec
from app.library.remoterequire import RemoteRequire as remoterequire
from app.library.storage import CRStorage as crstorage
from app.library.serverstatus import CRServerStatus as crserverstatus
from app.helpers.littletools import CRLittletools as crltools

class CRExec:
    TOOLS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
    
    def __init__(self):
        self.config = parseconfig()
        self.crstorage = crstorage()
        self.remoteexec = remoteexec()
        self.remoterequire = remoterequire()

    async def setup_executor_file(self, ip_address: str):
        sftp, setup = await self.remoterequire.ssh_client_connect(ip_address)
        if not setup:
            await self.remoterequire.dir_is_exists(self.config.CHECKER_TOOLS_PATH)
            list_file_tools = await crltools.list_file_tools(self.TOOLS_PATH)
            tasks = [
                self.remoterequire.copy_file(await crltools.local_path(self.TOOLS_PATH, file), await crltools.remote_path(file))
                for file in list_file_tools
            ]
            await asyncio.gather(*tasks)
            await self.remoterequire.pip_is_installed()
            await self.remoterequire.pip_package(self.config.CHECKER_TOOLS_PATH)

    async def execute_tools(self, **action):
        file = await crltools.remote_path("ceker.py")
        result = await self.remoterequire.execute_tools(file, **action)
        return ast.literal_eval(result)
    
    @staticmethod
    async def process_batch(batch):
        servers_status = []
        for server in batch:

            serverstatus = crserverstatus(
                server["ip_address"],
                ssh_username=server["username"],
                ssh_password=server["password"]
            )
            server_status = await crltools.to_json(
                id=server["id"],
                labels=[server["label"]],
                ip_address=server["ip_address"],
                username=server["username"]
            )
            server_status.update(await serverstatus.get_server_status())
            servers_status.append(server_status)
        return servers_status

    @staticmethod
    async def chunk_list(lst, n):
        if asyncio.iscoroutine(lst):
            lst = await lst
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def all_servers_status_perbatch(self):
        await self.crstorage.connect()
        servers = await self.crstorage.get_auth_server()
        # servers = self.crstorage.get_all_servers("dict")
        chunk_size = 12
        server_batches = [chunk async for chunk in self.chunk_list(servers, chunk_size)]

        async def process_batch_async(batch):
            return await self.process_batch(batch)

        tasks = [process_batch_async(batch) for batch in server_batches]
        
        for result in asyncio.as_completed(tasks):
            yield await result

    async def all_servers_status(self):
        await self.crstorage.connect()
        # servers = self.crstorage.get_all_servers("dict")
        servers = await self.crstorage.get_auth_server()
        chunk_size = 12
        server_batches = [chunk async for chunk in self.chunk_list(servers, chunk_size)]

        async def process_batch_async(batch):
            return await self.process_batch(batch)

        tasks = [process_batch_async(batch) for batch in server_batches]
        results = await asyncio.gather(*tasks)
        servers_status = [status for result in results for status in result]
        return servers_status
