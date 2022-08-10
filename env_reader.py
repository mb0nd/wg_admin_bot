"""import os

class Settings():
    api_token: str = os.getenv('API_TOKEN')
    admin_id: str = os.getenv('ADMIN_ID')
    pg_url: str = os.getenv('PG_URL')
    listen_port: str = os.getenv('LISTEN_PORT')
env = Settings()
"""

from pydantic import BaseSettings, SecretStr, PostgresDsn

class Settings(BaseSettings):
    api_token: SecretStr
    admin_id: int
    pg_url: PostgresDsn
    listen_port: int
    path_to_wg: str
env = Settings()