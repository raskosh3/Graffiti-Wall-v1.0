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
        touch-action: none;
    }
    .header {
        background: rgba(0,0,0,0.95);
        padding: 8px 15px;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 1000;
        backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        height: auto;
        min-height: 70px;
    }

    .stats {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 5px 0;
        flex-wrap: wrap;
    }

    .stat {
        background: rgba(255,255,255,0.15);
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .wall-container {
        margin-top: 80px;
        height: calc(100vh - 80px);
        overflow: scroll;
        cursor: grab;
        -webkit-overflow-scrolling: touch;
    }
    .wall {
        position: relative;
        width: 2000px;
        height: 2000px;
        background: #2d2d2d;
        transition: transform 0.1s ease-out;
    }
    .photo {
        position: absolute;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        touch-action: none;
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
        pointer-events: none;
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
        pointer-events: none;
    }
    .loading {
        text-align: center;
        padding: 50px;
        font-size: 1.2rem;
    }
    
    /* Мобильные контролы */
    .mobile-controls {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .zoom-btn {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(0,0,0,0.8);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        font-size: 20px;
        cursor: pointer;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        user-select: none;
    }
    
    .zoom-btn:active {
        background: rgba(255,255,255,0.2);
    }
    
    /* Скрыть контролы на десктопе */
    @media (min-width: 768px) {
        .mobile-controls {
            display: none;
        }
    }
</style>
    </head>
    <body>
        <div class="header">
            <h1>🎨 Graffiti Wall</h1>
            <p>Интерактивная галерея фотографий</p>
            <div class="stats">
                <div class="stat" id="total-photos">📸 Фото: 0</div>
                <div class="stat" id="total-users">👥 Участники: 0</div>
                <div class="stat" id="total-likes">❤️ Лайки: 0</div>
            </div>
        </div>
        
        <div class="wall-container" id="wall-container">
            <div class="wall" id="wall"></div>
        </div>
        
        <!-- Мобильные контролы -->
        <div class="mobile-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">-</button>
            <button class="zoom-btn" onclick="resetZoom()" style="font-size:16px;">⟲</button>
        </div>
            
        <div class="loading" id="loading">⏳ Загружаем галерею...</div>

        <script>
let wallScale = 1;
let isDragging = false;
let startX, startY, scrollLeft, scrollTop;
let initialDistance = null;

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
    const wall = document.getElementById('wall');
    
    let isDragging = false;
    let startX, startY, scrollLeft, scrollTop;
    let initialDistance = null;
    let lastScale = wallScale;

    // Desktop события
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

    // Touch события для мобильных
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            isDragging = true;
            startX = e.touches[0].pageX - container.offsetLeft;
            startY = e.touches[0].pageY - container.offsetTop;
            scrollLeft = container.scrollLeft;
            scrollTop = container.scrollTop;
        } else if (e.touches.length === 2) {
            // Pinch to zoom - запоминаем начальное расстояние
            isDragging = false;
            initialDistance = getDistance(e.touches[0], e.touches[1]);
            lastScale = wallScale;
        }
    });

    container.addEventListener('touchend', () => {
        isDragging = false;
        initialDistance = null;
    });

    container.addEventListener('touchmove', (e) => {
        if (e.touches.length === 1 && isDragging) {
            // Перетаскивание одним пальцем
            e.preventDefault();
            const x = e.touches[0].pageX - container.offsetLeft;
            const y = e.touches[0].pageY - container.offsetTop;
            const walkX = (x - startX) * 2;
            const walkY = (y - startY) * 2;
            container.scrollLeft = scrollLeft - walkX;
            container.scrollTop = scrollTop - walkY;
        } else if (e.touches.length === 2 && initialDistance !== null) {
            // Pinch to zoom - плавный зум
            e.preventDefault();
            const currentDistance = getDistance(e.touches[0], e.touches[1]);
            const scaleChange = (currentDistance - initialDistance) * 0.001; // Уменьшил чувствительность
            
            // Плавное изменение масштаба
            wallScale = Math.min(Math.max(0.3, lastScale + scaleChange), 3);
            updateWallScale();
        }
    });

    // Zoom колесиком мыши (тоже уменьшил чувствительность)
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = -e.deltaY * 0.002; // Еще меньше чувствительность
        wallScale = Math.min(Math.max(0.3, wallScale + delta), 3);
        updateWallScale();
    });
}

function getDistance(touch1, touch2) {
    return Math.sqrt(
        Math.pow(touch2.pageX - touch1.pageX, 2) +
        Math.pow(touch2.pageY - touch1.pageY, 2)
    );
}

// Функции зума с плавной анимацией
function zoomIn() {
    const targetScale = Math.min(wallScale + 0.2, 3);
    animateZoom(targetScale);
}

function zoomOut() {
    const targetScale = Math.max(wallScale - 0.2, 0.3);
    animateZoom(targetScale);
}

function resetZoom() {
    animateZoom(1);
    // Центрируем вид
    setTimeout(() => {
        const container = document.getElementById('wall-container');
        container.scrollLeft = 500;
        container.scrollTop = 500;
    }, 300);
}

// Плавная анимация зума
function animateZoom(targetScale) {
    const wall = document.getElementById('wall');
    const startScale = wallScale;
    const duration = 300; // мс
    const startTime = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // easing function для плавности
        const easeProgress = easeOutCubic(progress);
        
        wallScale = startScale + (targetScale - startScale) * easeProgress;
        updateWallScale();
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

// Easing function для плавной анимации
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

function updateWallScale() {
    const wall = document.getElementById('wall');
    wall.style.transform = `scale(${wallScale})`;
    wall.style.transformOrigin = '0 0';
    
    // Обновляем курсор в зависимости от масштаба
    const container = document.getElementById('wall-container');
    if (wallScale > 1) {
        container.style.cursor = 'grab';
    } else {
        container.style.cursor = 'default';
    }
}

// Автоматическая загрузка при открытии
document.addEventListener('DOMContentLoaded', function() {
    loadGallery();
    setupWallNavigation();
    // Центрируем при загрузке
    setTimeout(() => resetZoom(), 100);
});

// Авто-обновление каждые 30 секунд
setInterval(loadGallery, 3000000);
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
        
        if db is not None:
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

