from pydantic import BaseSettings, SecretStr, PostgresDsn


class Settings(BaseSettings):
    api_token: SecretStr
    admin_id: int
    pg_url: PostgresDsn
    listen_port: int
    path_to_wg: str
    host: str
env = Settings()