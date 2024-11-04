import redis
import json
import asyncio
from typing import List, Annotated
from models import ResponseSettingsServerManagementSuccess
from datetime import datetime
from app.helpers.littletools import CRLittletools as crlt
from app.library.hydra import get_password
from app.library.storage import CRStorage
from app.check import CRExec as crexec
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, WebSocket, Form, Query, Depends, WebSocketDisconnect, Security, Cookie, Header, status, Request


check = crexec()
crstorage = CRStorage()

app =FastAPI(debug=True, title="CheckerSettingsAPI", openapi_url="/api/v1")
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

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    await crstorage.connect()
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        loc = error["loc"]
        msg = error["msg"]
        formatted_errors.append(
            await crlt.to_json(
                field=loc[-1], error=msg
            )
        )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content= await crlt.to_json(
            status="failed",
            message="Added failed",
            detail=formatted_errors,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
    )

@app.post("/settings/server_management/add", tags=["ServerManagement"])
async def settings_server_management(
    ip_address: Annotated[str, Form(..., regex=r'^(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')], 
    label: Annotated[str, Form(..., regex=r'^[a-zA-Z0-9-_]{1,100}$')]) -> ResponseSettingsServerManagementSuccess:
    await crstorage.connect()
    password = get_password("root", ip_address, threads=64)
    data = await crlt.to_json(
        ip_address=ip_address,
        label=label,
        password=password
    )
    await crstorage.insert_server([data])
    await crstorage.insert_auth_server([data])
    await crstorage.close()
    del data["password"]
    await check.setup_executor_file(ip_address)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= await crlt.to_json(
            status="success",
            message="Server added successfully",
            data=data,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
    )

@app.put("/settings/server_management/edit", tags=["ServerManagement"])
async def settings_server_management_edit(
    id: Annotated[str, Form()],
    ip_address: Annotated[str, Form(..., regex=r'^(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')], 
    label: Annotated[str, Form(..., regex=r'^[a-zA-Z0-9-_]{1,100}$')]) -> ResponseSettingsServerManagementSuccess:
    await crstorage.connect()
    data = await crlt.to_json(
        id=id,
        ip_address=ip_address,
        label=label
    )
    await crstorage.update_server(data)
    await crstorage.update_auth_server(data)
    await crstorage.close()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= await crlt.to_json(
            status="success",
            message="Server updated successfully",
            data=data,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
    )

@app.delete("/settings/server_management/delete", tags=["ServerManagement"])
async def settings_server_management_delete(
    id: Annotated[str, Form()],
    ip_address: Annotated[str, Form(..., regex=r'^(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')]
    ) ->  ResponseSettingsServerManagementSuccess:
    await crstorage.connect()
    await crstorage.delete_server(id)
    await crstorage.delete_auth_server(id)
    await crstorage.close()
    await check.destroy_setup_exec_file(ip_address)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= await crlt.to_json(
            status="success",
            message="Server deleted successfully",
            data=id,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
    )

@app.get("/settings/server_management", tags=["ServerManagement"])
async def settings_server_management_get() -> ResponseSettingsServerManagementSuccess:
    await crstorage.connect()
    data = await crstorage.get_all_servers('dict')
    await crstorage.close()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= await crlt.to_json(
            status="success",
            message="Server settings retrieved successfully",
            data=data,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
    )