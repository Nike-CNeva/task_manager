from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from models import (
    ProductTypeEnum,
    UserTypeEnum,
    ProfileTypeEnum,
    WorkshopEnum,
    ManagerEnum,
    KlamerTypeEnum,
    CassetteTypeEnum,
    MaterialFormEnum,
    MaterialTypeEnum,
    MaterialThicknessEnum,
    UrgencyEnum,
    StatusEnum

)

# Base Pydantic Models
class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    firstname: Optional[str] = None
    email: Optional[EmailStr] = None
    telegram: Optional[str] = None
    username: str
    user_type: UserTypeEnum
    is_active: bool = True

class UserRead(UserBase):
    id: int


class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    waste: Optional[str] = None
    weight: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class TaskRead(TaskBase):
    id: int
    quantity: Optional[int] = None
    urgency: UrgencyEnum
    status: StatusEnum

class BidBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    task_number: Optional[str] = None
    manager: ManagerEnum


class BidRead(BidBase):
    id: int

class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
class ProductRead(ProductBase):
    id: int


class MaterialBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    form: MaterialFormEnum
    type: MaterialTypeEnum
    thickness: MaterialThicknessEnum
    painting: bool = False
    color_id: Optional[int] = None

class MaterialRead(MaterialBase):
    id: int

class MaterialColorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class CustomerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    name: str

class CustomerRead(CustomerBase):

    id: int

class WorkshopBase(BaseModel):
    name: str

class WorkshopRead(WorkshopBase):
    id: int

class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    comment: str
    created_at: datetime
    is_read: bool = False
    is_deleted: bool = False
    

class CommentRead(CommentBase):
    id: int


class SheetWidthRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    width: str
   
class SheetLengthRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    length: str

class SheetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    width: SheetWidthRead
    length: SheetLengthRead
    quantity: int    

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
    model_config = ConfigDict(from_attributes=True)
    product_type: str  # Тип продукта, например, "профиля", "клямера", "кассеты" и т.д.
    material_type: Optional[str] = None  # Дополнительный выбор материала, если применимо
    thickness: Optional[float] = None  # Толщина материала, если применимо
    other_condition: Optional[str] = None  # Дополнительное поле, если применимо
    paint: Optional[bool] = None  # Необходимость покраски, если материал не полимер


class Customer(BaseModel):
    name: str

class Manager(BaseModel):
    value: str

class BidDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    customer: CustomerRead
    manager: ManagerEnum

class ProductDetailField(BaseModel):
    name: str
    label: str
    type: str

class Responsible(BaseModel):
    name: str

class Comment(BaseModel):
    users:  List[Responsible]  # Assuming a user has a name
    text: str
    created_at: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)

class File(BaseModel):
    id: int
    filename: str

class TaskDetail(BaseModel):
    id: int
    bid: BidDetail
    product: ProductRead
    task_number: str
    material: Optional[MaterialRead]
    material_color: Optional[MaterialColorRead]
    quantity: int
    sheets: List[SheetRead]
    weight: Optional[str]
    waste: Optional[str]
    urgency: UrgencyEnum
    status: StatusEnum    
    workshops: List[WorkshopEnum]
    responsibles: List[Responsible]
    comments: List[Comment]
    files: List[File]
    created_at: datetime
    completed_at: Optional[datetime]

# Pydantic модель для Workshop с добавлением статуса