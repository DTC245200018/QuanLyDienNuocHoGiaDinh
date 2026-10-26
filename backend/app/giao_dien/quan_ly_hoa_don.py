"""API quan ly hoa don."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_hoa_don import (
    lap_hoa_don,
    lay_chi_tiet_hoa_don,
    lay_danh_sach_hoa_don,
    lay_hoa_don_theo_ma,
)
from app.luan_ly.xu_ly_phong import lay_phong_theo_ma
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/hoa-don", tags=["Quan ly Hoa don"])


class LapHoaDonRequest(BaseModel):
    ma_phong: int
    ky_hoa_don: str = Field(..., pattern=r"^\d{4}-\d{2}$")  # 2026-08
    ngay_lap: date | None = None


class HoaDonResponse(BaseModel):
    ma_hoa_don: int
    ma_phong: int
    ky_hoa_don: str
    ngay_lap: date
    tong_tien_dien: float
    tong_tien_nuoc: float
    tong_phu_phi: float
    tong_tien: float
    so_tien_da_tra: float
    trang_thai: str

    class Config:
        from_attributes = True


class ChiTietResponse(BaseModel):
    ma_chi_tiet: int
    ten_khoan: str
    so_luong: float | None
    don_gia: float | None
    thanh_tien: float

    class Config:
        from_attributes = True


@router.get("", response_model=list[HoaDonResponse])
def api_danh_sach_hoa_don(
    ma_phong: int | None = None,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach hoa don."""
    return lay_danh_sach_hoa_don(db, ma_phong)


@router.get("/{ma_hoa_don}", response_model=HoaDonResponse)
def api_chi_tiet_hoa_don(
    ma_hoa_don: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay thong tin 1 hoa don."""
    hd = lay_hoa_don_theo_ma(db, ma_hoa_don)
    if not hd:
        raise HTTPException(status_code=404, detail="Khong tim thay hoa don")
    return hd


@router.get("/{ma_hoa_don}/chi-tiet", response_model=list[ChiTietResponse])
def api_chi_tiet_cac_khoan(
    ma_hoa_don: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay cac khoan chi tiet trong hoa don."""
    if not lay_hoa_don_theo_ma(db, ma_hoa_don):
        raise HTTPException(status_code=404, detail="Khong tim thay hoa don")
    return lay_chi_tiet_hoa_don(db, ma_hoa_don)


@router.post("/lap", response_model=HoaDonResponse, status_code=status.HTTP_201_CREATED)
def api_lap_hoa_don(
    data: LapHoaDonRequest,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """
    Lap hoa don tu dong cho phong.
    Can co: cong to dien+nuoc, chi so, don gia.
    """
    if not lay_phong_theo_ma(db, data.ma_phong):
        raise HTTPException(status_code=404, detail="Khong tim thay phong")

    try:
        return lap_hoa_don(
            db,
            ma_phong=data.ma_phong,
            ky_hoa_don=data.ky_hoa_don,
            ngay_lap=data.ngay_lap,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))