import redis
import json
import asyncio
from typing import List
from models import ResponseServerList, ResponseServerStatus
from datetime import datetime
from app.helpers.littletools import CRLittletools as crlt
from app.library.storage import CRStorage
from app.check import CRExec as crexec
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, Security, Cookie, Header, Path


crstorage = CRStorage()
# redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, password="rediskuinibang", decode_responses=True)

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
    return ResponseServerList(
        server_list=crstorage.get_all_servers("dict"), 
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    )

@app.websocket("/ws/servers/list/status")
async def servers_list_status(websocket: WebSocket) -> ResponseServerStatus:
    await cwsmanager.connect(websocket)
    check = crexec()

    try:
        isfirst = True
        while True:
            if isfirst:
                all_server_status = []
                async for server_status in check.all_servers_status_perbatch():
                    message = crlt.to_json(
                        server_status_list=server_status if not all_server_status else all_server_status,
                        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    await cwsmanager.send_personal_message(message, websocket)
                    all_server_status.extend(server_status)
                isfirst = False
            else:
                all_server_status = await check.all_servers_status()
                message = crlt.to_json(
                    server_status_list=all_server_status,
                    timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                )
                await cwsmanager.send_personal_message(message, websocket)

        # done = False
        # while True:
        #     if done:
        #         server_status = crstorage.get_server_status()
        #         message = crlt.to_json(
        #             server_status_list=server_status,
        #             timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        #         )
        #         await cwsmanager.send_personal_message(message, websocket)

        #     async for server_status in check.all_servers_status():
        #         message = crlt.to_json(
        #             server_status_list=server_status,
        #             timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        #         )
        #         crstorage.insert_server_status(server_status)
        #         if not done:
        #             await cwsmanager.send_personal_message(message, websocket)
                
        #     done = True
                # await cwsmanager.send_personal_message(server_status_store, websocket)
                # async for server_status in check.all_servers_status():
                #     message = crlt.to_json(
                #         server_status_list=server_status,
                #         timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                #     )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        cwsmanager.disconnect(websocket)
