from typing import List, Dict, Any
from pydantic import BaseModel, Field

class Server(BaseModel):
    id: int
    ip_address: str
    created_at: str

class ResponseServerList(BaseModel):
    server_list: List[Server]
    timestamp: str

class ServerStatus(BaseModel):
    id: int
    ip_address: str
    username: str
    password: str
    status: str
    message: str

class ResponseServerStatus(BaseModel):
    server_status_list: List[ServerStatus]
    timestamp: str

class InfoParams(BaseModel):
    ip_address: str = Field("0.0.0.0")

class SystemInfo(BaseModel):
    system: str
    node_name: str
    release: str
    version: str
    machine: str
    processor: str

class ResponseServerSystemInfo(BaseModel):
    system_info: SystemInfo
    timestamp: str

class NetworkInfo(BaseModel):
    interfaces: Dict[Any, Any]

class ResponseNetworkInfo(BaseModel):
    network_info: NetworkInfo
    timestamp: str

class InputSettingsServerManagement(BaseModel):
    id: str|None
    ip_address: str|None
    label: str|None

class ResponseSettingsServerManagementSuccess(BaseModel):
    status: str
    message: str
    data: InputSettingsServerManagement|str
    timestamp: str