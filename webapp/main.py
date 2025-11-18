from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles  # Импортируем из starlette
from bson import ObjectId
from pydantic import BaseModel
from datetime import datetime
import os

# СНАЧАЛА создаем app
app = FastAPI(title="Graffiti Wall")

# Подключаем статические файлы (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ПОТОМ middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# И только ПОТОМ остальные импорты (если нужны)
try:
    from database import db
    print("✅ MongoDB подключена!")
except ImportError as e:
    print(f"❌ MongoDB не подключена: {e}")
    db = None

# Модели Pydantic для запросов (Pydantic v1 синтаксис)
class LikeRequest(BaseModel):
    photo_id: str
    user_id: int
    username: str

class DeleteRequest(BaseModel):
    photo_id: str
    user_id: int

# Маршруты API
@app.get("/")
async def root():
    """Перенаправление на главную страницу"""
    return RedirectResponse(url="/webapp")

@app.get("/webapp")
async def webapp_page():
    """Главная страница приложения"""
    # Читаем HTML из файла
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback если файл не найден
        return HTMLResponse(content="<h1>Static files not found</h1>")

@app.get("/api/top_users")
async def get_top_users():
    """API для получения топа пользователей"""
    try:
        from database import db
        if db is None:
            return []
        
        # Агрегация для топа пользователей
        pipeline = [
            {
                "$group": {
                    "_id": "$user_id",
                    "username": {"$first": "$username"},
                    "total_photos": {"$sum": 1},
                    "total_likes": {"$sum": "$likes"},
                    "avg_likes": {"$avg": "$likes"}
                }
            },
            {"$sort": {"total_likes": -1}},
            {"$limit": 10}
        ]
        
        top_users = list(db.photos.aggregate(pipeline))
        
        # Преобразуем результат
        for user in top_users:
            user['user_id'] = user['_id']
            del user['_id']
            
        return top_users
        
    except Exception as e:
        print(f"Top users error: {e}")
        return []

@app.get("/api/photos")
async def get_photos():
    """API для получения всех фотографий"""
    try:
        from database import db
        if db is None:
            return []
        
        photos = list(db.photos.find({}, {'image_data': 0}))
        
        for photo in photos:
            photo['_id'] = str(photo['_id'])
            photo.setdefault('likes', 0)
            photo.setdefault('liked_by', [])
            photo['image_url'] = f"/api/photo/{photo['_id']}"
            
        return photos
    except Exception as e:
        print(f"API Photos Error: {e}")
        return []

@app.get("/api/stats")
async def get_stats():
    """API для получения статистики"""
    try:
        from database import db
        if db is None:
            return {"total_photos": 0, "total_users": 0, "total_likes": 0}
        
        total_photos = db.photos.count_documents({})
        total_users = len(db.photos.distinct('user_id'))
        
        pipeline = [{"$group": {"_id": None, "total_likes": {"$sum": "$likes"}}}]
        result = list(db.photos.aggregate(pipeline))
        total_likes = result[0]['total_likes'] if result else 0
        
        return {
            "total_photos": total_photos,
            "total_users": total_users,
            "total_likes": total_likes
        }
    except Exception as e:
        print(f"API Stats Error: {e}")
        return {"total_photos": 0, "total_users": 0, "total_likes": 0}

@app.post("/api/like")
async def like_photo(request: LikeRequest):
    """API для лайка/анлайка фото"""
    try:
        from database import db
        if db is None:
            return {"success": False, "error": "Database not connected"}
        
        photo = db.photos.find_one({"_id": ObjectId(request.photo_id)})
        if not photo:
            return {"success": False, "error": "Photo not found"}
        
        liked_by = photo.get('liked_by', [])
        user_has_liked = request.user_id in liked_by
        
        if user_has_liked:
            db.photos.update_one(
                {"_id": ObjectId(request.photo_id)},
                {
                    "$inc": {"likes": -1},
                    "$pull": {"liked_by": request.user_id}
                }
            )
            new_likes = photo.get('likes', 1) - 1
        else:
            db.photos.update_one(
                {"_id": ObjectId(request.photo_id)},
                {
                    "$inc": {"likes": 1},
                    "$push": {"liked_by": request.user_id}
                }
            )
            new_likes = photo.get('likes', 0) + 1
        
        return {"success": True, "new_likes": new_likes}
        
    except Exception as e:
        print(f"Like error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/delete_photo")
async def delete_photo(request: DeleteRequest):
    """API для удаления фото (только для админов)"""
    try:
        from database import db
        
        if db is None:
            return {"success": False, "error": "Database not connected"}
        
        # Хардкод ID админов
        ADMIN_IDS = [1790615566]
        
        if request.user_id not in ADMIN_IDS:
            return {"success": False, "error": "Access denied"}
        
        result = db.photos.delete_one({"_id": ObjectId(request.photo_id)})
        
        if result.deleted_count > 0:
            return {"success": True}
        else:
            return {"success": False, "error": "Photo not found"}
            
    except Exception as e:
        print(f"Delete error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/is_admin/{user_id}")
async def check_admin(user_id: int):
    """API для проверки прав администратора"""
    try:
        user_id_int = int(user_id)
        ADMIN_IDS = [1790615566]
        is_admin = user_id_int in ADMIN_IDS
        
        return {
            "is_admin": is_admin,
            "user_id_received": user_id,
            "user_id_processed": user_id_int,
            "admin_ids": ADMIN_IDS
        }
    except Exception as e:
        return {"is_admin": False, "error": str(e)}

@app.get("/api/photo/{photo_id}")
async def get_photo(photo_id: str):
    """API для получения изображения по ID"""
    try:
        from database import db
        if db is None:
            return Response(content=b"", media_type="image/jpeg")
        
        photo = db.photos.find_one({"_id": ObjectId(photo_id)})
        if not photo or 'image_data' not in photo:
            return Response(content=b"", media_type="image/jpeg")
        
        image_data = photo['image_data']
        return Response(content=image_data, media_type="image/jpeg")
        
    except Exception as e:
        print(f"Photo endpoint error: {e}")
        return Response(content=b"", media_type="image/jpeg")

# Сервисные маршруты
@app.get("/ping")
async def ping():
    """Проверка работоспособности сервера"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    """Health check для мониторинга"""
    return {"status": "healthy"}

print("✅ Graffiti Wall сервер загружен!")
