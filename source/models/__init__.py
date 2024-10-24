from typing import List
from pydantic import BaseModel

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