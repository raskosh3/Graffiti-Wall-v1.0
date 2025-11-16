from pymongo import MongoClient
from config import config

try:
    client = MongoClient(config.MONGODB_URL)
    db = client.graffiti_wall
    print("✅ MongoDB подключена!")
except Exception as e:
    print(f"❌ Ошибка подключения к MongoDB: {e}")
    db = None