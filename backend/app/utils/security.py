from datetime import datetime, timedelta
from typing import Optional
import hashlib
import hmac
import os
import base64
from jose import JWTError, jwt
from backend.app.config import settings


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.b64encode(salt + pwd_hash).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        decoded = base64.b64decode(hashed_password)
        salt = decoded[:16]
        stored_hash = decoded[16:]
        pwd_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt, 100000)
        return hmac.compare_digest(pwd_hash, stored_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.APP_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.APP_SECRET_KEY, algorithm=settings.APP_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[settings.APP_ALGORITHM])
        return payload
    except JWTError:
        return None
