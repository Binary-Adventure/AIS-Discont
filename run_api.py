"""Запуск FastAPI сервера."""
import uvicorn
from config import config


if __name__ == "__main__":
    uvicorn.run(
        "Api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=True
    )
