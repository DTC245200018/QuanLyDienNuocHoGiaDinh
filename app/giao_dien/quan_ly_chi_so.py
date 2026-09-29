"""API quan ly chi so dien / nuoc."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_chi_so import (
    chot_chi_so,
    lay_chi_so_moi_nhat,
    lay_chi_so_theo_ma,
    lay_danh_sach_chi_so,
    tao_chi_so,
)
from app.luan_ly.xu_ly_cong_to import lay_cong_to_theo_ma
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/chi-so", tags=["Quan ly Chi so"])


class ChiSoCreate(BaseModel):
    ma_cong_to: int
    chi_so_cu: float = Field(..., ge=0)
    chi_so_moi: float = Field(..., ge=0)
    ngay_ghi: date
    la_tu_dong: bool = False
    la_uoc_tinh: bool = False
    ghi_chu: str | None = None


class ChiSoResponse(BaseModel):
    ma_chi_so: int
    ma_cong_to: int
    chi_so_cu: float
    chi_so_moi: float
    ngay_ghi: date
    la_tu_dong: bool
    la_uoc_tinh: bool
    da_chot: bool
    ghi_chu: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[ChiSoResponse])
def api_danh_sach_chi_so(
    ma_cong_to: int | None = None,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach chi so (co the loc theo ma_cong_to)."""
    return lay_danh_sach_chi_so(db, ma_cong_to)


@router.get("/moi-nhat/{ma_cong_to}", response_model=ChiSoResponse | None)
def api_chi_so_moi_nhat(
    ma_cong_to: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay chi so moi nhat cua 1 cong to."""
    if not lay_cong_to_theo_ma(db, ma_cong_to):
        raise HTTPException(status_code=404, detail="Khong tim thay cong to")
    return lay_chi_so_moi_nhat(db, ma_cong_to)


@router.post("", response_model=ChiSoResponse, status_code=status.HTTP_201_CREATED)
def api_tao_chi_so(
    data: ChiSoCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """
    Nhap chi so moi (thu cong).
    Neu chi_so_moi < chi_so_cu -> tra ve loi 400.
    """
    if not lay_cong_to_theo_ma(db, data.ma_cong_to):
        raise HTTPException(status_code=404, detail="Khong tim thay cong to")

    try:
        return tao_chi_so(
            db,
            ma_cong_to=data.ma_cong_to,
            chi_so_cu=data.chi_so_cu,
            chi_so_moi=data.chi_so_moi,
            ngay_ghi=data.ngay_ghi,
            la_tu_dong=data.la_tu_dong,
            la_uoc_tinh=data.la_uoc_tinh,
            ghi_chu=data.ghi_chu,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{ma_chi_so}/chot", response_model=ChiSoResponse)
def api_chot_chi_so(
    ma_chi_so: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Danh dau chi so da chot (san sang lap hoa don)."""
    cs = lay_chi_so_theo_ma(db, ma_chi_so)
    if not cs:
        raise HTTPException(status_code=404, detail="Khong tim thay chi so")
    return chot_chi_so(db, cs)