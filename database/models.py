from pymongo import MongoClient
from datetime import datetime
import uuid
from database import db

class Photo:
    def __init__(self, user_id: int, username: str, image_data: bytes, position_x: int, position_y: int):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.username = username
        self.image_data = image_data  # Бинарные данные фото
        self.position_x = position_x
        self.position_y = position_y
        self.likes = 0
        self.liked_by = []
        self.created_at = datetime.utcnow()

    def save(self):
        if db is None:
            print("❌ DB не подключена!")
            return False
        try:
            db.photos.insert_one(self.__dict__)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения фото: {e}")
            return False

    @staticmethod
    def get_all():
        if db is None:
            return []
        try:
            return list(db.photos.find({}, {'image_data': 0}))  # Не грузим бинарные данные в списке
        except Exception as e:
            print(f"❌ Ошибка получения фото: {e}")
            return []
