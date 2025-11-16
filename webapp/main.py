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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: "Segoe UI", sans-serif;
                color: white;
                min-height: 100vh;
                overflow-x: hidden;
            }
            .header {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            .stats {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .stat {
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 20px;
                backdrop-filter: blur(5px);
            }
            .gallery {
                padding: 20px;
                text-align: center;
            }
            .photo-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .photo-card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s;
            }
            .photo-card:hover {
                transform: translateY(-5px);
            }
            .photo-placeholder {
                background: #555;
                height: 120px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 10px;
            }
            .loading {
                text-align: center;
                padding: 50px;
                font-size: 1.2rem;
            }
            .btn {
                background: linear-gradient(45deg, #FF6B6B, #FF8E53);
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                cursor: pointer;
                margin: 10px;
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
        
        <div class="gallery">
            <button class="btn" onclick="loadGallery()">🔄 Обновить</button>
            
            <div class="loading" id="loading">⏳ Загружаем галерею...</div>
            
            <div class="photo-grid" id="photo-grid" style="display: none;">
                <!-- Фото будут здесь -->
            </div>
        </div>

        <script>
    async function loadGallery() {
        try {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('photo-grid').style.display = 'none';
            
            // Загружаем статистику
            const statsResponse = await fetch('/api/stats');
            const stats = await statsResponse.json();
            
            document.getElementById('total-photos').textContent = `📸 Фото: ${stats.total_photos}`;
            document.getElementById('total-users').textContent = `👥 Участники: ${stats.total_users}`;
            document.getElementById('total-likes').textContent = `❤️ Лайки: ${stats.total_likes}`;
            
            // Загружаем фото
            const photosResponse = await fetch('/api/photos');
            const photos = await photosResponse.json();
            
            const grid = document.getElementById('photo-grid');
            grid.innerHTML = '';
            
            if (photos.length === 0) {
                grid.innerHTML = '<div style="text-align: center; padding: 40px;">🎨 Пока нет фото на стене. Будьте первым!</div>';
            } else {
                photos.forEach(photo => {
                    const card = document.createElement('div');
                    card.className = 'photo-card';
                    card.innerHTML = `
                        <div class="photo-placeholder">
                            📸 Фото ${photo._id.slice(-4)}
                        </div>
                        <p><b>@${photo.username}</b></p>
                        <p>❤️ ${photo.likes} лайков</p>
                        <small>Позиция: ${photo.position_x}, ${photo.position_y}</small>
                    `;
                    grid.appendChild(card);
                });
            }
            
            document.getElementById('loading').style.display = 'none';
            grid.style.display = 'grid';
            
        } catch (error) {
            document.getElementById('loading').innerHTML = '❌ Ошибка загрузки галереи';
            console.error('Error:', error);
        }
    }
    
    // Автоматическая загрузка при открытии
    loadGallery();
    
    // Авто-обновление каждые 10 секунд
    setInterval(loadGallery, 10000);
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
        
        # Для MongoDB
        photos = list(db.photos.find({}))
        
        # Преобразуем ObjectId в строку для JSON
        for photo in photos:
            photo['_id'] = str(photo['_id'])
            # Убедимся что все нужные поля есть
            photo.setdefault('likes', 0)
            photo.setdefault('liked_by', [])
            
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

print("✅ webapp/main.py загружен! App создан.")




