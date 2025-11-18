// Глобальные переменные для управления стеной
let wallScale = 1;
let isDragging = false;
let startX, startY, scrollLeft, scrollTop;
let initialDistance = null;
let currentUser = null;

// Инициализация пользователя Telegram
try {
    if (window.Telegram && Telegram.WebApp) {
        currentUser = Telegram.WebApp.initDataUnsafe.user;
    }
} catch (e) {
    console.log('Telegram Web App not available');
}

// Основная функция загрузки галереи
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
                createPhotoElement(photo, wall);
            });
        }
        
        document.getElementById('loading').style.display = 'none';
        
    } catch (error) {
        document.getElementById('loading').innerHTML = '❌ Ошибка загрузки галереи';
        console.error('Error:', error);
    }
}

// Создание элемента фото на стене
function createPhotoElement(photo, wall) {
    const photoElement = document.createElement('div');
    photoElement.className = 'photo';
    photoElement.style.left = photo.position_x + 'px';
    photoElement.style.top = photo.position_y + 'px';
    photoElement.style.width = '150px';
    photoElement.style.height = '150px';
    
    // Проверяем лайкнул ли пользователь это фото
    const userLiked = currentUser && photo.liked_by && photo.liked_by.includes(currentUser.id);
    
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
}

// Функция показа модалки с фото
async function showPhotoModal(photo, userLiked) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.8);
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
           <div style="position: absolute; bottom: 15px; left: 15px; background: rgba(0,0,0,0.0); padding: 10px 15px; border-radius: 10px;">
    <strong style="color: rgba(0,0,0,1.9);">@${photo.username}</strong><br>
    <span style="color: rgba(0,0,0,1.0);">❤️ ${photo.likes} лайков</span><br>
    <span style="color: rgba(0,0,0,1.9);">Позиция: ${photo.position_x}, ${photo.position_y}</span>
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

// Навигация по стене (зум и перетаскивание)
function setupWallNavigation() {
    const container = document.getElementById('wall-container');
    const wall = document.getElementById('wall');
    
    let isDragging = false;
    let startX, startY, scrollLeft, scrollTop;
    let initialDistance = null;
    let lastScale = wallScale;

    // Обработчики мыши
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

    // Обработчики тач-событий
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

    // Обработчик колеса мыши для зума
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = -e.deltaY * 0.002;
        wallScale = Math.min(Math.max(0.3, wallScale + delta), 3);
        updateWallScale();
    });
}

// Вспомогательные функции для навигации
function getDistance(touch1, touch2) {
    return Math.sqrt(
        Math.pow(touch2.pageX - touch1.pageX, 2) +
        Math.pow(touch2.pageY - touch1.pageY, 2)
    );
}

// Функции зума
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

// Анимация зума
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

// Обновление масштаба стены
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

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadGallery();
    setupWallNavigation();
    setTimeout(() => resetZoom(), 100);
});

// Автообновление галереи каждые 30 секунд
setInterval(loadGallery, 3000000);
