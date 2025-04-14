from sqlalchemy import JSON, Table, Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

# Enums
class ProductTypeEnum(str, PyEnum):
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

class UserTypeEnum(str, PyEnum):
    ADMIN = "Администратор"
    ENGINEER = "Инженер"
    OPERATOR = "Оператор"
    SUPERVISER = "Старший смены"
    
class ProfileTypeEnum(str, PyEnum):
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


class WorkshopEnum(str, PyEnum):
    PROFILE = "Прокат профилей"
    KLAMER = "Прокат клямеров"
    BRACKET = "Прокат кронштейнов"
    EXTENSION_BRACKET = "Гибка удлинителей кронштейнов"
    ENGINEER = "Инженер"
    BENDING = "Гибка"
    CUTTING = "Резка"
    COORDINATE_PUNCHING = "Координатка"
    PAINTING = "Покраска"

class ManagerEnum(str, PyEnum):
    NOVIKOV = "Новиков"
    SEMICHEV = "Семичев С."
    PTICHKINA = "Птичкина"
    VIKULINA = "Викулина"
    GAVRILOVEC = "Гавриловец"
    SEMICHEV_YOUNGER = "Семичев Д."

class KlamerTypeEnum(str, PyEnum):
    IN_LINE = "Рядный"
    STARTING = "Стартовый"
    ANGULAR = "Угловой"

class CassetteTypeEnum(str, PyEnum):
    KZT_STD = "Зактрытого типа(стандарт)"
    KOT_STD = "Открытого типа(стандарт)"
    KOTVO = "Открытого типа, отв. в вертикальных рустах"
    KZT = "Закрытого типа"
    KOT = "Открытого типа"
    OTHER = "Другое"

class MaterialFormEnum(str, PyEnum):
    SHEET = "Лист"
    COIL = "Рулон"
    STRIP = "Штрипс"

class MaterialTypeEnum(str, PyEnum):
    ALUMINIUM = "Алюминий"
    STEEL = "Сталь"
    STAINLESS_STEEL = "Нержавеющая сталь"
    ZINC = "Оцинковка"
    POLYMER = "Полимер"

class MaterialThicknessEnum(str, PyEnum):
    ZERO_FIVE = "0.5мм"
    ZERO_SEVEN = "0.7мм"
    ONE = "1.0мм"
    ONE_TWO = "1.2мм"
    ONE_FIVE = "1.5мм"
    TWO = "2.0мм"
    THREE = "3.0мм"

class UrgencyEnum(str, PyEnum):
    LOW = "Низкая"
    MEDIUM = "Нормальная"
    HIGH = "Высокая"

class StatusEnum(str, PyEnum):
    NEW = "Новая"
    IN_WORK = "В работе"
    COMPLETED = "Выполнена"
    CANCELED = "Отменена"
    ON_HOLD = "На удержании"

# Промежуточные таблицы (Many-to-Many)
user_workshop_association = Table(
    "user_workshop_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("workshop_id", Integer, ForeignKey("workshop.id"), primary_key=True)
)

task_responsible_association = Table(
    "task_responsible_association",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("task.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

comment_user_association = Table(
    "comment_user_association",
    Base.metadata,
    Column("comment_id", Integer, ForeignKey("comment.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

# Users Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    firstname = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    telegram = Column(String(50), nullable=True, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(60), nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    is_active = Column(Boolean, default=True)
    # Связь Many-to-Many с Task (Ответственные)
    tasks = relationship("Task", secondary=task_responsible_association, back_populates="responsible_users")
    workshops = relationship("Workshop", secondary=user_workshop_association, back_populates="users")
    comments = relationship("Comment", secondary=comment_user_association, back_populates="users")

# Bid Table
class Bid(Base):
    __tablename__ = "bid"
    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(String(50), nullable=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    manager = Column(Enum(ManagerEnum), nullable=False)
    files = relationship("Files", back_populates="bid", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="bid", cascade="all, delete-orphan")
    customer = relationship("Customer", back_populates="bid")


# Task Table
class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey("bid.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("material.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=True)
    urgency = Column(Enum(UrgencyEnum), nullable=False)
    status = Column(Enum(StatusEnum), default="NEW")
    waste = Column(String(50), nullable=True)
    weight = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # One-to-Many связи
    sheets = relationship("Sheets", back_populates="task", cascade="all, delete-orphan")
    
    bid = relationship("Bid", back_populates="tasks")
    product = relationship("Product", back_populates="tasks", cascade="all, delete-orphan", single_parent=True)
    material = relationship("Material", back_populates="tasks", cascade="all, delete-orphan", single_parent=True)
    # One-to-Many связь с Comment
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    workshops = relationship("TaskWorkshop", back_populates="task", cascade="all, delete-orphan")
    # Many-to-Many связи
   
    responsible_users = relationship("User", secondary=task_responsible_association, back_populates="tasks")

# Workshop Table
class Workshop(Base):
    __tablename__ = "workshop"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(WorkshopEnum), nullable=False)
    # Связь Many-to-Many с Task
    task_workshops = relationship("TaskWorkshop", back_populates="workshop", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_workshop_association, back_populates="workshops")
    
# TaskWorkshop Table
class TaskWorkshop(Base):
    __tablename__ = "task_workshops"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    workshop_id = Column(Integer, ForeignKey("workshop.id", ondelete="CASCADE"))
    status = Column(Enum(StatusEnum), default="ON_HOLD")  # Статус выполнения в цехе

    task = relationship("Task", back_populates="workshops")
    workshop = relationship("Workshop", back_populates="task_workshops")
    
# Customer Table
class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    bid = relationship("Bid", back_populates="customer")

# Product Table
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ProductTypeEnum), nullable=False)
    tasks = relationship("Task", back_populates="product", uselist=False)
    profile = relationship("Profile", back_populates="product", cascade="all, delete-orphan")
    klamer = relationship("Klamer", back_populates="product", cascade="all, delete-orphan")
    bracket = relationship("Bracket", back_populates="product", cascade="all, delete-orphan")
    extension_bracket = relationship("ExtensionBracket", back_populates="product", cascade="all, delete-orphan")
    cassette = relationship("Cassette", back_populates="product", cascade="all, delete-orphan")
    linear_panel = relationship("LinearPanel", back_populates="product", cascade="all, delete-orphan")

# Profile Table
class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    profile_type_id = Column(Integer, ForeignKey("profile_type.id"), nullable=False)
    length = Column(Integer, nullable=False)
    product = relationship("Product", back_populates="profile")
    profile_type = relationship("ProfileType")

class ProfileType(Base):
    __tablename__ = "profile_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)

# Klamer Table
class Klamer(Base):
    __tablename__ = "klamer"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    type = Column(Enum(KlamerTypeEnum), nullable=False)
    product = relationship("Product", back_populates="klamer")

# Bracket Table
class Bracket(Base):
    __tablename__ = "bracket"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    width = Column(Integer, nullable=False)
    length = Column(String(50), nullable=False)
    thickness = Column(Integer, nullable=False)
    product = relationship("Product", back_populates="bracket")

# Extension Bracket Table
class ExtensionBracket(Base):
    __tablename__ = "extension_bracket"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    width = Column(Integer, nullable=False)
    length = Column(String(50), nullable=False)
    heel = Column(Boolean, default=True)
    product = relationship("Product", back_populates="extension_bracket")

# Cassette Table
class Cassette(Base):
    __tablename__ = "cassette"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    cassette_type = Column(Enum(CassetteTypeEnum), nullable=False)
    description = Column(String(255), nullable=True)
    product = relationship("Product", back_populates="cassette")

# Linear Panel Table
class LinearPanel(Base):
    __tablename__ = "linear_panel"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    field = Column(Integer, nullable=False)
    rust = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)
    butt_end = Column(Boolean, nullable=False, default=False)
    product = relationship("Product", back_populates="linear_panel")

# Materials Tables
class Material(Base):
    __tablename__ = "material"
    id = Column(Integer, primary_key=True, index=True)
    form = Column(Enum(MaterialFormEnum), nullable=False)
    type = Column(Enum(MaterialTypeEnum), nullable=False)
    thickness = Column(Enum(MaterialThicknessEnum), nullable=False)
    color_id = Column(Integer, ForeignKey("material_color.id"), nullable=True)
    painting = Column(Boolean, default=False)
    tasks = relationship("Task", back_populates="material")
    color = relationship("MaterialColor", back_populates="materials")

# MaterialColor Table
class MaterialColor(Base):
    __tablename__ = "material_color"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    materials = relationship("Material", back_populates="color", passive_deletes=True)


# Additional Tables
class Sheets(Base):
    __tablename__ = "sheets"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)  # Привязываем к Task
    width_sheet = Column(Integer, ForeignKey("sheet_width.id"), nullable=False)
    length_sheet = Column(Integer, ForeignKey("sheet_length.id"), nullable=False )
    quantity = Column(Integer, nullable=False)
    # Обратная связь One-to-Many
    task = relationship("Task", back_populates="sheets")
    width = relationship("SheetWidth", back_populates="sheets")
    length = relationship("SheetLength", back_populates="sheets")

class SheetWidth(Base):
    __tablename__ = "sheet_width"
    id = Column(Integer, primary_key=True, index=True)
    width = Column(String(50), nullable=False, unique=True)
    sheets = relationship("Sheets", back_populates="width")

class SheetLength(Base):
    __tablename__ = "sheet_length"
    id = Column(Integer, primary_key=True, index=True)
    length = Column(String(50), nullable=False, unique=True)
    sheets = relationship("Sheets", back_populates="length")

class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey("bid.id"), nullable=False)  # Привязываем к Task
    file_name = Column(String(255), nullable=False)
    file_path = Column(String, nullable=False)

    # Обратная связь One-to-Many
    bid = relationship("Bid", back_populates="files")

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    comment = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)


    # One-to-Many связь с Task
    task = relationship("Task", back_populates="comments")

    # Many-to-Many связь с User
    users = relationship("User", secondary=comment_user_association, back_populates="comments")

