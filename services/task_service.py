<<<<<<< HEAD
from sqlalchemy import JSON, or_
from typing import Dict, List
from fastapi.background import P
from sqlalchemy.orm import Session
from models import Bid, Bracket, Cassette, CassetteTypeEnum, Comment, Customer, ExtensionBracket, Files, Klamer, KlamerTypeEnum, LinearPanel, ManagerEnum, Material, MaterialColor, Product, Profile, ProfileType, SheetLength, SheetWidth, Sheets, StatusEnum, Task, TaskWorkshop, UrgencyEnum, User, Workshop
from schemas import BidBase
from services.comment_service import add_comment
from sqlalchemy.orm import subqueryload
from pprint import pprint

def save_customer(db: Session, name: str) -> Customer:
    customer = db.query(Customer).filter(Customer.name == name).first()
    if customer:
        return customer
    customer = Customer(name=name)
    db.add(customer)
    db.flush()
    return customer
    
def create_bid(db: Session, bid_data: dict):
    # Валидация данных через Pydantic
    validated_data = BidBase(**bid_data)

    bid = Bid(
        task_number=validated_data.task_number,
        customer_id=validated_data.customer_id,
        manager=validated_data.manager
    )
    db.add(bid)
    db.flush()
    return bid
    
def create_product(db: Session, product_type: str):
    product = Product(type=product_type)
    db.add(product)
    db.flush()
    return product
    
def create_profile(db: Session, profile_data: dict, product: Product):
    details = profile_data["product_details"]
    profile_type_id = details["profile_type_id"]
    profile_type = db.query(ProfileType).get(profile_type_id)

    if profile_type and profile_type.name == "Не стандарт":
        profile_type = ProfileType(name=details["custom_profile_type"])
        db.add(profile_type)
        db.flush()

    profile = Profile(
        product_id=product.id,
        profile_type_id=profile_type.id,
        length=details["length"]
    )
    db.add(profile)
    db.flush()

    return profile
    
def create_klamer(db: Session, klamer_data: dict, product: Product):
    klamer = Klamer(
        product_id=product.id,
        type=klamer_data["product_details"]["type"]
    )
    db.add(klamer)
    db.flush()
    return klamer

def create_bracket(db: Session, bracket_data: dict, product: Product):
    bracket = Bracket(
        product_id=product.id,
        width=bracket_data["product_details"]["width"],
        length=bracket_data["product_details"]["length"],
        thickness=bracket_data["product_details"]["thickness"]
    )
    db.add(bracket)
    db.flush()
    return bracket
    
def create_extension_bracket(db: Session, extension_bracket_data: dict, product: Product):
    extension_bracket =ExtensionBracket(
        product_id=product.id,
        width = extension_bracket_data["product_details"].get("width", 0),
        length = extension_bracket_data["product_details"].get("length", ""),
        heel = extension_bracket_data.get("product_details", {}).get("heel") == "on",
    )
    db.add(extension_bracket)
    db.flush()
    return extension_bracket
                    
def create_cassette(db: Session, cassette_data: dict, product: Product):
    description = cassette_data.get("product_details", {}).get("description")
    cassette = Cassette(
        product_id=product.id,
        cassette_type=cassette_data["product_details"]["cassette_type_id"],
        description=description
    )
    db.add(cassette)
    db.flush()
    return cassette

def create_linear_panel(db: Session, linear_panel_data: dict, product: Product):
    linear_panel = LinearPanel(
        product_id=product.id,
        field=linear_panel_data["product_details"].get("field", 0),
        rust=linear_panel_data["product_details"].get("rust", 0),
        length=linear_panel_data["product_details"].get("length", 0),
        butt_end=linear_panel_data.get("product_details", {}).get("butt_end") == "on"
    )
    db.add(linear_panel)
    db.flush()
    return linear_panel
    
def create_product_type(db: Session, product_data: dict, product: Product):
    if product.type == "PROFILE":
        try:
            product_type = create_profile(db, product_data, product)                        
        except Exception as e:
            print(f"Ошибка при обработке профиля: {e}")
            raise
    elif product.type == "KLAMER":
        try:
            product_type = create_klamer(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке клямера: {e}")
            raise
    elif product.type == "BRACKET":
        try:
            product_type = create_bracket(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке кронштейна: {e}")
            raise
    elif product.type == "EXTENSION_BRACKET":
        try:
            product_type = create_extension_bracket(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке удлинителя: {e}")
            raise
    elif product.type == "CASSETTE":
        try:
            product_type = create_cassette(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке кассеты: {e}")
            raise
    elif product.type == "LINEAR_PANEL":
        try:
            product_type = create_linear_panel(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке панели: {e}")
            raise
    else:
        print(f"⚠️ Тип продукта: {product.type}. Пропускаем.")
        return None
    return product_type

def create_material_color(db: Session, task_item: dict):
    color_name = task_item["product_details"].get("material_color", "")
    color = db.query(MaterialColor).filter_by(name=color_name).first()
    if not color:
        color = MaterialColor(
            name = task_item["product_details"].get("material_color", ""),
        )
        db.add(color)
        db.flush()
        
    return color
    
def create_material(db: Session, material_data: dict, material_color: MaterialColor):
    material = Material(
        form=material_data["material"],
        type=material_data["material_type"],
        thickness=material_data["thickness"],
        color_id=material_color.id,
        painting = material_data.get("product_details", {}).get("material_paintable")
    )
    db.add(material)
    db.flush()
    return material

def create_task(db: Session, bid: Bid, product: Product, material: Material, bid_data: dict, task_data: dict):
    task = Task(
        bid_id=bid.id,
        product_id=product.id,
        material_id=material.id,
        quantity=bid_data["product_details"]["quantity"],
        urgency=bid_data["urgency"],
        data=task_data
    )
    db.add(task)
    db.flush()
    return task

def create_sheets(db: Session, task: Task, task_item: dict):
    for sheet_data in task_item.get("sheets", []):
        
        # Проверка уникальности для sheet_width
        existing_width = db.query(SheetWidth).filter(SheetWidth.width == sheet_data["width"]).first()
        if existing_width:
            width_sheet=existing_width.id
            print(f"SheetWidth с таким значением {sheet_data['width']} уже существует в базе данных.")
        else:
            sheet_width = SheetWidth(width=sheet_data["width"])
            db.add(sheet_width)
            db.flush()
            width_sheet=sheet_width.id
            
        # Проверка уникальности для sheet_length
        existing_length = db.query(SheetLength).filter(SheetLength.length == sheet_data["length"]).first()
        if existing_length:
            length_sheet=existing_length.id
            print(f"SheetLength с таким значением {sheet_data['length']} уже существует в базе данных.")
        else:
            sheet_length = SheetLength(length=sheet_data["length"])
            db.add(sheet_length)
            db.flush()
            length_sheet=sheet_length.id
        
        sheet = Sheets(
            task_id=task.id,
            width_sheet=width_sheet,
            length_sheet=length_sheet,
            quantity=sheet_data["quantity"]
        )
        db.add(sheet)
        db.flush()
        
def add_workshops(db: Session, task: Task, bid_data: dict):
    workshop_ids = bid_data.get("workshops", [])
    for index, workshop_id in enumerate(workshop_ids):
        workshop = db.get(Workshop, workshop_id)
        if workshop:
            status = "NEW" if index == 0 else "ON_HOLD"
            db.add(TaskWorkshop(task_id=task.id, workshop_id=workshop.id, status=status))
            

def add_employees(db: Session, task: Task, bid_data: dict):
    for user_id in bid_data.get("employees", []):
        user = db.get(User, user_id)
        if user:
            task.responsible_users.append(user)
    db.add(task)

def create_tasks(db: Session, bid: Bid, bid_data: dict):
    task_ids = []        
    for task_item in bid_data["products"]:
        # 2.1 получаем Product
        product = create_product(db, task_item["product_id"])
        
        # 2.2 Обрабатываем подтип продукта
        create_product_type(db, task_item, product)
        
        # 2.3
        material_color = create_material_color(db, task_item)

        # 2.3 Создаем Material
        material = create_material(db, task_item, material_color)

        # 2.4 Создаем Task
        task = create_task(db, bid, product, material, task_item, bid_data)
        task_ids.append(task.id)

        # 2.5 Сохраняем комментарии
        if task_item["comment"]:
            add_comment(db, task, task_item["comment"])

        # 2.5 Сохраняем Sheets
        create_sheets(db, task, task_item)
        
        # 2.6 
        add_workshops(db, task, task_item)
        
        # 2.7
        add_employees(db, task, task_item)

    return task_ids
        

def get_tasks_list(user: User, db: Session) -> List[Dict]:
    """Получает список задач, назначенных на пользователя по цехам или напрямую."""

    workshop_ids = [workshop.id for workshop in user.workshops]

    # Получаем задачи, либо связанные с нужными цехами, либо напрямую назначенные пользователю
    tasks = db.query(Task).distinct().join(TaskWorkshop, isouter=True).join(Task.responsible_users, isouter=True).filter(
        or_(
            TaskWorkshop.workshop_id.in_(workshop_ids),
            User.id == user.id
        )
    ).all()

    result = []

    for task in tasks:
        # Если задача назначена на пользователя, получаем все статусы цехов этой задачи
        if any(u.id == user.id for u in task.responsible_users):
            # Получаем все цехи для задачи, не фильтруем по user.workshops
            task_workshops = db.query(TaskWorkshop).filter(TaskWorkshop.task_id == task.id).all()
        else:
            # Если задача относится только к цеху пользователя, фильтруем по соответствующему цеху
            task_workshops = db.query(TaskWorkshop).filter(
                TaskWorkshop.task_id == task.id,
                TaskWorkshop.workshop_id.in_(workshop_ids)
            ).all()

        workshops_status = [
            {
                "workshop_name": tw.workshop.name.value,  # если name — Enum
                "workshop_status": tw.status.value
            }
            for tw in task_workshops
        ]

        # Опциональная сортировка по приоритету
        workshop_order = {
            "Инженер": 0,
            "Резка": 1,
            "Прокат профилей": 2,
            "Прокат клямеров": 3,
            "Прокат кронштейнов": 4,
            "Прокат удлинителей кронштейнов": 5,
            "Гибка": 7,
            "Покраска": 8,
            "Координатка": 6
        }

        workshops_status.sort(key=lambda w: workshop_order.get(w["workshop_name"], float('inf')))


        # Формируем строку материала
        material_str = None
        if task.material:
            material_str = f"{task.material.form.value}, {task.material.type.value}, {task.material.thickness.value}"

        # Формируем строку листов
        sheets_str = None
        if task.sheets:
            sheets_data = []
            for sheet in task.sheets:
                # Получаем ширину и длину по ID
                sheet_width = db.query(SheetWidth).filter(SheetWidth.id == sheet.width_sheet).first()
                sheet_length = db.query(SheetLength).filter(SheetLength.id == sheet.length_sheet).first()
                
                if sheet_width and sheet_length:
                    # Формируем строку с информацией о листе
                    sheets_data.append(f"{sheet_width.width}x{sheet_length.length} мм, {sheet.quantity} шт")
                else:
                    # В случае ошибки, если не удается найти ширину или длину
                    sheets_data.append(f"Ошибка: нет данных для листа {sheet.id}")
            
            # Соединяем все строки в одну
            sheets_str = "; ".join(sheets_data)


        result.append({
            "id": task.id,
            "task_number": task.bid.task_number if task.bid else None,
            "customer": task.bid.customer.name if task.bid and task.bid.customer else None,
            "manager": task.bid.manager.value if task.bid else None,
            "product": task.product.type.value if task.product else None,
            "quantity": task.quantity,
            "material": material_str,
            "sheets": sheets_str,
            "status": task.status.value,
            "urgency": task.urgency.value,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "workshops_status": workshops_status,
        })

    return result



def get_task_by_id(task_id: int, db: Session) -> Task:
    """Получает детальную информацию о задаче."""
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .options(
            subqueryload(Task.product),
            subqueryload(Task.material),
            subqueryload(Task.comments),
            subqueryload(Task.comments).subqueryload(Comment.users),
            subqueryload(Task.workshops),
            subqueryload(Task.sheets),
            subqueryload(Task.bid).subqueryload(Bid.customer),
        )
        .first()
    )
    return task

def get_products(db: Session):
    products = db.query(Product).all()
    return [{"id": str(item.id), "value": item.type.value} for item in products]

def get_types(db: Session):
    managers = [managers.value for managers in ManagerEnum]
    profile_types = db.query(ProfileType).all()
    profile_values = [profile.name for profile in profile_types]
    klamer_types = [klamer_types.value for klamer_types in KlamerTypeEnum]
    kassete_types = [kassete_types.value for kassete_types in CassetteTypeEnum]
    return managers, profile_values, klamer_types, kassete_types
=======
from sqlalchemy import JSON, or_
from typing import Dict, List
from fastapi.background import P
from sqlalchemy.orm import Session
from models import Bid, Bracket, Cassette, CassetteTypeEnum, Comment, Customer, ExtensionBracket, Files, Klamer, KlamerTypeEnum, LinearPanel, ManagerEnum, Material, MaterialColor, Product, Profile, ProfileType, SheetLength, SheetWidth, Sheets, StatusEnum, Task, TaskWorkshop, UrgencyEnum, User, Workshop
from schemas import BidBase
from services.comment_service import add_comment
from sqlalchemy.orm import subqueryload
from pprint import pprint

def save_customer(db: Session, name: str) -> Customer:
    customer = db.query(Customer).filter(Customer.name == name).first()
    if customer:
        return customer
    customer = Customer(name=name)
    db.add(customer)
    db.flush()
    return customer
    
def create_bid(db: Session, bid_data: dict):
    # Валидация данных через Pydantic
    validated_data = BidBase(**bid_data)

    bid = Bid(
        task_number=validated_data.task_number,
        customer_id=validated_data.customer_id,
        manager=validated_data.manager
    )
    db.add(bid)
    db.flush()
    return bid
    
def create_product(db: Session, product_type: str):
    product = Product(type=product_type)
    db.add(product)
    db.flush()
    return product
    
def create_profile(db: Session, profile_data: dict, product: Product):
    details = profile_data["product_details"]
    profile_type_id = details["profile_type_id"]
    profile_type = db.query(ProfileType).get(profile_type_id)

    if profile_type and profile_type.name == "Не стандарт":
        profile_type = ProfileType(name=details["custom_profile_type"])
        db.add(profile_type)
        db.flush()

    profile = Profile(
        product_id=product.id,
        profile_type_id=profile_type.id,
        length=details["length"]
    )
    db.add(profile)
    db.flush()

    return profile
    
def create_klamer(db: Session, klamer_data: dict, product: Product):
    klamer = Klamer(
        product_id=product.id,
        type=klamer_data["product_details"]["type"]
    )
    db.add(klamer)
    db.flush()
    return klamer

def create_bracket(db: Session, bracket_data: dict, product: Product):
    bracket = Bracket(
        product_id=product.id,
        width=bracket_data["product_details"]["width"],
        length=bracket_data["product_details"]["length"],
        thickness=bracket_data["product_details"]["thickness"]
    )
    db.add(bracket)
    db.flush()
    return bracket
    
def create_extension_bracket(db: Session, extension_bracket_data: dict, product: Product):
    extension_bracket =ExtensionBracket(
        product_id=product.id,
        width = extension_bracket_data["product_details"].get("width", 0),
        length = extension_bracket_data["product_details"].get("length", ""),
        heel = extension_bracket_data.get("product_details", {}).get("heel") == "on",
    )
    db.add(extension_bracket)
    db.flush()
    return extension_bracket
                    
def create_cassette(db: Session, cassette_data: dict, product: Product):
    description = cassette_data.get("product_details", {}).get("description")
    cassette = Cassette(
        product_id=product.id,
        cassette_type=cassette_data["product_details"]["cassette_type_id"],
        description=description
    )
    db.add(cassette)
    db.flush()
    return cassette

def create_linear_panel(db: Session, linear_panel_data: dict, product: Product):
    linear_panel = LinearPanel(
        product_id=product.id,
        field=linear_panel_data["product_details"].get("field", 0),
        rust=linear_panel_data["product_details"].get("rust", 0),
        length=linear_panel_data["product_details"].get("length", 0),
        butt_end=linear_panel_data.get("product_details", {}).get("butt_end") == "on"
    )
    db.add(linear_panel)
    db.flush()
    return linear_panel
    
def create_product_type(db: Session, product_data: dict, product: Product):
    if product.type == "PROFILE":
        try:
            product_type = create_profile(db, product_data, product)                        
        except Exception as e:
            print(f"Ошибка при обработке профиля: {e}")
            raise
    elif product.type == "KLAMER":
        try:
            product_type = create_klamer(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке клямера: {e}")
            raise
    elif product.type == "BRACKET":
        try:
            product_type = create_bracket(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке кронштейна: {e}")
            raise
    elif product.type == "EXTENSION_BRACKET":
        try:
            product_type = create_extension_bracket(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке удлинителя: {e}")
            raise
    elif product.type == "CASSETTE":
        try:
            product_type = create_cassette(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке кассеты: {e}")
            raise
    elif product.type == "LINEAR_PANEL":
        try:
            product_type = create_linear_panel(db, product_data, product)
        except Exception as e:
            print(f"Ошибка при обработке панели: {e}")
            raise
    else:
        print(f"⚠️ Тип продукта: {product.type}. Пропускаем.")
        return None
    return product_type

def create_material_color(db: Session, task_item: dict):
    color_name = task_item["product_details"].get("material_color", "")
    color = db.query(MaterialColor).filter_by(name=color_name).first()
    if not color:
        color = MaterialColor(
            name = task_item["product_details"].get("material_color", ""),
        )
        db.add(color)
        db.flush()
        
    return color
    
def create_material(db: Session, material_data: dict, material_color: MaterialColor):
    material = Material(
        form=material_data["material"],
        type=material_data["material_type"],
        thickness=material_data["thickness"],
        color_id=material_color.id,
        painting = material_data.get("product_details", {}).get("material_paintable")
    )
    db.add(material)
    db.flush()
    return material

def create_task(db: Session, bid: Bid, product: Product, material: Material, bid_data: dict, task_data: dict):
    task = Task(
        bid_id=bid.id,
        product_id=product.id,
        material_id=material.id,
        quantity=bid_data["product_details"]["quantity"],
        urgency=bid_data["urgency"],
        data=task_data
    )
    db.add(task)
    db.flush()
    return task

def create_sheets(db: Session, task: Task, task_item: dict):
    for sheet_data in task_item.get("sheets", []):
        
        # Проверка уникальности для sheet_width
        existing_width = db.query(SheetWidth).filter(SheetWidth.width == sheet_data["width"]).first()
        if existing_width:
            width_sheet=existing_width.id
            print(f"SheetWidth с таким значением {sheet_data['width']} уже существует в базе данных.")
        else:
            sheet_width = SheetWidth(width=sheet_data["width"])
            db.add(sheet_width)
            db.flush()
            width_sheet=sheet_width.id
            
        # Проверка уникальности для sheet_length
        existing_length = db.query(SheetLength).filter(SheetLength.length == sheet_data["length"]).first()
        if existing_length:
            length_sheet=existing_length.id
            print(f"SheetLength с таким значением {sheet_data['length']} уже существует в базе данных.")
        else:
            sheet_length = SheetLength(length=sheet_data["length"])
            db.add(sheet_length)
            db.flush()
            length_sheet=sheet_length.id
        
        sheet = Sheets(
            task_id=task.id,
            width_sheet=width_sheet,
            length_sheet=length_sheet,
            quantity=sheet_data["quantity"]
        )
        db.add(sheet)
        db.flush()
        
def add_workshops(db: Session, task: Task, bid_data: dict):
    workshop_ids = bid_data.get("workshops", [])
    for index, workshop_id in enumerate(workshop_ids):
        workshop = db.get(Workshop, workshop_id)
        if workshop:
            status = "NEW" if index == 0 else "ON_HOLD"
            db.add(TaskWorkshop(task_id=task.id, workshop_id=workshop.id, status=status))
            

def add_employees(db: Session, task: Task, bid_data: dict):
    for user_id in bid_data.get("employees", []):
        user = db.get(User, user_id)
        if user:
            task.responsible_users.append(user)
    db.add(task)

def create_tasks(db: Session, bid: Bid, bid_data: dict):
    task_ids = []        
    for task_item in bid_data["products"]:
        # 2.1 получаем Product
        product = create_product(db, task_item["product_id"])
        
        # 2.2 Обрабатываем подтип продукта
        create_product_type(db, task_item, product)
        
        # 2.3
        material_color = create_material_color(db, task_item)

        # 2.3 Создаем Material
        material = create_material(db, task_item, material_color)

        # 2.4 Создаем Task
        task = create_task(db, bid, product, material, task_item, bid_data)
        task_ids.append(task.id)

        # 2.5 Сохраняем комментарии
        if task_item["comment"]:
            add_comment(db, task, task_item["comment"])

        # 2.5 Сохраняем Sheets
        create_sheets(db, task, task_item)
        
        # 2.6 
        add_workshops(db, task, task_item)
        
        # 2.7
        add_employees(db, task, task_item)

    return task_ids
        

def get_tasks_list(user: User, db: Session) -> List[Dict]:
    """Получает список задач, назначенных на пользователя по цехам или напрямую."""

    workshop_ids = [workshop.id for workshop in user.workshops]

    # Получаем задачи, либо связанные с нужными цехами, либо напрямую назначенные пользователю
    tasks = db.query(Task).distinct().join(TaskWorkshop, isouter=True).join(Task.responsible_users, isouter=True).filter(
        or_(
            TaskWorkshop.workshop_id.in_(workshop_ids),
            User.id == user.id
        )
    ).all()

    result = []

    for task in tasks:
        # Если задача назначена на пользователя, получаем все статусы цехов этой задачи
        if any(u.id == user.id for u in task.responsible_users):
            # Получаем все цехи для задачи, не фильтруем по user.workshops
            task_workshops = db.query(TaskWorkshop).filter(TaskWorkshop.task_id == task.id).all()
        else:
            # Если задача относится только к цеху пользователя, фильтруем по соответствующему цеху
            task_workshops = db.query(TaskWorkshop).filter(
                TaskWorkshop.task_id == task.id,
                TaskWorkshop.workshop_id.in_(workshop_ids)
            ).all()

        workshops_status = [
            {
                "workshop_name": tw.workshop.name.value,  # если name — Enum
                "workshop_status": tw.status.value
            }
            for tw in task_workshops
        ]

        # Опциональная сортировка по приоритету
        workshop_order = {
            "Инженер": 0,
            "Резка": 1,
            "Прокат профилей": 2,
            "Прокат клямеров": 3,
            "Прокат кронштейнов": 4,
            "Прокат удлинителей кронштейнов": 5,
            "Гибка": 7,
            "Покраска": 8,
            "Координатка": 6
        }

        workshops_status.sort(key=lambda w: workshop_order.get(w["workshop_name"], float('inf')))


        # Формируем строку материала
        material_str = None
        if task.material:
            material_str = f"{task.material.form.value}, {task.material.type.value}, {task.material.thickness.value}"

        # Формируем строку листов
        sheets_str = None
        if task.sheets:
            sheets_data = []
            for sheet in task.sheets:
                # Получаем ширину и длину по ID
                sheet_width = db.query(SheetWidth).filter(SheetWidth.id == sheet.width_sheet).first()
                sheet_length = db.query(SheetLength).filter(SheetLength.id == sheet.length_sheet).first()
                
                if sheet_width and sheet_length:
                    # Формируем строку с информацией о листе
                    sheets_data.append(f"{sheet_width.width}x{sheet_length.length} мм, {sheet.quantity} шт")
                else:
                    # В случае ошибки, если не удается найти ширину или длину
                    sheets_data.append(f"Ошибка: нет данных для листа {sheet.id}")
            
            # Соединяем все строки в одну
            sheets_str = "; ".join(sheets_data)


        result.append({
            "id": task.id,
            "task_number": task.bid.task_number if task.bid else None,
            "customer": task.bid.customer.name if task.bid and task.bid.customer else None,
            "manager": task.bid.manager.value if task.bid else None,
            "product": task.product.type.value if task.product else None,
            "quantity": task.quantity,
            "material": material_str,
            "sheets": sheets_str,
            "status": task.status.value,
            "urgency": task.urgency.value,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "workshops_status": workshops_status,
        })

    return result



def get_task_by_id(task_id: int, db: Session) -> Task:
    """Получает детальную информацию о задаче."""
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .options(
            subqueryload(Task.product),
            subqueryload(Task.material),
            subqueryload(Task.comments),
            subqueryload(Task.comments).subqueryload(Comment.users),
            subqueryload(Task.workshops),
            subqueryload(Task.sheets),
            subqueryload(Task.bid).subqueryload(Bid.customer),
        )
        .first()
    )
    return task

def get_products(db: Session):
    products = db.query(Product).all()
    return [{"id": str(item.id), "value": item.type.value} for item in products]

def get_types(db: Session):
    managers = [managers.value for managers in ManagerEnum]
    profile_types = db.query(ProfileType).all()
    profile_values = [profile.name for profile in profile_types]
    klamer_types = [klamer_types.value for klamer_types in KlamerTypeEnum]
    kassete_types = [kassete_types.value for kassete_types in CassetteTypeEnum]
    return managers, profile_values, klamer_types, kassete_types
>>>>>>> 1488e3832cf2a54b8b2965ef1d819b318057be39
