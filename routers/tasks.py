import json
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Request, UploadFile, status
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from models import Bid, Customer, ProfileType, Task, TaskWorkshop, User, Workshop, WorkshopEnum, Product, Material, MaterialColor, Sheets
from dependencies import get_current_user
from database import get_db
from fastapi.templating import Jinja2Templates
from schemas import BidDetail, CassetteTypeEnum, Comment, KlamerTypeEnum, Manager, ManagerEnum, MaterialFormEnum, MaterialThicknessEnum, MaterialTypeEnum, ProductTypeEnum, Responsible,  StatusEnum, TaskDetail, UrgencyEnum, WorkshopRead, Workshop, ProductRead, MaterialRead, CustomerRead, SheetRead, File, MaterialColorRead
from services.file_service import save_file
from services.task_service import create_bid, create_tasks, get_tasks_list, save_customer
import os
import logging


logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tasks")
async def get_tasks(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Возвращает HTML-шаблон со списком задач."""
    if current_user:
        user_authenticated = True
    tasks = get_tasks_list(current_user, db)
    return templates.TemplateResponse("tasks_list.html", {
        "request": request,
        "user_authenticated": user_authenticated, # type: ignore
        "user_type": current_user.user_type.value,
        "tasks": tasks
        })

@router.get("/{task_id}", response_model=TaskDetail)
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """
    Get the detailed information for a specific task.
    """
    task = db.query(Task).filter(Task.id == task_id).options(
        selectinload(Task.bid).selectinload(Bid.customer),
        selectinload(Task.sheets).selectinload(Sheets.width),
        selectinload(Task.sheets).selectinload(Sheets.length),
        selectinload(Task.material).selectinload(Material.color),
        selectinload(Task.workshops).selectinload(TaskWorkshop.workshop),
        selectinload(Task.responsible_users),
        selectinload(Task.comments).selectinload(Comment.users),
        selectinload(Task.bid).selectinload(Bid.files),
        selectinload(Task.product)
    ).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Construct the TaskDetail object
    task_detail = TaskDetail(
        id=task.id,
        bid=BidDetail(
            task_number=task.bid.task_number,
            customer=CustomerRead.model_validate(task.bid.customer),
            manager=task.bid.manager,
        ),
        product=ProductRead.model_validate(task.product),
        material = MaterialRead.model_validate(task.material),
        material_color = MaterialColorRead.model_validate(task.material.color) if task.material.color else None,
        quantity=task.quantity,
        sheets=[SheetRead.model_validate(sheet) for sheet in task.sheets],
        weight=task.weight,
        waste=task.waste,
        urgency=task.urgency,
        status=task.status,
        workshops=[
            Workshop(name=tw.workshop.name, status=tw.status)
            for tw in task.workshops
        ],
        responsibles=[Responsible(name=user.name) for user in task.responsible_users],
        comments=[Comment(users=[Responsible(name=user.name) for user in comment.users],text=comment.comment, created_at=comment.created_at) for comment in task.comments],
        files=[File(id=file.id, filename=file.file_name) for file in task.bid.files],
        created_at=task.created_at,
        completed_at=task.completed_at,
    )

    return task_detail

@router.post("/task/{task_id}/delete")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    bid_id = task.bid_id
    db.delete(task)
    db.commit()

    # После удаления проверим — остались ли еще задачи у этого bid
    remaining_tasks = db.query(Task).filter(Task.bid_id == bid_id).count()
    if remaining_tasks == 0:
        bid = db.query(Bid).filter(Bid.id == bid_id).first()
        if bid:
            db.delete(bid)
            db.commit()

    return {
        "message": f"Задача удалена. Bid {'тоже удалён' if remaining_tasks == 0 else 'сохранён'}",
        "bid_id": bid_id,
        "bid_deleted": remaining_tasks == 0
    }
    
    
@router.get("/tasks/new")
def get_bids(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user:
        user_authenticated = True
    managers = [managers for managers in ManagerEnum]
    status = [status for status in StatusEnum]
    return templates.TemplateResponse("create_task.html", {
        "request": request,
        "user_authenticated": user_authenticated, # type: ignore
        "user_type": current_user.user_type.value,
        "managers": managers,
        "status":status
        })
    
@router.post("/bids/create/")
def create_bids(
    bid_data: str = Form(...),  # Получаем строку JSON
    files: list[UploadFile] = File(None),  # Получаем файлы
    db: Session = Depends(get_db)
):
    # Преобразуем строку JSON в словарь
    
    bid_data_dict = json.loads(bid_data)
    print("📥 Полученные данные:", json.dumps(bid_data_dict, ensure_ascii=False, indent=4))

    try:
        with db.begin():
            if bid_data_dict["customer_id"] == "new":
                customer = save_customer(db, bid_data_dict["customer"])
                bid_data_dict["customer_id"] = customer.id
            # 1. Создаем Bid
            bid = create_bid(db, bid_data_dict)
            
            if files:
                # Обработка файлов (например, сохранение на сервере)
                for file in files:
                    save_file(bid, file, db)
                    
            # 2. Создаем задачи
            task_ids = create_tasks(db, bid, bid_data_dict)

            task_list = ", ".join(str(tid) for tid in task_ids)
            return {
                "bid_id": bid.id,
                "task_ids": task_ids,
                "message": f"Bid #{bid.id} и задачи с ID: {task_list} успешно созданы"
            }    
    except UnicodeDecodeError as e:
        print(f"❌ Ошибка кодировки: {e}")
        raise HTTPException(status_code=400, detail="Ошибка кодировки в JSON")
    except SQLAlchemyError as e:
        print(f"❌ Ошибка БД: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/customers/")
async def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@router.post("/customers/")
def add_customer(name: str, db: Session = Depends(get_db)):
    customer = Customer(name=name)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/products/")
def get_products():
    """Возвращает список продуктов из Enum"""
    return [{"value": item.name, "label": item.value} for item in ProductTypeEnum]

@router.get("/products/{productType}/fields")
def get_product_fields(productType: str, db: Session = Depends(get_db)):

    fields = []
    if productType == "PROFILE": # type: ignore
        profile_types = db.query(ProfileType).all()
        opt_profile = []
        for item in profile_types:
            opt_profile.append({"value": item.id, "label": item.name})
        fields = [
            {"name": "profile_type_id", "label": "Выберите тип профиля", "type": "select", "options": opt_profile},
            {"name": "length", "label": "Введите длину профиля", "type": "number"},
            {"name": "quantity", "label": "Введите количество профилей", "type": "number"},
        ]
    elif productType == "KLAMER": # type: ignore
        opt_klamer = []
        for item in KlamerTypeEnum:
            opt_klamer.append({"value": item.name, "label": item.value})
        fields = [
            {"name": "type", "label": "Выберите тип клямеров", "type": "select", "options": opt_klamer},
            {"name": "quantity", "label": "Введите количество клямеров", "type": "number"},
        ]
    elif productType == "BRACKET": # type: ignore
        fields = [
            {"name": "width", "label": "Введите ширину кронштейнов", "type": "number"},
            {"name": "length", "label": "Введите длину кронштейнов", "type": "text"},
            {"name": "thickness", "label": "Введите толщину кронштейнов", "type": "number"},
            {"name": "quantity", "label": "Введите количество кронштейнов", "type": "number"},
        ]
    elif productType == "EXTENSION_BRACKET": # type: ignore
        fields = [
            {"name": "width", "label": "Введите ширину удлинителей", "type": "number"},
            {"name": "length", "label": "Введите длину удлинителей", "type": "text"},
            {"name": "heel", "label": "Угловой", "type": "checkbox"},
            {"name": "quantity", "label": "Введите количество удлинителей", "type": "number"},
        ]
    elif productType == "CASSETTE": # type: ignore
        opt_cassette = []
        for item in CassetteTypeEnum:
            opt_cassette.append({"value": item.name, "label": item.value})
        fields = [
            {"name": "cassette_type_id", "label": "Выберите тип кассет", "type": "select", "options": opt_cassette},
            {"name": "quantity", "label": "Введите количество кассет", "type": "number"},
        ]
    elif productType == "LINEAR_PANEL": # type: ignore
        fields = [
            {"name": "field", "label": "Введите размер рабочей поверхности", "type": "number"},
            {"name": "rust", "label": "Введите размер руста", "type": "number"},
            {"name": "length", "label": "Введите длину панели", "type": "number"},
            {"name": "butt_end", "label": "Закрытые торцы", "type": "checkbox"},
            {"name": "quantity", "label": "Введите количество панелей", "type": "number"},
        ]
    elif productType == "FACING": # type: ignore
        fields = [
            {"name": "quantity", "label": "Введите количество фасонки", "type": "number"},
        ]
    elif productType == "SHEET": # type: ignore
        fields = [
            {"name": "quantity", "label": "Введите количество листов", "type": "number"},
        ]
    elif productType == "WALL_PANEL": # type: ignore
        fields = [
            {"name": "quantity", "label": "Введите количество продэкса", "type": "number"},
        ]
    elif productType == "OTHER": # type: ignore
        fields = [
            {"name": "quantity", "label": "Введите количество", "type": "number"},
        ]

    return fields

@router.get("/material/forms/{product_id}")
def get_material_forms(product_id: str):
    """Возвращает формы материала в зависимости от типа изделия"""
    product = product_id
    # Определяем доступные формы материала
    product_material_map = {
        "PROFILE": [MaterialFormEnum.STRIP, MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "KLAMER": [MaterialFormEnum.STRIP],
        "BRACKET": [MaterialFormEnum.STRIP, MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "EXTENSION_BRACKET": [MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "CASSETTE": [MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "LINEAR_PANEL": [MaterialFormEnum.COIL],
        "FACING": [MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "SHEET": [MaterialFormEnum.COIL, MaterialFormEnum.SHEET],
        "WALL_PANEL": [MaterialFormEnum.SHEET],
        "OTHER": [MaterialFormEnum.STRIP, MaterialFormEnum.COIL, MaterialFormEnum.SHEET]
    }

    forms = product_material_map.get(product, []) # type: ignore
    return [{"name": form.name, "value": form.value} for form in forms]

@router.get("/material/types/{product_id}/{form}")
def get_material_types(product_id: str, form: str = Path(...)):
    """Определяем доступные типы материала в зависимости от изделия и формы материала"""
    # Преобразуем строку в Enum
    form_enum = MaterialFormEnum[form]

    # Карта типов материалов с учетом изделия
    product_material_map = {
        "PROFILE": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC],
            MaterialFormEnum.STRIP: [MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.STEEL, MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC]
        },
        "KLAMER": {
            MaterialFormEnum.STRIP: [MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC]
        },
        "BRACKET": {
            MaterialFormEnum.STRIP: [MaterialTypeEnum.ZINC],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC]
        },
        "EXTENSION_BRACKET": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC]
        },
        "CASSETTE": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER]
        },
        "LINEAR_PANEL": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER]
        },
        "FACING": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.STEEL, MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER]
        },
        "SHEET": {
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.STEEL, MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC]
        },
        "WALL_PANEL": {
            MaterialFormEnum.SHEET: [MaterialTypeEnum.STEEL]
        },
        "OTHER": {
            MaterialFormEnum.STRIP: [MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC],
            MaterialFormEnum.COIL: [MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER],
            MaterialFormEnum.SHEET: [MaterialTypeEnum.ALUMINIUM, MaterialTypeEnum.STEEL, MaterialTypeEnum.STAINLESS_STEEL, MaterialTypeEnum.ZINC, MaterialTypeEnum.POLYMER]
        }
    }

    # Получаем доступные типы материалов для выбранного продукта и формы
    available_materials = product_material_map.get(product_id, {}).get(form_enum, []) # type: ignore

    return [{"name": mat.name, "value": mat.value} for mat in available_materials]

@router.get("/material/thickness/{type}")
def get_material_thickness(type: str = Path(...)):
    try:
        type_enum = MaterialTypeEnum[type]  # Конвертируем строку в Enum
    except KeyError:
        raise HTTPException(status_code=422, detail="Неверный тип материала")

    thickness_map = {
        MaterialTypeEnum.ALUMINIUM: [MaterialThicknessEnum.ONE, MaterialThicknessEnum.TWO],
        MaterialTypeEnum.STEEL: [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
        MaterialTypeEnum.STAINLESS_STEEL: [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO, MaterialThicknessEnum.TWO],
        MaterialTypeEnum.ZINC: [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO, MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO, MaterialThicknessEnum.THREE],
        MaterialTypeEnum.POLYMER: [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
    }

    thicknesses = thickness_map.get(type_enum, [])
    return [{"name": thick.name, "value": thick.value} for thick in thicknesses]


@router.get("/workshops", response_model=List[WorkshopRead])
async def get_workshops(db: Session = Depends(get_db)) -> List[WorkshopRead]:
    """Возвращает список цехов, отсортированных в заданном порядке."""
    
    workshops = db.query(Workshop).all()
    workshop_order = {
        WorkshopEnum.PROFILE.value: 3,
        WorkshopEnum.KLAMER.value: 4,
        WorkshopEnum.BRACKET.value: 5,
        WorkshopEnum.EXTENSION_BRACKET.value: 6,
        WorkshopEnum.ENGINEER.value: 0,
        WorkshopEnum.CUTTING.value: 1,
        WorkshopEnum.COORDINATE_PUNCHING.value: 2,
        WorkshopEnum.BENDING.value: 7,
        WorkshopEnum.PAINTING.value: 8,
    }
    
    sorted_workshops = sorted(workshops, key=lambda workshop: workshop_order.get(workshop.name.value, float('inf')))
    workshops = [WorkshopRead.model_validate(workshop) for workshop in sorted_workshops]
    print(workshops)
    # Преобразуем SQLAlchemy-объекты в Pydantic-модели
    return workshops


@router.get("/employee")
async def get_employee(db: Session = Depends(get_db)):
    employee = db.query(User).all()
    return employee

@router.get("/urgency")
async def get_urgency():
    urgency = [urgency for urgency in UrgencyEnum]
    return urgency

    
# ------------------- Загрузка файлов -------------------
@router.post("/files/upload/")
def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"message": "Файл загружен", "file_path": file_location}
