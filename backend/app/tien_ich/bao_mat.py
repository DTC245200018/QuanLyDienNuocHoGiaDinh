"""
Cac ham xu ly mat khau va JWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

# Cau hinh ma hoa mat khau
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cau hinh JWT (chi dung cho demo, sau nay dua vao .env)
SECRET_KEY = "do-an-dien-nuoc-secret-key-doi-khi-deploy"
ALGORITHM = "HS256"
THOI_HAN_TOKEN_PHUT = 60 * 24  # 24 gio


def bam_mat_khau(mat_khau: str) -> str:
    """Bam mat khau bang bcrypt."""
    return pwd_context.hash(mat_khau)


def kiem_tra_mat_khau(mat_khau_tho: str, mat_khau_hash: str) -> bool:
    """Kiem tra mat khau nhap vao co khop hash khong."""
    return pwd_context.verify(mat_khau_tho, mat_khau_hash)


def tao_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Tao JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=THOI_HAN_TOKEN_PHUT)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def giai_ma_token(token: str) -> dict[str, Any] | None:
    """Giai ma JWT, tra ve payload neu hop le."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None