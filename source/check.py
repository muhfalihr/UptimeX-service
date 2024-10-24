from app.check import CRExec
from app.library.storage import CRStorage
from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, Security, Cookie, Header, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from typing import List, Optional
import asyncio

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua domain (atau ganti dengan list asal yang diizinkan)
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode (GET, POST, PUT, DELETE, dll.)
    allow_headers=["*"],  # Mengizinkan semua header
)


connected_clients = set()

@app.websocket("/ws/{ip_address}")
async def websocket_endpoint(
    websocket: WebSocket,
    ip_address: str = Path(...)
):

    await websocket.accept()
    connected_clients.add(websocket)

    cr = CRExec()

    try:
        while True:
            cr.setup_executor_file(ip_address)
            result = cr.execute_tools_remote("ceker.py", action="detail")

            await websocket.send_json(result)

            for client in connected_clients:
                if client != websocket:
                    await client.send_json(result)

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client}")
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        await websocket.close()

@app.get("/list_servers")
async def list_servers():
    crstorage = CRStorage()
    output = {
        "list_servers": crstorage.get_all_servers()
    }
    return output