from fastapi import FastAPI
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, seed_data, run_migrations
from models import User
from routers import users, tasks, files, comments, auth, home
from settings import settings
from middlewares.auth_middleware import AuthMiddleware, get_password_hash


# Подключаем Jinja2-шаблоны
templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Система управления задачами для производства",
    version="1.0",
    debug=settings.DEBUG
)

# Подключаем Middleware
app.add_middleware(AuthMiddleware)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Подключение роутеров
app.include_router(home.router, tags=["Главная"])
app.include_router(users.router, tags=["Пользователи"])
app.include_router(tasks.router, tags=["Задачи"])
app.include_router(files.router, prefix="/files", tags=["Файлы"])
app.include_router(comments.router, prefix="/comments", tags=["Комментарии"])
app.include_router(auth.router, tags=["Авторизация"])

# Функция для создания администратора
def create_admin():
    with SessionLocal() as db:
        # Проверяем, существует ли уже администратор
        admin = db.query(User).filter(User.user_type == "Администратор").first()
        if not admin:  # Если администратора нет, создаём нового
            new_user = User(
                name="admin",
                username="admin",
                password=get_password_hash("admin"),  # Хешируем пароль
                user_type="Администратор"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
# Создаём администратора при старте приложения
create_admin()

# Дополнительные действия с базой данных
with SessionLocal() as db:
    seed_data(db)
    #run_migrations()  # Раскомментируйте, если нужно выполнить миграции

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)