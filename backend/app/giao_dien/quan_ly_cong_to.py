"""API quan ly cong to dien / nuoc."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_cong_to import (
    cap_nhat_cong_to,
    lay_cong_to_theo_ma,
    lay_cong_to_theo_ma_thiet_bi,
    lay_cong_to_theo_phong,
    lay_danh_sach_cong_to,
    tao_cong_to,
    xoa_cong_to,
)
from app.luan_ly.xu_ly_phong import lay_phong_theo_ma
from app.mo_hinh.cong_to import LoaiCongTo
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/cong-to", tags=["Quan ly Cong to"])


class CongToCreate(BaseModel):
    ma_thiet_bi: str = Field(..., min_length=1, max_length=50)
    loai_cong_to: LoaiCongTo
    ma_phong: int | None = None
    dang_hoat_dong: bool = True


class CongToUpdate(BaseModel):
    ma_thiet_bi: str | None = None
    loai_cong_to: LoaiCongTo | None = None
    ma_phong: int | None = None
    dang_hoat_dong: bool | None = None


class CongToResponse(BaseModel):
    ma_cong_to: int
    ma_thiet_bi: str
    loai_cong_to: LoaiCongTo
    ma_phong: int | None
    dang_hoat_dong: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[CongToResponse])
def api_danh_sach_cong_to(
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach tat ca cong to."""
    return lay_danh_sach_cong_to(db)


@router.get("/phong/{ma_phong}", response_model=list[CongToResponse])
def api_cong_to_theo_phong(
    ma_phong: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay cong to cua 1 phong."""
    if not lay_phong_theo_ma(db, ma_phong):
        raise HTTPException(status_code=404, detail="Khong tim thay phong")
    return lay_cong_to_theo_phong(db, ma_phong)


@router.get("/{ma_cong_to}", response_model=CongToResponse)
def api_chi_tiet_cong_to(
    ma_cong_to: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay chi tiet 1 cong to."""
    cong_to = lay_cong_to_theo_ma(db, ma_cong_to)
    if not cong_to:
        raise HTTPException(status_code=404, detail="Khong tim thay cong to")
    return cong_to


@router.post("", response_model=CongToResponse, status_code=status.HTTP_201_CREATED)
def api_tao_cong_to(
    data: CongToCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Them cong to moi."""
    if lay_cong_to_theo_ma_thiet_bi(db, data.ma_thiet_bi):
        raise HTTPException(status_code=400, detail="Ma thiet bi da ton tai")

    if data.ma_phong and not lay_phong_theo_ma(db, data.ma_phong):
        raise HTTPException(status_code=400, detail="Phong khong ton tai")

    return tao_cong_to(
        db,
        ma_thiet_bi=data.ma_thiet_bi,
        loai_cong_to=data.loai_cong_to,
        ma_phong=data.ma_phong,
        dang_hoat_dong=data.dang_hoat_dong,
    )


@router.put("/{ma_cong_to}", response_model=CongToResponse)
def api_cap_nhat_cong_to(
    ma_cong_to: int,
    data: CongToUpdate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Cap nhat cong to (co the gan vao phong)."""
    cong_to = lay_cong_to_theo_ma(db, ma_cong_to)
    if not cong_to:
        raise HTTPException(status_code=404, detail="Khong tim thay cong to")

    if data.ma_thiet_bi and data.ma_thiet_bi != cong_to.ma_thiet_bi:
        if lay_cong_to_theo_ma_thiet_bi(db, data.ma_thiet_bi):
            raise HTTPException(status_code=400, detail="Ma thiet bi da ton tai")

    if data.ma_phong is not None and data.ma_phong != 0:
        if not lay_phong_theo_ma(db, data.ma_phong):
            raise HTTPException(status_code=400, detail="Phong khong ton tai")

    return cap_nhat_cong_to(db, cong_to, **data.model_dump(exclude_unset=True))


@router.delete("/{ma_cong_to}", status_code=status.HTTP_204_NO_CONTENT)
def api_xoa_cong_to(
    ma_cong_to: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Xoa cong to."""
    cong_to = lay_cong_to_theo_ma(db, ma_cong_to)
    if not cong_to:
        raise HTTPException(status_code=404, detail="Khong tim thay cong to")
    xoa_cong_to(db, cong_to)
    return None