import functools
import asyncio
import aiosqlite

def async_error_handler_sqlite(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                raise
            else:
                raise
    return wrapper