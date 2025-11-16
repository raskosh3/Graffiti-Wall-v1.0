class GraffitiGallery {
    constructor() {
        this.canvas = document.getElementById('main-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.photos = [];
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.lastX = 0;
        this.lastY = 0;

        this.init();
    }

    async init() {
        try {
            await this.loadPhotos();
            this.setupEventListeners();
            this.render();
            this.hideLoading();
        } catch (error) {
            console.error('Error initializing gallery:', error);
        }
    }

    async loadPhotos() {
        const response = await fetch('/api/photos');
        this.photos = await response.json();
        this.resizeCanvas();
    }

    resizeCanvas() {
        // Находим максимальные координаты
        const maxX = Math.max(...this.photos.map(p => p.x + p.width), 2000);
        const maxY = Math.max(...this.photos.map(p => p.y + p.height), 2000);

        this.canvas.width = maxX;
        this.canvas.height = maxY;
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Рисуем сетку фона
        this.drawGrid();

        // Рисуем все фото
        this.photos.forEach(photo => {
            this.drawPhoto(photo);
        });
    }

    drawGrid() {
        this.ctx.strokeStyle = '#444';
        this.ctx.lineWidth = 1;

        // Вертикальные линии
        for (let x = 0; x <= this.canvas.width; x += 100) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        // Горизонтальные линии
        for (let y = 0; y <= this.canvas.height; y += 100) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawPhoto(photo) {
        // Прямоугольник для фото
        this.ctx.fillStyle = '#555';
        this.ctx.fillRect(photo.x, photo.y, photo.width, photo.height);

        // Текст с именем пользователя
        this.ctx.fillStyle = 'white';
        this.ctx.font = '12px Arial';
        this.ctx.fillText(
            `@${photo.username} (${photo.likes}❤️)`,
            photo.x + 5,
            photo.y + 15
        );

        // ID фото
        this.ctx.fillStyle = '#ccc';
        this.ctx.font = '10px Arial';
        this.ctx.fillText(
            `ID: ${photo.id}`,
            photo.x + 5,
            photo.y + 30
        );
    }

    setupEventListeners() {
        // Перетаскивание canvas
        this.canvas.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.lastX = e.clientX;
            this.lastY = e.clientY;
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const deltaX = e.clientX - this.lastX;
                const deltaY = e.clientY - this.lastY;

                this.offsetX += deltaX;
                this.offsetY += deltaY;

                this.lastX = e.clientX;
                this.lastY = e.clientY;

                this.canvas.style.transform = `translate(${this.offsetX}px, ${this.offsetY}px)`;
            }
        });

        this.canvas.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.isDragging = false;
        });
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
}

// Инициализация когда DOM загружен
document.addEventListener('DOMContentLoaded', () => {
    new GraffitiGallery();
});