"""API quan ly phu phi."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_phu_phi import (
    cap_nhat_phu_phi,
    lay_danh_sach_phu_phi,
    lay_phu_phi_theo_ma,
    tao_phu_phi,
    xoa_phu_phi,
)
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/phu-phi", tags=["Quan ly Phu phi"])


class PhuPhiCreate(BaseModel):
    ten_phu_phi: str = Field(..., min_length=1, max_length=100)
    so_tien: float = Field(..., gt=0)
    dang_ap_dung: bool = True
    mo_ta: str | None = None


class PhuPhiUpdate(BaseModel):
    ten_phu_phi: str | None = None
    so_tien: float | None = Field(default=None, gt=0)
    dang_ap_dung: bool | None = None
    mo_ta: str | None = None


class PhuPhiResponse(BaseModel):
    ma_phu_phi: int
    ten_phu_phi: str
    so_tien: float
    dang_ap_dung: bool
    mo_ta: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[PhuPhiResponse])
def api_danh_sach_phu_phi(
    chi_dang_ap_dung: bool = False,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach phu phi."""
    return lay_danh_sach_phu_phi(db, chi_dang_ap_dung)


@router.post("", response_model=PhuPhiResponse, status_code=status.HTTP_201_CREATED)
def api_tao_phu_phi(
    data: PhuPhiCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Them phu phi moi."""
    return tao_phu_phi(
        db,
        ten_phu_phi=data.ten_phu_phi,
        so_tien=data.so_tien,
        dang_ap_dung=data.dang_ap_dung,
        mo_ta=data.mo_ta,
    )


@router.put("/{ma_phu_phi}", response_model=PhuPhiResponse)
def api_cap_nhat_phu_phi(
    ma_phu_phi: int,
    data: PhuPhiUpdate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Cap nhat phu phi."""
    pp = lay_phu_phi_theo_ma(db, ma_phu_phi)
    if not pp:
        raise HTTPException(status_code=404, detail="Khong tim thay phu phi")
    return cap_nhat_phu_phi(db, pp, **data.model_dump(exclude_unset=True))


@router.delete("/{ma_phu_phi}", status_code=status.HTTP_204_NO_CONTENT)
def api_xoa_phu_phi(
    ma_phu_phi: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Xoa phu phi."""
    pp = lay_phu_phi_theo_ma(db, ma_phu_phi)
    if not pp:
        raise HTTPException(status_code=404, detail="Khong tim thay phu phi")
    xoa_phu_phi(db, pp)
    return None