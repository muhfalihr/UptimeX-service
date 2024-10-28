from .hydra import get_password
from .storage import CRStorage as crstorage

async def setup_auth_server(ip_address: str, user: str = "root"):
    crs = crstorage()
    await crs.connect()
    access = crs.get_auth_specific_server(ip_address)
    password = get_password(user, ip_address, threads=64)
    await crs.insert_auth_server(ip_address, password)