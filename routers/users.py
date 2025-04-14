from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dependencies import get_current_user
from middlewares.auth_middleware import get_password_hash, verify_password
from models import User, UserTypeEnum, Workshop
from services import user_service
from database import get_db
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user:
        user_authenticated = True
    users = user_service.get_users(db)
    # Формируем список пользователей с их цехами
    users_with_workshops = []
    for user in users:
        user_workshops = [w.name for w in user.workshops]  # Получаем список цехов пользователя
        users_with_workshops.append({
            "id": user.id,
            "name": user.name,
            "firstname": user.firstname,
            "username": user.username,
            "email": user.email,
            "telegram": user.telegram,
            "user_type": user.user_type.value,
            "workshops": user_workshops  # Передаем список цехов
        })
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "users": users_with_workshops,
        "user_authenticated": user_authenticated,
        "user_type": current_user.user_type.value
    })

@router.get("/admin/users/create", response_class=HTMLResponse)
def create_user_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user:
        user_authenticated = True
    workshops = db.query(Workshop).all()
    roles = [role.value for role in UserTypeEnum]
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user_type": current_user.user_type.value,
        "roles": roles,
        "workshops": workshops,
        "edit": False,
        "user_obj": None,
        "user_workshops": []
    })

@router.post("/admin/users/create")
@router.post("/admin/users/{user_id}/edit")
def save_user(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = None,
    name: str = Form(...),
    username: str = Form(...),
    user_type: str = Form(...),
    password: str = Form(...),
    is_active: bool = Form(True),
    workshops: list[str] = Form(..., alias="workshops[]")  # Теперь это список
):
    # Находим соответствующие объекты Workshop
    workshop_objs = db.query(Workshop).filter(Workshop.name.in_(workshops)).all()
    
    if not workshop_objs:
        return {"error": f"Цеха {workshops} не найдены"}
    if user_id:
        user = user_service.get_user_by_username(db, username)
        user_id = user.id
    user_data = {
        "name": name,
        "username": username,
        "user_type": user_type,
        "password": password,
        "is_active": is_active
    }
    if user_id:
        user_data["id"] = user_id
        user_service.update_user(db, user_data, [w.id for w in workshop_objs])
    else:
        user_service.create_user(db, user_data, [w.id for w in workshop_objs])
    return RedirectResponse(url="/admin/users", status_code=303)

@router.get("/admin/users/{user_id}/edit")
async def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user:
        user_authenticated = True
    # Проверяем, является ли пользователь администратором
    if current_user.user_type != UserTypeEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Получаем пользователя из базы
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получаем все прикрепленные цеха для этого пользователя
    user_workshops = [w.name for w in user_obj.workshops]
    workshops = db.query(Workshop).all()
    roles = [role.value for role in UserTypeEnum]
    # Возвращаем шаблон с данными пользователя для редактирования
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user_type": current_user.user_type.value,
        "roles": roles,
        "workshops": workshops,
        "edit": True,
        "user_obj": user_obj,
        "user_workshops": user_workshops
    })


@router.get("/profile")
async def get_profile(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Возвращаем информацию о текущем пользователе
    if current_user:
        user_authenticated = True
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "name": current_user.name,
        "firstname": current_user.firstname,
        "email": current_user.email,
        "telegram": current_user.telegram,
        "username": current_user.username,
        "user_type": current_user.user_type.value,
        "tasks": [task.id for task in current_user.tasks],  # список задач пользователя
        "workshops": [workshop.name.value for workshop in current_user.workshops],  # список цехов
        "comments": [comment.id for comment in current_user.comments],  # список комментариев
    })

@router.post("/profile")
async def edit_profile(
    request: Request,
    name: str = Form(...),
    firstname: str = Form(...),
    email: str = Form(...),
    telegram: str = Form(...),
    username: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получаем текущего пользователя и обновляем его данные
    current_user.name = name
    current_user.firstname = firstname
    current_user.email = email
    current_user.telegram = telegram
    current_user.username = username

    db.commit()  # Сохраняем изменения в базе данных

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "name": current_user.name,
        "firstname": current_user.firstname,
        "email": current_user.email,
        "telegram": current_user.telegram,
        "username": current_user.username,
    })

@router.get("/profile/password")
async def change_password_page(request: Request, current_user: User = Depends(get_current_user)):
        if current_user:
            user_authenticated = True
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user_authenticated": user_authenticated,
            "user_type": current_user.user_type.value
            })

@router.post("/profile/password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, совпадает ли текущий пароль, используя verify_password
    if not verify_password(current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Текущий пароль введен неверно")
    
    # Проверяем, совпадают ли новый пароль и подтверждение
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Новый пароль и его подтверждение не совпадают")
    
    # Обновляем пароль в базе данных, используя get_password_hash
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    # Перенаправляем пользователя в личный кабинет
    return RedirectResponse(url="/profile", status_code=303)

