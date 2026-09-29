"""
Logic xac thuc dang nhap va phan quyen.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.co_so_du_lieu.ket_noi import SessionLocal
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro
from app.tien_ich.bao_mat import kiem_tra_mat_khau, tao_access_token, giai_ma_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/dang-nhap")


def lay_db():
    """Dependency lay session database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def xac_thuc_nguoi_dung(
    db: Session, ten_dang_nhap: str, mat_khau: str
) -> NguoiDung | None:
    """Kiem tra ten dang nhap va mat khau."""
    nguoi_dung = (
        db.query(NguoiDung)
        .filter(NguoiDung.ten_dang_nhap == ten_dang_nhap)
        .first()
    )
    if not nguoi_dung:
        return None
    if not nguoi_dung.dang_hoat_dong:
        return None
    if not kiem_tra_mat_khau(mat_khau, nguoi_dung.mat_khau_hash):
        return None
    return nguoi_dung


def tao_token_cho_nguoi_dung(nguoi_dung: NguoiDung) -> str:
    """Tao JWT cho nguoi dung da xac thuc."""
    data = {
        "sub": nguoi_dung.ten_dang_nhap,
        "ma_nguoi_dung": nguoi_dung.ma_nguoi_dung,
        "vai_tro": nguoi_dung.vai_tro.value,
    }
    return tao_access_token(data)


def lay_nguoi_dung_hien_tai(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(lay_db),
) -> NguoiDung:
    """Lay thong tin nguoi dung tu JWT (dung cho API can dang nhap)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Khong the xac thuc thong tin dang nhap",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = giai_ma_token(token)
    if payload is None:
        raise credentials_exception

    ten_dang_nhap: str | None = payload.get("sub")
    if ten_dang_nhap is None:
        raise credentials_exception

    nguoi_dung = (
        db.query(NguoiDung)
        .filter(NguoiDung.ten_dang_nhap == ten_dang_nhap)
        .first()
    )
    if nguoi_dung is None or not nguoi_dung.dang_hoat_dong:
        raise credentials_exception
    return nguoi_dung


def yeu_cau_quan_ly(
    nguoi_dung: NguoiDung = Depends(lay_nguoi_dung_hien_tai),
) -> NguoiDung:
    """Chi cho phep vai tro quan_ly."""
    if nguoi_dung.vai_tro != VaiTro.QUAN_LY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ban khong co quyen thuc hien chuc nang nay",
        )
    return nguoi_dung