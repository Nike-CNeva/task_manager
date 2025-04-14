from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import APIRouter, Form, Request, HTTPException, Response, status
from passlib.context import CryptContext
from settings import settings
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# Инициализация хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# В зависимости от того, где вам нужно проверять токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки авторизации через JWT.
    """
    async def dispatch(self, request: Request, call_next):
        access_token = request.cookies.get("access_token") or request.headers.get("Authorization")

        if access_token:
            if access_token.startswith("Bearer "):
                token_part = access_token.split(" ", 1)[1]
            else:
                token_part = access_token  # Если токен в куках

            try:
                payload = decode_access_token(token_part)
                request.state.user_id = payload.get("sub") if payload else None
            except JWTError:
                request.state.user_id = None
        else:
            if any(request.url.path.startswith(path) for path in ["/static", "/favicon.ico", "/login", "/"]):
                return await call_next(request)
            request.state.user_id = None

        if request.state.user_id is None and request.url.path not in ["/", "/login"]:
            response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
            return response  # Возвращаем Response без `await`

        print(f"🔍 Middleware получил запрос: {request.url}")

        try:
            response = await call_next(request)  # Пропускаем запрос дальше
        except Exception as e:
            print(f"❌ Ошибка в обработчике запроса: {e}")
            response = Response("Ошибка сервера", status_code=500)

        print(f"✅ Middleware пропустил запрос: {request.url}")

        return response

# ================================
# Хэширование и проверка пароля
# ================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие хэшированного пароля введенному."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хэширует пароль перед сохранением в БД."""
    return pwd_context.hash(password)

# ================================
# Генерация и проверка JWT токенов
# ================================
def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str):
    """
    Декодирует JWT-токен и проверяет его корректность.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

# Функция для извлечения токена из cookies
def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")  # Получаем токен из куки
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token
