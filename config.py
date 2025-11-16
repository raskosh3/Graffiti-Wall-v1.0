import os
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "ТВОЙ_ТОКЕН")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://your-app.onrender.com")


config = Config()