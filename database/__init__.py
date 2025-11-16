from pymongo import MongoClient
from config import config
import os

try:
    mongodb_url = config.MONGODB_URL
    
    if not mongodb_url:
        print("❌ MONGODB_URL не настроен в Environment Variables")
        db = None
    else:
        client = MongoClient(mongodb_url)
        db = client.graffiti_wall
        print(f"✅ MongoDB подключена! База: {db.name}")
        
except Exception as e:
    print(f"❌ Ошибка подключения к MongoDB: {e}")
    db = None
