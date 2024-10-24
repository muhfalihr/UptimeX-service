import os
import re
import yaml

from app.config.crsconfig import BaseConfig as parseconfig
from app.library.storage import CRStorage as crstorage

class CRLittletools:

    @staticmethod
    def list_file_tools(tools_path: str):
        try:
            files = os.listdir(tools_path)
            return [file for file in files if os.path.isfile(os.path.join(tools_path, file))]
        except FileNotFoundError:
            pass
    
    @staticmethod
    def remote_path(file: str):
        config = parseconfig()
        return os.path.join(config.CHECKER_PATH, file)
    
    @staticmethod
    def local_path(tools_path: str, file: str):
        return os.path.join(tools_path, file)
    
    @staticmethod
    def to_json(**kwargs):
        return kwargs
    
    @staticmethod
    def comparing_list(list1, list2):
        for value in list2:
            if value in list1:
                return True
        return False
    
    @staticmethod
    def update_list(list1, list2):
        for i in range(len(list2)):
            try:
                if list1[i]["status"] != list2[i]["status"]:
                    list1[i] = list2[i]
            except IndexError:
                list1[i] = list2[i]
        return list1

# class LittleTools:
#     def __init__(self) -> None:
#         pass

#     def research(self, pattern: str, string: str):
#         matches = re.compile( pattern ).search( string )
#         return matches.group() if matches else None
    
#     def get_config(self):
#         config_path = os.path.join(os.path.dirname( os.path.abspath( __name__ ) ), "config.yaml")
#         try:
#             with open( config_path, "r" ) as stream:
#                 return yaml.safe_load( stream )
#         except FileNotFoundError:
#             raise FileNotFoundError(f"Configuration file not found at {config_path}")
#         except yaml.YAMLError as error:
#             raise ValueError(f"Error parsing YAML file: {error}")
    
#     def _read_file(self, path: str):
#         try:
#             with open( path, "r" ) as file:
#                 return [ line.strip( "\n" ) for line in file.readlines() ]
#         except FileNotFoundError:
#             raise FileNotFoundError(f"File not found: {path}")
    
#     def get_passwd_list(self):
#         return self._read_file( self.config[ "PASSWD_LIST" ] )
    
#     def load_cache(self):
#         cache_set = set()
#         for uhp in self._read_file( self.config[ "CACHE_PATH" ] ):
#             cache_set.add( uhp )
#         return cache_set

#     def version_list(self):
#         return self._read_file( self.config[ "VERSION_LIST" ] )
    
#     def add_version(self, version):
#         version = str( version )
#         try:
#             with open( self.config[ "VERSION_LIST" ], "a" ) as file:
#                 file.write( f"\n{version}" )
#         except FileNotFoundError:
#             raise FileNotFoundError(f"Configuration file not found at {self.config[ 'VERSION_LIST' ]}")
    
#     def server_list(self):
#         list_server = []
#         for line in self._read_file( self.config[ "SERVER_CONFIG_LIST" ] ):
#             if line == "[list_server]":
#                 continue
#             elif re.match( r'\d+\.\d+\.\d+\.\d+', line ):
#                 list_server.append(line)
#             else:
#                 raise ValueError("Invalid server IP")
#         return list_server
