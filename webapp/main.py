from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId, Binary

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
        cursor: pointer;
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
    background: rgba(0,0,0,0.3); /* Было 0.7, стало 0.5 - прозрачнее */
    color: white;
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 0.7rem;
    backdrop-filter: blur(5px);
    pointer-events: none;
    opacity: 0.4; /* Добавляем общую прозрачность */
}

.photo-likes {
    position: absolute;
    top: 5px;
    right: 5px;
    background: rgba(0,0,0,0.3); /* Было 0.7 */
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 0.6rem;
    backdrop-filter: blur(5px);
    pointer-events: none;
    opacity: 0.4;
}
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
        transition: all 0.2s ease;
    }
    
    .zoom-btn:active {
        background: rgba(255,255,255,0.2);
        transform: scale(0.95);
    }
    
    /* Кнопки действий в модалке */
    .action-buttons {
        position: absolute;
        top: 20px;
        right: 20px;
        display: flex;
        gap: 10px;
        z-index: 10001;
    }
    
    .action-btn {
    background: rgba(0,0,0,0.6); /* Было 0.7 */
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 20px;
    cursor: pointer;
    backdrop-filter: blur(10px);
    font-size: 0.9rem;
    transition: all 0.2s ease;
    opacity: 0.3;
}
    
    .action-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    
    .like-btn {
        background: rgba(255,0,0,0.7);
    }
    
    .like-btn.liked {
        background: rgba(255,0,0,0.9);
    }
    
    .delete-btn {
        background: rgba(255,0,0,0.7);
    }
    
    /* Скрыть контролы на десктопе */
    @media (min-width: 768px) {
        .mobile-controls {
            display: flex;
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
            <button class="zoom-btn" onclick="zoomIn()" title="Приблизить">+</button>
            <button class="zoom-btn" onclick="zoomOut()" title="Отдалить">-</button>
            <button class="zoom-btn" onclick="resetZoom()" title="Сбросить зум" style="font-size:16px;">⟲</button>
            <button class="zoom-btn" onclick="showFullWall()" title="Показать всю стену" style="font-size:14px;">🏞️</button>
        </div>
            
        <div class="loading" id="loading">⏳ Загружаем галерею...</div>

        <script>
let wallScale = 1;
let isDragging = false;
let startX, startY, scrollLeft, scrollTop;
let initialDistance = null;
let currentUser = null;

// Получаем данные пользователя из Telegram Web App
try {
    if (window.Telegram && Telegram.WebApp) {
        currentUser = Telegram.WebApp.initDataUnsafe.user;
    }
} catch (e) {
    console.log('Telegram Web App not available');
}

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
                
                // Проверяем лайкнул ли пользователь это фото
                const userLiked = currentUser && photo.liked_by && photo.liked_by.includes(currentUser.id);
                
                // РЕАЛЬНЫЕ ФОТО ИЗ MONGODB
                photoElement.innerHTML = `
                    <img src="${photo.image_url}" 
                         alt="Фото от @${photo.username}" 
                         loading="lazy"
                         style="width:100%;height:100%;object-fit:cover;border-radius:8px;">
                    <div class="photo-credits">@${photo.username}</div>
                    <div class="photo-likes">❤️ ${photo.likes}</div>
                `;
                
                // Добавляем клик для открытия модалки
                photoElement.onclick = (e) => {
                    e.stopPropagation();
                    showPhotoModal(photo, userLiked);
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

// Функция показа модалки с фото и кнопками
async function showPhotoModal(photo, userLiked) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.8); // фон сзади 
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: zoom-out;
    `;
    
    // Проверяем является ли пользователь админом
    let isAdmin = false;
    if (currentUser) {
        try {
            const response = await fetch(`/api/is_admin/${currentUser.id}`);
            const result = await response.json();
            isAdmin = result.is_admin;
        } catch (error) {
            console.error('Admin check error:', error);
        }
    }
    
    modal.innerHTML = `
        <div style="max-width: 90vw; max-height: 90vh; position: relative;">
            <img src="${photo.image_url}" 
                 alt="Фото от @${photo.username}"
                 style="max-width: 90vw; max-height: 90vh; border-radius: 15px;">
            <div class="action-buttons">
                <button class="action-btn like-btn ${userLiked ? 'liked' : ''}" onclick="likePhoto('${photo._id}', this)">
                    ❤️ ${photo.likes}
                </button>
                ${isAdmin ? `<button class="action-btn delete-btn" onclick="deletePhoto('${photo._id}')">🗑️ Удалить</button>` : ''}
            </div>
           <div style="position: absolute; bottom: 20px; left: 20px; background: rgba(0,0,0,0.0); padding: 10px 15px; border-radius: 10px;">
    <strong style="color: rgba(128,128,128,0.8);">@${photo.username}</strong><br>
    <span style="color: rgba(128,128,128,0.8);">❤️ ${photo.likes} лайков</span><br>
    <span style="color: rgba(128,128,128,0.8);">Позиция: ${photo.position_x}, ${photo.position_y}</span>
</div>
        </div>
    `;
    
    modal.onclick = () => document.body.removeChild(modal);
    document.body.appendChild(modal);
}

// Функция лайка фото
async function likePhoto(photoId, button) {
    if (!currentUser) {
        alert('⚠️ Необходимо открыть через Telegram бота для лайков');
        return;
    }
    
    try {
        const response = await fetch('/api/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                photo_id: photoId,
                user_id: currentUser.id,
                username: currentUser.username || `user_${currentUser.id}`
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            button.classList.toggle('liked');
            button.innerHTML = `❤️ ${result.new_likes}`;
            loadGallery();
        } else {
            alert('❌ ' + result.error);
        }
    } catch (error) {
        console.error('Like error:', error);
        alert('❌ Ошибка при лайке');
    }
}

// Функция удаления фото (для админа)
async function deletePhoto(photoId) {
    if (!currentUser) {
        alert('⚠️ Необходимо открыть через Telegram бота');
        return;
    }
    
    if (!confirm('🗑️ Удалить это фото?')) return;
    
    try {
        const response = await fetch('/api/delete_photo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                photo_id: photoId,
                user_id: currentUser.id
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Фото удалено');
            document.body.removeChild(document.body.lastChild);
            loadGallery();
        } else {
            alert('❌ ' + result.error);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('❌ Ошибка при удалении');
    }
}

// Функция показа всей стены
function showFullWall() {
    const container = document.getElementById('wall-container');
    const wall = document.getElementById('wall');
    
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const wallWidth = 2000;
    const wallHeight = 2000;
    
    const scaleX = containerWidth / wallWidth;
    const scaleY = containerHeight / wallHeight;
    const minScale = Math.min(scaleX, scaleY) * 0.9;
    
    wallScale = Math.max(minScale, 0.1);
    updateWallScale();
    
    container.scrollLeft = (wallWidth * wallScale - containerWidth) / 2;
    container.scrollTop = (wallHeight * wallScale - containerHeight) / 2;
}

// Функции для навигации по стене
function setupWallNavigation() {
    const container = document.getElementById('wall-container');
    const wall = document.getElementById('wall');
    
    let isDragging = false;
    let startX, startY, scrollLeft, scrollTop;
    let initialDistance = null;
    let lastScale = wallScale;

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

    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            isDragging = true;
            startX = e.touches[0].pageX - container.offsetLeft;
            startY = e.touches[0].pageY - container.offsetTop;
            scrollLeft = container.scrollLeft;
            scrollTop = container.scrollTop;
        } else if (e.touches.length === 2) {
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
            e.preventDefault();
            const x = e.touches[0].pageX - container.offsetLeft;
            const y = e.touches[0].pageY - container.offsetTop;
            const walkX = (x - startX) * 2;
            const walkY = (y - startY) * 2;
            container.scrollLeft = scrollLeft - walkX;
            container.scrollTop = scrollTop - walkY;
        } else if (e.touches.length === 2 && initialDistance !== null) {
            e.preventDefault();
            const currentDistance = getDistance(e.touches[0], e.touches[1]);
            const scaleChange = (currentDistance - initialDistance) * 0.001;
            
            wallScale = Math.min(Math.max(0.3, lastScale + scaleChange), 3);
            updateWallScale();
        }
    });

    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = -e.deltaY * 0.002;
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
    setTimeout(() => {
        const container = document.getElementById('wall-container');
        container.scrollLeft = 500;
        container.scrollTop = 500;
    }, 300);
}

function animateZoom(targetScale) {
    const wall = document.getElementById('wall');
    const startScale = wallScale;
    const duration = 300;
    const startTime = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        wallScale = startScale + (targetScale - startScale) * easeProgress;
        updateWallScale();
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function updateWallScale() {
    const wall = document.getElementById('wall');
    wall.style.transform = `scale(${wallScale})`;
    wall.style.transformOrigin = '0 0';
    
    const container = document.getElementById('wall-container');
    if (wallScale > 1) {
        container.style.cursor = 'grab';
    } else {
        container.style.cursor = 'default';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadGallery();
    setupWallNavigation();
    setTimeout(() => resetZoom(), 100);
});

setInterval(loadGallery, 30000);
</script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@app.get("/")
async def root():
    return RedirectResponse(url="/webapp")
    
@app.get("/api/top_users")
async def get_top_users():
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

from pydantic import BaseModel

class LikeRequest(BaseModel):
    photo_id: str
    user_id: int
    username: str

class DeleteRequest(BaseModel):
    photo_id: str
    user_id: int

@app.post("/api/like")
async def like_photo(request: LikeRequest):
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
    try:
        from database import db
        from config import config
        
        if db is None:
            return {"success": False, "error": "Database not connected"}
        
        # ПРОСТОЙ ХАРДКОД - ЛЮБОЙ С ЭТИМ ID МОЖЕТ УДАЛЯТЬ
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

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/photo/{photo_id}")
async def get_photo(photo_id: str):
    try:
        from database import db
        if db is None:
            return Response(content=b"", media_type="image/jpeg")
        
        photo = db.photos.find_one({"_id": ObjectId(photo_id)})
        if not photo or 'image_data' not in photo:
            return Response(content=b"", media_type="image/jpeg")
        
        image_data = photo['image_data']
        if isinstance(image_data, Binary):
            image_data = image_data
        
        return Response(content=image_data, media_type="image/jpeg")
        
    except Exception as e:
        print(f"Photo endpoint error: {e}")
        return Response(content=b"", media_type="image/jpeg")
        
print("✅ webapp/main.py загружен! App создан.")







