import os
import re
import yaml
import asyncio
from aiofiles import os as async_os

from app.config.crsconfig import BaseConfig as parseconfig
from app.library.storage import CRStorage as crstorage

class CRLittletools:

    @staticmethod
    async def list_file_tools(tools_path: str):
        try:
            files = await async_os.listdir(tools_path)
            return [file for file in files if await async_os.path.isfile(os.path.join(tools_path, file))]
        except FileNotFoundError:
            return []

    @staticmethod
    async def remote_path(file: str):
        config = parseconfig()
        return os.path.join(config.CHECKER_TOOLS_PATH, file)
    
    @staticmethod
    async def local_path(tools_path: str, file: str):
        return os.path.join(tools_path, file)
    
    @staticmethod
    async def to_json(**kwargs):
        return kwargs
    
    @staticmethod
    async def comparing_list(list1, list2):
        for value in list2:
            if value in list1:
                return True
        return False
    
    @staticmethod
    async def update_list(list1, list2):
        for i in range(len(list2)):
            try:
                if list1[i]["status"] != list2[i]["status"]:
                    list1[i] = list2[i]
            except IndexError:
                list1[i] = list2[i]
        return list1
