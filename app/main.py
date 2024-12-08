from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.users import router as user_router
from app.routes.executors import router as executor_router
from app.routes.requests import router as request_router
from typing import Optional

# Создаем приложение FastAPI
app = FastAPI(
    title="Service Platform API",
    description="API для управления пользователями, исполнителями, запросами и авторизацией",
    version="1.0.0",
)

# Разрешаем CORS для доступа из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше ограничить разрешенные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Корневой эндпоинт
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в Service Platform API!"}

# Подключаем маршруты
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(executor_router, prefix="/executors", tags=["executors"])
app.include_router(request_router, prefix="/requests", tags=["requests"])

# Для запуска сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
