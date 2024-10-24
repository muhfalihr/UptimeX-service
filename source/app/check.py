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
    
    @staticmethod
    def _secure_copy_file(sftp, remotepath: str, localpath: str):
        try:
            sftp.stat(remotepath)
            logging.info(f"File {remotepath} already exists on the remote server")
        except FileNotFoundError:
            sftp.put(localpath, remotepath)
            logging.info(f"Uploaded {localpath} to {remotepath}")

    def setup_executor_file(self, ip_address: str):
        sftp, setup = self.remoterequire.ssh_client_connect(ip_address)
        if not setup:
            self.remoterequire.pip_is_installed()
            self.remoterequire.dir_is_exists(self.config.CHECKER_PATH)
            self.remoterequire.pip_package(self.config.CHECKER_PATH)
        
            [
                self._secure_copy_file(sftp, crltools.remote_path(file), crltools.local_path(self.TOOLS_PATH, file))
                for file in crltools.list_file_tools(self.TOOLS_PATH)
            ]

        # if(self.config.VERSION != self.crstorage.get_latest_version()):
        #     ...
    
    def execute_tools_remote(self, file, **action):
        result = self.remoterequire.execute_tools(crltools.remote_path(file), **action)
        result = ast.literal_eval(result)
        return result
    
    @staticmethod
    def process_batch(batch):
        servers_status = []
        for server in batch:
            # Ambil status server menggunakan SSH
            serverstatus = crserverstatus(
                server["ip_address"],
                ssh_username=server["username"],
                ssh_password=server["password"]
            )
            # Format data server dalam JSON
            server_status = crltools.to_json(
                id=server["id"],
                ip_address=server["ip_address"],
                username=server["username"],
                password=server["password"]
            )
            server_status.update(serverstatus.get_server_status())
            servers_status.append(server_status)
        return servers_status

    @staticmethod
    def chunk_list(lst, n):
        """Membagi list menjadi batch dengan ukuran n."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def all_servers_status_perbatch(self):
        servers = self.crstorage.get_auth_server()
        
        # Here, chunk the servers list into batches of exactly 12
        chunk_size = 12
        server_batches = list(self.chunk_list(servers, chunk_size))

        async def process_batch_async(batch):
            return await asyncio.to_thread(self.process_batch, batch)

        tasks = [process_batch_async(batch) for batch in server_batches]
        
        for result in asyncio.as_completed(tasks):
            yield await result

    async def all_servers_status(self):
        servers = self.crstorage.get_auth_server()
        chunk_size = 12
        server_batches = list(self.chunk_list(servers, chunk_size))
        async def process_batch_async(batch):
            return await asyncio.to_thread(self.process_batch, batch)
        tasks = [process_batch_async(batch) for batch in server_batches]
        results = await asyncio.gather(*tasks)
        servers_status = [status for result in results for status in result]
        return servers_status
    # def all_servers_status(self):
    #     servers = self.crstorage.get_auth_server()
        
    #     chunk_size = max(1, len(servers) // 12)

    #     server_batches = list(self.chunk_list(servers, chunk_size))
        
    #     
    #     with ThreadPoolExecutor(max_workers=min(12, len(server_batches))) as executor:
    #         futures = {executor.submit(self.process_batch, batch): batch for batch in server_batches}
            
    #         for future in as_completed(futures):
    #             yield future.result()
        #         servers_status.extend(future.result())
        
        # return servers_status