from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User
from services.user_service import get_user_by_username, get_user
from settings import settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from datetime import datetime

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home(request: Request, user: User = Depends(get_current_user)):
    """
    Главная страница. Если пользователь не авторизован, предлагает войти в систему.
    Если авторизован, приветствует его и предлагает перейти к задачам.
    """
    current_datetime = datetime.now().isoformat()
    if user is None:
        message = "Добро пожаловать! Пожалуйста, авторизуйтесь, чтобы продолжить."
        user_authenticated = False
        user_name = "Гость"
        user_type = "guest"  # роль для неавторизованного пользователя
    else:
        message = "Здравствуйте! Добро пожаловать в систему управления задачами."
        user_authenticated = True
        user_name = user.name if user.name else "Гость"
        user_type = user.user_type.value

    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": message,
        "current_datetime": current_datetime,
        "user_authenticated": user_authenticated,
        "user_name": user_name,
        "user_type": user_type
    })
