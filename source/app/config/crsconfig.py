from pydantic.v1 import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class BaseConfig(BaseSettings):
    VERSION: str
    SQLITE_DATABASE: str
    TOOLS_PATH: str
    CHECKER_PATH: str

    class Config:
        env = '.env'
