from sqlalchemy.orm import Session
from fastapi import Form, HTTPException
from middlewares.auth_middleware import get_password_hash
from models import User, UserTypeEnum, Workshop

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data, workshop_ids):
    # Проверка, существует ли пользователь с таким именем
    if get_user_by_username(db, user_data["username"]):
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    # Хешируем пароль
    hashed_password = get_password_hash(user_data["password"])

    # Преобразуем user_type в Enum (если он передан строкой)
    if isinstance(user_data["user_type"], str):
        try:
            user_type_enum = UserTypeEnum(user_data["user_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректный тип пользователя: {user_data['user_type']}")
    else:
        user_type_enum = user_data["user_type"]

    # Создаем пользователя
    new_user = User(
        name=user_data["name"],
        username=user_data["username"],
        password=hashed_password,
        user_type=user_type_enum,
    )

    # Получаем объекты цехов
    if workshop_ids:
        workshops = db.query(Workshop).filter(Workshop.id.in_(workshop_ids)).all()

        # Проверяем, все ли цеха найдены
        if len(workshops) != len(workshop_ids):
            raise HTTPException(status_code=400, detail="Один или несколько цехов не найдены")

        # Устанавливаем связь пользователя с цехами
        new_user.workshops.extend(workshops)

    # Добавляем пользователя в БД
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def update_user(db: Session, user_data, workshop_ids):
    user = db.query(User).filter(User.id == user_data.get("id")).first()
    # Преобразуем user_type в Enum (если он передан строкой)
    if isinstance(user_data["user_type"], str):
        try:
            user_type_enum = UserTypeEnum(user_data["user_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректный тип пользователя: {user_data['user_type']}")
    else:
        user_type_enum = user_data["user_type"]
    
    # Обновляем данные пользователя
    user.name = user_data.get("name")
    user.username = user_data.get("username")
    user.user_type = user_type_enum
    user.is_active = user_data.get("is_active")
    # Получаем объекты цехов
    if workshop_ids:
        workshops = db.query(Workshop).filter(Workshop.id.in_(workshop_ids)).all()

        # Проверяем, все ли цеха найдены
        if len(workshops) != len(workshop_ids):
            raise HTTPException(status_code=400, detail="Один или несколько цехов не найдены")

        # Устанавливаем связь пользователя с цехами
        update_user_workshops(db, user_data.get("id"), workshops)

    db.commit()
    db.refresh(user)

def update_user_workshops(session, user_id, new_workshop_ids):
    # Получаем пользователя по ID
    user = get_user(session, user_id)
    if not user:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Получаем текущие объекты Workshop, связанные с пользователем
    current_workshop_ids = {workshop.id for workshop in user.workshops}
    new_workshops = []
    for workshop in new_workshop_ids:
        new_workshops.append(workshop.id)

    # Находим цеха, которые нужно добавить
    workshops_to_add = [workshop_id for workshop_id in new_workshops if workshop_id not in current_workshop_ids]

    # Находим цеха, которые нужно удалить
    workshops_to_remove = [workshop_id for workshop_id in current_workshop_ids if workshop_id not in new_workshops]

    # Добавляем новые цеха
    for workshop_id in workshops_to_add:
        workshop = session.query(Workshop).filter_by(id=workshop_id).first()
        if workshop:
            user.workshops.append(workshop)
    
    # Удаляем старые цеха
    for workshop_id in workshops_to_remove:
        workshop = session.query(Workshop).filter_by(id=workshop_id).first()
        if workshop:
            user.workshops.remove(workshop)

    # Сохраняем изменения в базе данных
    session.commit()

def get_user_workshop(user: User):
    """Определяет список цехов, к которым относится пользователь."""
    return {workshop.name for workshop in user.workshops}
