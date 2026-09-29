"""API thanh toan va cong no."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.luan_ly.xac_thuc import lay_db, yeu_cau_quan_ly
from app.luan_ly.xu_ly_thanh_toan import (
    ghi_nhan_thanh_toan,
    lay_danh_sach_thanh_toan,
    tinh_cong_no,
)
from app.luan_ly.xu_ly_hoa_don import lay_hoa_don_theo_ma
from app.mo_hinh.nguoi_dung import NguoiDung

router = APIRouter(prefix="/api/thanh-toan", tags=["Thanh toan & Cong no"])


class ThanhToanCreate(BaseModel):
    ma_hoa_don: int
    so_tien: float = Field(..., gt=0)
    ngay_thanh_toan: date | None = None
    hinh_thuc: str = "tien_mat"  # tien_mat / chuyen_khoan
    ghi_chu: str | None = None


class ThanhToanResponse(BaseModel):
    ma_thanh_toan: int
    ma_hoa_don: int
    so_tien: float
    ngay_thanh_toan: date
    hinh_thuc: str
    ghi_chu: str | None

    class Config:
        from_attributes = True


class CongNoResponse(BaseModel):
    ma_hoa_don: int
    tong_tien: float
    so_tien_da_tra: float
    cong_no: float
    trang_thai: str


@router.get("", response_model=list[ThanhToanResponse])
def api_danh_sach_thanh_toan(
    ma_hoa_don: int | None = None,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Lay danh sach thanh toan."""
    return lay_danh_sach_thanh_toan(db, ma_hoa_don)


@router.post("", response_model=ThanhToanResponse, status_code=status.HTTP_201_CREATED)
def api_ghi_nhan_thanh_toan(
    data: ThanhToanCreate,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Ghi nhan thanh toan (du hoac mot phan)."""
    if not lay_hoa_don_theo_ma(db, data.ma_hoa_don):
        raise HTTPException(status_code=404, detail="Khong tim thay hoa don")

    try:
        return ghi_nhan_thanh_toan(
            db,
            ma_hoa_don=data.ma_hoa_don,
            so_tien=data.so_tien,
            ngay_thanh_toan=data.ngay_thanh_toan,
            hinh_thuc=data.hinh_thuc,
            ghi_chu=data.ghi_chu,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cong-no/{ma_hoa_don}", response_model=CongNoResponse)
def api_xem_cong_no(
    ma_hoa_don: int,
    db: Session = Depends(lay_db),
    _: NguoiDung = Depends(yeu_cau_quan_ly),
):
    """Xem cong no con lai cua hoa don."""
    try:
        return tinh_cong_no(db, ma_hoa_don)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))