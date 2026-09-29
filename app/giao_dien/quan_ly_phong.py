"""API quan ly ho gia dinh."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_phong import (
    cap_nhat_phong,
    lay_danh_sach_phong,
    lay_phong_theo_ma,
    lay_phong_theo_ten,
    tao_phong,
    xoa_phong,
)
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/phong", tags=["Quan ly Ho gia dinh"])


class PhongCreate(BaseModel):
    """Du lieu tao ho gia dinh moi."""

    ten_phong: str = Field(..., min_length=1, max_length=50, description="Ten ho gia dinh")
    so_nguoi_o: int = Field(default=1, ge=1, description="So nguoi trong ho")
    ngay_bat_dau_thue: date | None = None
    trang_thai: str = "dang_thue"
    ma_khach_thue: int | None = None
    ghi_chu: str | None = None


class PhongUpdate(BaseModel):
    """Du lieu cap nhat ho gia dinh."""

    ten_phong: str | None = None
    so_nguoi_o: int | None = Field(default=None, ge=1)
    ngay_bat_dau_thue: date | None = None
    trang_thai: str | None = None
    ma_khach_thue: int | None = None
    ghi_chu: str | None = None


class PhongResponse(BaseModel):
    """Thong tin ho gia dinh tra ve."""

    ma_phong: int
    ten_phong: str
    so_nguoi_o: int
    ngay_bat_dau_thue: date | None
    trang_thai: str
    ma_khach_thue: int | None
    ghi_chu: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[PhongResponse])
def api_danh_sach_ho(
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach tat ca ho gia dinh (chi quan ly)."""
    return lay_danh_sach_phong(db)


@router.get("/{ma_phong}", response_model=PhongResponse)
def api_chi_tiet_ho(
    ma_phong: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay chi tiet 1 ho gia dinh."""
    phong = lay_phong_theo_ma(db, ma_phong)
    if not phong:
        raise HTTPException(status_code=404, detail="Khong tim thay ho gia dinh")
    return phong


@router.post("", response_model=PhongResponse, status_code=status.HTTP_201_CREATED)
def api_tao_ho(
    data: PhongCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Them ho gia dinh moi."""
    if lay_phong_theo_ten(db, data.ten_phong):
        raise HTTPException(status_code=400, detail="Ten ho gia dinh da ton tai")
    return tao_phong(
        db,
        ten_phong=data.ten_phong,
        so_nguoi_o=data.so_nguoi_o,
        ngay_bat_dau_thue=data.ngay_bat_dau_thue,
        trang_thai=data.trang_thai,
        ma_khach_thue=data.ma_khach_thue,
        ghi_chu=data.ghi_chu,
    )


@router.put("/{ma_phong}", response_model=PhongResponse)
def api_cap_nhat_ho(
    ma_phong: int,
    data: PhongUpdate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Cap nhat ho gia dinh."""
    phong = lay_phong_theo_ma(db, ma_phong)
    if not phong:
        raise HTTPException(status_code=404, detail="Khong tim thay ho gia dinh")

    if data.ten_phong and data.ten_phong != phong.ten_phong:
        if lay_phong_theo_ten(db, data.ten_phong):
            raise HTTPException(status_code=400, detail="Ten ho gia dinh da ton tai")

    return cap_nhat_phong(db, phong, **data.model_dump(exclude_unset=True))


@router.delete("/{ma_phong}", status_code=status.HTTP_204_NO_CONTENT)
def api_xoa_ho(
    ma_phong: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Xoa ho gia dinh."""
    phong = lay_phong_theo_ma(db, ma_phong)
    if not phong:
        raise HTTPException(status_code=404, detail="Khong tim thay ho gia dinh")
    xoa_phong(db, phong)
    return None