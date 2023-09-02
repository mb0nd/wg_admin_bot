from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_token: SecretStr
    admin_id: int
    pg_url: str
    listen_port: int
    path_to_wg: str
    host: str
env = Settings()