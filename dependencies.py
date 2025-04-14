from fastapi import Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import get_user_by_username


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Проверяет авторизован ли пользователь и возвращает объект User"""
    # Получаем user_id из request.state, который был установлен в middleware
    user_username = getattr(request.state, 'user_id', None)
        
    # Получаем пользователя из базы данных по user_id
    user = get_user_by_username(db, user_username)

    return user