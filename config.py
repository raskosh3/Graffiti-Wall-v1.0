import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "")
    
config = Config()
