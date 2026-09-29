"""
API dang nhap va lay thong tin nguoi dung hien tai.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import (
    lay_db,
    lay_nguoi_dung_hien_tai,
    tao_token_cho_nguoi_dung,
    xac_thuc_nguoi_dung,
)
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(tags=["Xac thuc"])


class TokenResponse(BaseModel):
    """Phan hoi khi dang nhap thanh cong."""

    access_token: str
    token_type: str = "bearer"
    vai_tro: str
    ho_ten: str


class NguoiDungResponse(BaseModel):
    """Thong tin nguoi dung tra ve."""

    ma_nguoi_dung: int
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: str
    so_dien_thoai: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


@router.post("/api/dang-nhap", response_model=TokenResponse)
def dang_nhap(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(lay_db),
):
    """
    Dang nhap bang ten dang nhap va mat khau.
    Tra ve JWT token neu thanh cong.
    """
    nguoi_dung = xac_thuc_nguoi_dung(db, form_data.username, form_data.password)
    if not nguoi_dung:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ten dang nhap hoac mat khau khong chinh xac",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = tao_token_cho_nguoi_dung(nguoi_dung)
    return TokenResponse(
        access_token=token,
        vai_tro=nguoi_dung.vai_tro.value,
        ho_ten=nguoi_dung.ho_ten,
    )


@router.get("/api/toi", response_model=NguoiDungResponse)
def lay_thong_tin_toi(
    nguoi_dung: NguoiDung = Depends(lay_nguoi_dung_hien_tai),
):
    """Lay thong tin nguoi dung dang dang nhap."""
    return NguoiDungResponse(
        ma_nguoi_dung=nguoi_dung.ma_nguoi_dung,
        ten_dang_nhap=nguoi_dung.ten_dang_nhap,
        ho_ten=nguoi_dung.ho_ten,
        vai_tro=nguoi_dung.vai_tro.value,
        so_dien_thoai=nguoi_dung.so_dien_thoai,
        email=nguoi_dung.email,
    )