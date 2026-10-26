"""API cau hinh don gia dien / nuoc."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_don_gia import (
    cap_nhat_don_gia,
    lay_danh_sach_don_gia,
    lay_don_gia_dang_ap_dung,
    lay_don_gia_theo_ma,
    tao_don_gia,
    xoa_don_gia,
)
from app.mo_hinh.don_gia import LoaiDonGia
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/don-gia", tags=["Cau hinh Don gia"])


class DonGiaCreate(BaseModel):
    loai: LoaiDonGia
    ten_muc: str = Field(..., min_length=1, max_length=50)
    don_gia: float = Field(..., gt=0)
    ngay_hieu_luc: date
    tu_so: float | None = None
    den_so: float | None = None
    dang_ap_dung: bool = True


class DonGiaUpdate(BaseModel):
    ten_muc: str | None = None
    don_gia: float | None = Field(default=None, gt=0)
    ngay_hieu_luc: date | None = None
    tu_so: float | None = None
    den_so: float | None = None
    dang_ap_dung: bool | None = None


class DonGiaResponse(BaseModel):
    ma_don_gia: int
    loai: LoaiDonGia
    ten_muc: str
    tu_so: float | None
    den_so: float | None
    don_gia: float
    ngay_hieu_luc: date
    dang_ap_dung: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[DonGiaResponse])
def api_danh_sach_don_gia(
    loai: LoaiDonGia | None = None,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach don gia (co the loc theo loai=dien/nuoc)."""
    return lay_danh_sach_don_gia(db, loai)


@router.get("/dang-ap-dung/{loai}", response_model=list[DonGiaResponse])
def api_don_gia_dang_ap_dung(
    loai: LoaiDonGia,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay cac muc don gia dang ap dung cua 1 loai."""
    return lay_don_gia_dang_ap_dung(db, loai)


@router.post("", response_model=DonGiaResponse, status_code=status.HTTP_201_CREATED)
def api_tao_don_gia(
    data: DonGiaCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Them muc don gia moi."""
    return tao_don_gia(
        db,
        loai=data.loai,
        ten_muc=data.ten_muc,
        don_gia=data.don_gia,
        ngay_hieu_luc=data.ngay_hieu_luc,
        tu_so=data.tu_so,
        den_so=data.den_so,
        dang_ap_dung=data.dang_ap_dung,
    )


@router.put("/{ma_don_gia}", response_model=DonGiaResponse)
def api_cap_nhat_don_gia(
    ma_don_gia: int,
    data: DonGiaUpdate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Cap nhat muc don gia."""
    dg = lay_don_gia_theo_ma(db, ma_don_gia)
    if not dg:
        raise HTTPException(status_code=404, detail="Khong tim thay don gia")
    return cap_nhat_don_gia(db, dg, **data.model_dump(exclude_unset=True))


@router.delete("/{ma_don_gia}", status_code=status.HTTP_204_NO_CONTENT)
def api_xoa_don_gia(
    ma_don_gia: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Xoa muc don gia."""
    dg = lay_don_gia_theo_ma(db, ma_don_gia)
    if not dg:
        raise HTTPException(status_code=404, detail="Khong tim thay don gia")
    xoa_don_gia(db, dg)
    return None