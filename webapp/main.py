from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# СНАЧАЛА создаем app
app = FastAPI(title="Graffiti Wall")

# ПОТОМ middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.responses import RedirectResponse

# И только ПОТОМ остальные импорты (если нужны)
try:
    from database import db
    print("✅ MongoDB подключена!")
except ImportError as e:
    print(f"❌ MongoDB не подключена: {e}")
    db = None

@app.get("/webapp")
async def webapp_page():
    html_content = '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎨 Graffiti Wall</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    body {
        background: #1a1a1a;
        font-family: "Segoe UI", sans-serif;
        color: white;
        overflow: hidden;
    }
    .header {
        background: rgba(0,0,0,0.9);
        padding: 10px;
        text-align: center;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 1000;
        backdrop-filter: blur(10px);
        height: 80px; /* Фиксированная высота */
    }

.wall-container {
    margin-top: 80px; /* Уменьши отступ */
    height: calc(100vh - 80px);
}
    .stats {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 10px 0;
        flex-wrap: wrap;
    }
    .stat {
        background: rgba(255,255,255,0.1);
        padding: 8px 16px;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .wall-container {
        margin-top: 120px;
        overflow: scroll;
        width: 100vw;
        height: calc(100vh - 120px);
        cursor: grab;
    }
    .wall {
        position: relative;
        width: 2000px;
        height: 2000px;
        background: #2d2d2d;
    }
    .photo {
        position: absolute;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .photo:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        z-index: 100;
    }
    .photo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .photo-credits {
        position: absolute;
        bottom: 5px;
        left: 5px;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        backdrop-filter: blur(5px);
    }
    .loading {
        text-align: center;
        padding: 50px;
        font-size: 1.2rem;
    }
    .btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        margin: 5px;
    }
</style>
    </head>
    <body>
        <div class="header">
            <h1>🎨 Graffiti Wall</h1>
            <p>Интерактивная галерея фотографий</p>
        </div>
        
        <div class="stats">
            <div class="stat" id="total-photos">📸 Фото: 0</div>
            <div class="stat" id="total-users">👥 Участники: 0</div>
            <div class="stat" id="total-likes">❤️ Лайки: 0</div>
        </div>
        
       <div class="wall-container" id="wall-container">
    <div class="wall" id="wall"></div>
</div>
            
            <div class="loading" id="loading">⏳ Загружаем галерею...</div>
            
            <div class="photo-grid" id="photo-grid" style="display: none;">
                <!-- Фото будут здесь -->
            </div>
        </div>

        <script>
    let wallScale = 1;
let isDragging = false;
let startX, startY, scrollLeft, scrollTop;

async function loadGallery() {
    try {
        document.getElementById('loading').style.display = 'block';
        
        // Загружаем статистику
        const statsResponse = await fetch('/api/stats');
        const stats = await statsResponse.json();
        
        document.getElementById('total-photos').textContent = `📸 Фото: ${stats.total_photos}`;
        document.getElementById('total-users').textContent = `👥 Участники: ${stats.total_users}`;
        document.getElementById('total-likes').textContent = `❤️ Лайки: ${stats.total_likes}`;
        
        // Загружаем фото
        const photosResponse = await fetch('/api/photos');
        const photos = await photosResponse.json();
        
        const wall = document.getElementById('wall');
        wall.innerHTML = '';
        
        if (photos.length === 0) {
            wall.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;">🎨 Пока нет фото на стене. Будьте первым!</div>';
        } else {
            photos.forEach(photo => {
                const photoElement = document.createElement('div');
                photoElement.className = 'photo';
                photoElement.style.left = photo.position_x + 'px';
                photoElement.style.top = photo.position_y + 'px';
                photoElement.style.width = '150px';
                photoElement.style.height = '150px';
                
               // РЕАЛЬНЫЕ ФОТО ИЗ MONGODB
            photoElement.innerHTML = `
                <img src="${photo.image_url}" 
                     alt="Фото от @${photo.username}" 
                     loading="lazy"
                     style="width:100%;height:100%;object-fit:cover;border-radius:8px;">
                <div class="photo-credits">@${photo.username}</div>
            `;
                
                // Добавляем зум при клике
                photoElement.onclick = (e) => {
                    e.stopPropagation();
                    zoomPhoto(photo);
                };
                
                wall.appendChild(photoElement);
            });
        }
        
        document.getElementById('loading').style.display = 'none';
        
    } catch (error) {
        document.getElementById('loading').innerHTML = '❌ Ошибка загрузки галереи';
        console.error('Error:', error);
    }
}

// Функция зума фото
function zoomPhoto(photo) {
    // Создаем модальное окно для просмотра фото
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: zoom-out;
    `;
    
   modal.innerHTML = `
    <div style="max-width: 90vw; max-height: 90vh; position: relative;">
        <img src="${photo.image_url}" 
             alt="Фото от @${photo.username}"
             style="max-width: 90vw; max-height: 90vh; border-radius: 15px;">
        <div style="position: absolute; bottom: 20px; left: 20px; background: rgba(0,0,0,0.7); color: white; padding: 10px 15px; border-radius: 10px;">
            <strong>@${photo.username}</strong><br>
            ❤️ ${photo.likes} лайков<br>
            Позиция: ${photo.position_x}, ${photo.position_y}
        </div>
    </div>
`;
    
    modal.onclick = () => document.body.removeChild(modal);
    document.body.appendChild(modal);
}

// Функции для навигации по стене
function setupWallNavigation() {
    const container = document.getElementById('wall-container');
    
    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.pageX - container.offsetLeft;
        startY = e.pageY - container.offsetTop;
        scrollLeft = container.scrollLeft;
        scrollTop = container.scrollTop;
        container.style.cursor = 'grabbing';
    });
    
    container.addEventListener('mouseup', () => {
        isDragging = false;
        container.style.cursor = 'grab';
    });
    
    container.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const y = e.pageY - container.offsetTop;
        const walkX = (x - startX) * 2;
        const walkY = (y - startY) * 2;
        container.scrollLeft = scrollLeft - walkX;
        container.scrollTop = scrollTop - walkY;
    });
    
    // Zoom колесиком мыши
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = -e.deltaY * 0.01;
        wallScale = Math.min(Math.max(0.5, wallScale + delta), 3);
        
        const wall = document.getElementById('wall');
        wall.style.transform = `scale(${wallScale})`;
        wall.style.transformOrigin = '0 0';
    });
}

// Автоматическая загрузка при открытии
document.addEventListener('DOMContentLoaded', function() {
    loadGallery();
    setupWallNavigation();
});

// Авто-обновление каждые 10 секунд
setInterval(loadGallery, 10000000);
</script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)



@app.get("/")
async def root():
    # Редирект с главной на /webapp
    return RedirectResponse(url="/webapp")
    
@app.get("/api/photos")
async def get_photos():
    try:
        from database import db
        if db is None:
            return []
        
        # Не загружаем image_data чтобы не перегружать список
        photos = list(db.photos.find({}, {'image_data': 0}))
        
        for photo in photos:
            photo['_id'] = str(photo['_id'])
            photo.setdefault('likes', 0)
            photo.setdefault('liked_by', [])
            # Добавляем URL для получения фото
            photo['image_url'] = f"/api/photo/{photo['_id']}"
            
        return photos
    except Exception as e:
        print(f"API Photos Error: {e}")
        return []

@app.get("/api/stats")
async def get_stats():
    try:
        from database import db
        if db is None:
            return {"total_photos": 0, "total_users": 0, "total_likes": 0}
        
        # Для MongoDB
        total_photos = db.photos.count_documents({})
        total_users = len(db.photos.distinct('user_id'))
        
        # Считаем общее количество лайков
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
        
@app.get("/health")
async def health():
    return {"status": "healthy"}
    
@app.get("/check-mongo")
async def check_mongo():
    from config import config
    import urllib.parse
    
    # Скрываем пароль для безопасности
    safe_url = config.MONGODB_URL
    if safe_url and "@" in safe_url:
        # Заменяем пароль на ****
        parts = safe_url.split("@")
        user_pass = parts[0].split("//")[1]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            safe_url = safe_url.replace(user_pass, f"{user}:****")
    
    return {
        "mongodb_url_safe": safe_url,
        "url_length": len(config.MONGODB_URL)
    }
from fastapi import Response

from bson import ObjectId, Binary
@app.get("/api/photo/{photo_id}")
async def get_photo(photo_id: str):
    try:
        from database import db
        if db is None:
            return Response(content=b"", media_type="image/jpeg")
        
        # ПРЕОБРАЗУЕМ строку в ObjectId
        photo = db.photos.find_one({"_id": ObjectId(photo_id)})
        if not photo or 'image_data' not in photo:
            return Response(content=b"", media_type="image/jpeg")
        
        # Возвращаем бинарные данные фото
        image_data = photo['image_data']
        if isinstance(image_data, Binary):
            image_data = image_data  # Binary объект от pymongo
        
        return Response(content=image_data, media_type="image/jpeg")
        
    except Exception as e:
        print(f"Photo endpoint error: {e}")
        return Response(content=b"", media_type="image/jpeg")
        
@app.get("/debug/db")
async def debug_db():
    try:
        from database import db
        from config import config
        
        info = {
            "mongodb_url_configured": bool(config.MONGODB_URL),
            "mongodb_url_length": len(config.MONGODB_URL) if config.MONGODB_URL else 0,
            "db_connected": db is not None,
            "db_name": db.name if db else None
        }
        
        if db:
            # Проверяем коллекции
            collections = db.list_collection_names()
            info["collections"] = collections
            
            if "photos" in collections:
                photos_count = db.photos.count_documents({})
                info["photos_count"] = photos_count
                
                # Покажем несколько фото
                photos = list(db.photos.find().limit(3))
                info["sample_photos"] = [
                    {
                        "username": p.get("username"),
                        "position": f"{p.get('position_x')},{p.get('position_y')}",
                        "likes": p.get("likes", 0)
                    }
                    for p in photos
                ]
        
        return info
        
    except Exception as e:
        return {"error": str(e)}
        
print("✅ webapp/main.py загружен! App создан.")










