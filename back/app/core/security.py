import bcrypt
import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import get_settings

settings = get_settings()

MIN_PASSWORD_LENGTH = 6


def generate_password_hash(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def _is_django_hash(hashed: str) -> bool:
    return hashed.startswith("pbkdf2_sha256$")


def _verify_django_password(plain: str, hashed: str) -> bool:
    try:
        import base64
        parts = hashed.split("$")
        if len(parts) < 4:
            return False
        iterations = int(parts[1])
        salt = parts[2]
        stored = parts[3]
        derived = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), iterations)
        derived_b64 = base64.b64encode(derived).decode().strip()
        return derived_b64 == stored
    except (ValueError, IndexError):
        return False


def _verify_bcrypt_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except (ValueError, AttributeError):
        return False


def verify_password(plain: str, hashed: str) -> bool:
    if _is_django_hash(hashed):
        return _verify_django_password(plain, hashed)
    return _verify_bcrypt_password(plain, hashed)


def password_meets_requirements(password: str) -> tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Mínimo de {MIN_PASSWORD_LENGTH} caracteres"
    if not any(c.isupper() for c in password):
        return False, "Deve conter pelo menos uma letra maiúscula"
    if not any(c.islower() for c in password):
        return False, "Deve conter pelo menos uma letra minúscula"
    if not any(c.isdigit() for c in password):
        return False, "Deve conter pelo menos um número"
    return True, ""


def generate_temp_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") not in ("access", "refresh"):
            return None
        return payload
    except JWTError:
        return None
