<<<<<<< HEAD
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Form, status, Request
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from middlewares.auth_middleware import create_access_token, verify_password
from models import User
from services import user_service
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()  # Добавляем роутер
templates = Jinja2Templates(directory="templates")


# ================================
# Эндпоинты авторизации
# ================================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: User = Depends(get_current_user)):
    if user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": "Неверный логин или пароль"  # Передаем сообщение об ошибке в шаблон
    })

@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Авторизация пользователя"""
    user = user_service.get_user_by_username(db, username)
    
    if not user or not verify_password(password, user.password):  # ✅ Исправлено
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    # Генерируем access и refresh токены
    access_token = create_access_token({"sub": user.username, "user_id": user.id})

    # Создаем редирект и устанавливаем токены в cookies
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    expire_time = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=expire_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    return response

@router.get("/logout")
def logout():
    """Выход из аккаунта"""
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

=======
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Form, status, Request
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from middlewares.auth_middleware import create_access_token, verify_password
from models import User
from services import user_service
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()  # Добавляем роутер
templates = Jinja2Templates(directory="templates")


# ================================
# Эндпоинты авторизации
# ================================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: User = Depends(get_current_user)):
    if user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": "Неверный логин или пароль"  # Передаем сообщение об ошибке в шаблон
    })

@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Авторизация пользователя"""
    user = user_service.get_user_by_username(db, username)
    
    if not user or not verify_password(password, user.password):  # ✅ Исправлено
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    # Генерируем access и refresh токены
    access_token = create_access_token({"sub": user.username, "user_id": user.id})

    # Создаем редирект и устанавливаем токены в cookies
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    expire_time = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=expire_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    return response

@router.get("/logout")
def logout():
    """Выход из аккаунта"""
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

>>>>>>> 1488e3832cf2a54b8b2965ef1d819b318057be39
