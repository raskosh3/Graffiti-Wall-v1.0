from pymongo import MongoClient
from datetime import datetime
import uuid

client = MongoClient(Config.MONGODB_URL)
db = client.graffiti_wall


class Photo:
    def __init__(self, user_id: int, username: str, image_url: str, position: dict):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.username = username
        self.image_url = image_url
        self.position = position
        self.likes = 0
        self.liked_by = []
        self.created_at = datetime.utcnow()

    def save(self):
        db.photos.insert_one(self.__dict__)

    @staticmethod
    def get_all():
        return list(db.photos.find())