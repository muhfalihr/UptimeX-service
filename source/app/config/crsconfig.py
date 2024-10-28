from pydantic.v1 import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class BaseConfig(BaseSettings):
    VERSION: str
    SQLITE_DATABASE: str
    TOOLS_PATH: str
    PASSWORD_PATH: str
    CHECKER_TOOLS_PATH: str

    class Config:
        env = '.env'
