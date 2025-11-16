from pymongo import MongoClient
from config import config
import os

print("=== DATABASE INIT ===")
print(f"MONGODB_URL configured: {bool(config.MONGODB_URL)}")

try:
    if not config.MONGODB_URL:
        print("❌ MONGODB_URL пустой")
        db = None
    else:
        print("🔄 Пытаемся подключиться...")
        # Добавляем таймаут
        client = MongoClient(config.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Проверяем подключение
        client.admin.command('ismaster')
        db = client.graffiti_wall
        
        print(f"✅ MongoDB подключена! База: {db.name}")
        print(f"📂 Коллекции: {db.list_collection_names()}")
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    db = None
