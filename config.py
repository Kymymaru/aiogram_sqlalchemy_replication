from pydantic import BaseModel

from typing import List, Optional
import json


class WebhookConfig(BaseModel):
    url: str
    host: str
    port: int
    path: str


class BotConfig(BaseModel):
    token: str
    polling: bool
    use_redis: bool
    skip_updates: bool
    webhook: WebhookConfig
    username: Optional[str]

    class Config:
        extra = 'allow'


class DbConnection(BaseModel):
    user: str
    password: str
    host: str
    database: str


class DatabaseConfig(BaseModel):
    master: DbConnection
    slaves: List[DbConnection]
    debug: bool

    class Config:
        extra = 'allow'


class RedisConfig(BaseModel):
    host: str
    db: int

    class Config:
        extra = 'allow'


class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
    redis: RedisConfig

    class Config:
        extra = 'allow'

    @staticmethod
    def load_settings():
        # Загрузка конфигурации из JSON файла
        with open('settings.json') as f:
            config_data = json.load(f)
            return Config(**config_data)

    def save_settings(self):
        # Преобразование данных модели в словарь
        config_dict = self.model_dump()

        # Сохранение данных в JSON файл
        with open('settings.json', 'w') as f:
            json.dump(config_dict, f, indent=4)
