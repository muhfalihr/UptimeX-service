import redis
import json
import asyncio
from typing import List, Annotated
from models import ResponseServerList, ResponseServerStatus, ResponseServerSystemInfo, ResponseNetworkInfo, InfoParams
from datetime import datetime
from app.helpers.littletools import CRLittletools as crlt
from app.library.storage import CRStorage
from app.check import CRExec as crexec
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, Query, Depends, WebSocketDisconnect, Security, Cookie, Header, Path

check = crexec()
crstorage = CRStorage()

app =FastAPI(debug=True, title="CheckerAPI", openapi_url="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ConnectionWSManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

cwsmanager = ConnectionWSManager()

@app.get("/servers/list", tags=["Servers"])
async def servers_list() -> ResponseServerList:
    servers_list = await crstorage.get_all_servers("dict")
    await crstorage.close()
    return ResponseServerList(
        server_list=servers_list, 
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    )

# @app.get("/servers/system_info", tags=["Servers"])
# async def servers_system_info(params: Annotated[InfoParams, Query()]) -> ResponseServerSystemInfo:
#     await check.setup_executor_file(params.ip_address)
#     await crstorage.close()
#     return ResponseServerSystemInfo(
#         system_info=await check.execute_tools(action="system_info"),
#         timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
#     )

# @app.websocket("/servers/network_info")
# async def servers_network_info(websocket: WebSocket, params: Annotated[InfoParams, Query()]) -> ResponseNetworkInfo:
#     await cwsmanager.connect(websocket)
#     await check.setup_executor_file(params.ip_address)
#     try:
#         while True:
#             message = await crlt.to_json(
#                 network_info=await check.execute_tools(action="network_info"),
#                 timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
#             )
#             await cwsmanager.send_personal_message(message, websocket)
#             await asyncio.sleep(1)
#     except WebSocketDisconnect:
#         cwsmanager.disconnect(websocket)

@app.websocket("/ws/servers/list/status")
async def servers_list_status(websocket: WebSocket) -> ResponseServerStatus:
    await cwsmanager.connect(websocket)
    try:
        isfirst = True
        while True:
            if isfirst:
                all_server_status = []
                all_servers_status_perbatch = check.all_servers_status_perbatch()
                async for server_status in all_servers_status_perbatch:
                    message = await crlt.to_json(
                        server_status_list=server_status if not all_server_status else all_server_status,
                        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    await cwsmanager.send_personal_message(message, websocket)
                    all_server_status.extend(server_status)
                isfirst = False
            else:
                all_server_status = await check.all_servers_status()
                message = await crlt.to_json(
                    server_status_list=all_server_status,
                    timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                )
                await cwsmanager.send_personal_message(message, websocket)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        cwsmanager.disconnect(websocket)
