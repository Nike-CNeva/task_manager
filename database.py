from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from alembic import command
from alembic.config import Config
from settings import settings
from sqlalchemy import event
from sqlalchemy.engine import Engine
# ---------------------------
# ⚙️ Параметры подключения
# ---------------------------

# 🔽 Адрес базы данных
# Пример для SQLite (тестовая локальная база), позже можно заменить на PostgreSQL или MySQL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# ---------------------------
# 🚀 Создание движка БД
# ---------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# ---------------------------
# 🧠 Создание фабрики сессий
# ---------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ---------------------------
# 📦 Базовый класс для моделей
# ---------------------------
Base = declarative_base()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для применения миграций через Alembic
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

# Функция для отката миграций через Alembic
def downgrade_migrations():
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")

def seed_data(db):
    from models import Product, ProductTypeEnum, Workshop, WorkshopEnum, ProfileType, ProfileTypeEnum
    if not db.query(Workshop).first():
        # Заполнение таблицы Workshop
        for workshop in WorkshopEnum:
            exists = db.query(Workshop).filter_by(name=workshop).first()
            if not exists:
                db.add(Workshop(name=workshop))
                db.commit()
                
    if not db.query(ProfileType).first():
        # Перебираем все значения перечисления ProfileTypeEnum и добавляем их в таблицу
        for profile_name in ProfileTypeEnum:
            # Проверка, если такой тип уже существует
            exists = db.query(ProfileType).filter_by(name = profile_name).first()
            if not exists:
                db.add(ProfileType(name=profile_name))
                db.commit()
    
