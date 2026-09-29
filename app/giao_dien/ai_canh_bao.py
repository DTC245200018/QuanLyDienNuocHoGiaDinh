"""API AI phan tich canh bao va goi y tiet kiem."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.phan_tich_ai import lay_canh_bao_phong, phan_tich_phong
from app.luan_ly.xu_ly_phong import lay_phong_theo_ma
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/ai", tags=["AI Phan tich & Canh bao"])


class CanhBaoResponse(BaseModel):
    ma_canh_bao: int
    ma_phong: int
    ma_hoa_don: int | None
    loai_canh_bao: str
    noi_dung: str
    muc_do: str
    da_xu_ly: bool

    class Config:
        from_attributes = True


class PhanTichRequest(BaseModel):
    ma_phong: int
    ma_hoa_don: int | None = None


@router.post("/phan-tich", response_model=CanhBaoResponse)
async def api_phan_tich_ai(
    data: PhanTichRequest,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """
    Phan tich tieu thu phong bang AI (hoac fallback).
    Tra ve canh bao + goi y tiet kiem.
    """
    if not lay_phong_theo_ma(db, data.ma_phong):
        raise HTTPException(status_code=404, detail="Khong tim thay phong")

    try:
        return await phan_tich_phong(db, data.ma_phong, data.ma_hoa_don)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/canh-bao/{ma_phong}", response_model=list[CanhBaoResponse])
def api_lich_su_canh_bao(
    ma_phong: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay lich su canh bao AI cua phong."""
    if not lay_phong_theo_ma(db, ma_phong):
        raise HTTPException(status_code=404, detail="Khong tim thay phong")
    return lay_canh_bao_phong(db, ma_phong)