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

# И только ПОТОМ остальные импорты (если нужны)
try:
    from database import db
    print("✅ MongoDB подключена!")
except ImportError as e:
    print(f"❌ MongoDB не подключена: {e}")
    db = None

@app.get("/webapp")
async def webapp_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎨 Graffiti Wall</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 20px;
            }
            .status {
                background: green;
                padding: 10px 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Graffiti Wall</h1>
            <div class="status">✅ Web App успешно запущен!</div>
            <p>Скоро здесь будет интерактивная галерея</p>
            <p>Бот подключается...</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
async def home():
    return {"status": "success", "message": "Graffiti Wall API работает!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

print("✅ webapp/main.py загружен! App создан.")
