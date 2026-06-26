"""Конфигурация приложения."""
from dataclasses import dataclass
from dotenv import load_dotenv
from os import environ

@dataclass
class DataBase:
    db_name: str
    db_user: str
    db_pass: str
    db_host: str
    db_port: int

@dataclass
class Api:
    host: str
    port: int
    url: str

@dataclass
class Config:
    db: DataBase
    api: Api

def get_config():
    load_dotenv()
    api_host = environ.get("API_HOST")
    api_port = int(environ.get("API_PORT"))
    api_url = f"http://{api_host}:{api_port}"
    
    return Config(
        db=DataBase(
            db_name=environ.get("DB_NAME"),
            db_user=environ.get("DB_USER"),
            db_pass=environ.get("DB_PASS"),
            db_host=environ.get("DB_HOST"),
            db_port=int(environ.get("DB_PORT")),
        ),
        api=Api(
            host=api_host,
            port=api_port,
            url=api_url,
        )
    )

config = get_config()