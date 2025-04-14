from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

# Enums
class ProductTypeEnum(str, Enum):
    PROFILE = "Профиля"
    KLAMER = "Клямера"
    BRACKET = "Кронштейны"
    EXTENSION_BRACKET = "Удлинители кронштейнов"
    CASSETTE = "Кассеты"
    FACING = "Фасонка"
    LINEAR_PANEL = "Линеарные панели"
    SHEET = "Листы"
    WALL_PANEL = "Стеновые панели(Продэкс)"
    OTHER = "Другое"

class UserTypeEnum(str, Enum):
    ADMIN = "Администратор"
    ENGINEER = "Инженер"
    OPERATOR = "Оператор"
    SUPERVISER = "Старший смены"
    
class ProfileTypeEnum(str, Enum):
    G40X40 = "Г-образный 40х40"
    G40X60 = "Г-образный 40х60"
    G50X50 = "Г-образный 50х50"
    P60 = "П-образный 60"
    P80 = "П-образный 80"
    P100 = "П-образный 100"
    Z20X20X40 = "З-образный 20х20х40"
    PGSH = "ПГШ"
    PVSH = "ПВШ"
    PNU = "ПНУ"
    OTHER = "Не стандрт"


class WorkshopEnum(str, Enum):
    PROFILE = "Прокат профилей"
    KLAMER = "Прокат клямеров"
    BRACKET = "Прокат кронштейнов"
    EXTENSION_BRACKET = "Гибка удлинителей кронштейнов"
    ENGINEER = "Инженер"
    BENDING = "Гибка"
    CUTTING = "Резка"
    COORDINATE_PUNCHING = "Координатка"
    PAINTING = "Покраска"

class ManagerEnum(str, Enum):
    NOVIKOV = "Новиков"
    SEMICHEV = "Семичев С."
    PTICHKINA = "Птичкина"
    VIKULINA = "Викулина"
    GAVRILOVEC = "Гавриловец"
    SEMICHEV_YOUNGER = "Семичев Д."

class KlamerTypeEnum(str, Enum):
    IN_LINE = "Рядный"
    STARTING = "Стартовый"
    ANGULAR = "Угловой"

class CassetteTypeEnum(str, Enum):
    KZT_STD = "Зактрытого типа(стандарт)"
    KOT_STD = "Открытого типа(стандарт)"
    KOTVO = "Открытого типа, отв. в вертикальных рустах"
    KZT = "Закрытого типа"
    KOT = "Открытого типа"
    OTHER = "Другое"

class MaterialFormEnum(str, Enum):
    SHEET = "Лист"
    COIL = "Рулон"
    STRIP = "Штрипс"

class MaterialTypeEnum(str, Enum):
    ALUMINIUM = "Алюминий"
    STEEL = "Сталь"
    STAINLESS_STEEL = "Нержавеющая сталь"
    ZINC = "Оцинковка"
    POLYMER = "Полимер"

class MaterialThicknessEnum(str, Enum):
    ZERO_FIVE = "0.5мм"
    ZERO_SEVEN = "0.7мм"
    ONE = "1.0мм"
    ONE_TWO = "1.2мм"
    ONE_FIVE = "1.5мм"
    TWO = "2.0мм"
    THREE = "3.0мм"

class UrgencyEnum(str, Enum):
    LOW = "Низкая"
    MEDIUM = "Нормальная"
    HIGH = "Высокая"

class StatusEnum(str, Enum):
    NEW = "Новая"
    IN_WORK = "В работе"
    COMPLETED = "Выполнена"
    CANCELED = "Отменена"
    ON_HOLD = "На удержании"

# Base Pydantic Models
class UserBase(BaseModel):
    name: str
    firstname: Optional[str] = None
    email: Optional[EmailStr] = None
    telegram: Optional[str] = None
    username: str
    user_type: UserTypeEnum
    is_active: bool = True

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    quantity: Optional[int] = None
    urgency_id: StatusEnum
    status_id: StatusEnum
    waste: Optional[str] = None
    weight: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class TaskRead(TaskBase):
    id: int

    class Config:
        from_attributes = True

class BidBase(BaseModel):
    task_number: Optional[str] = None
    customer_id: int
    manager: ManagerEnum


class BidRead(BidBase):
    id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    type: str

class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True

class MaterialBase(BaseModel):
    form_id: str
    type_id: str
    thickness_id: str
    painting: bool = False

class MaterialRead(MaterialBase):
    id: int

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str

class CustomerRead(CustomerBase):
    id: int

    class Config:
        from_attributes = True

class WorkshopBase(BaseModel):
    name: str

class WorkshopRead(WorkshopBase):
    id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    comment: str
    created_at: datetime
    is_read: bool = False
    is_deleted: bool = False

class CommentRead(CommentBase):
    id: int

    class Config:
        from_attributes = True

# Связи Many-to-Many
class UserWithTasks(UserRead):
    tasks: List[TaskRead] = []

class TaskWithUsers(TaskRead):
    responsible_users: List[UserRead] = []

class BidWithTasks(BidRead):
    tasks: List[TaskRead] = []

class CustomerWithBids(CustomerRead):
    bid: List[BidRead] = []


class ProductRequest(BaseModel):
    product_type: str  # Тип продукта, например, "профиля", "клямера", "кассеты" и т.д.
    material_type: Optional[str] = None  # Дополнительный выбор материала, если применимо
    thickness: Optional[float] = None  # Толщина материала, если применимо
    other_condition: Optional[str] = None  # Дополнительное поле, если применимо
    color: Optional[str] = None  # Поле для цвета, если применимо
    paint: Optional[bool] = None  # Необходимость покраски, если материал не полимер