"""Logic xu ly don gia dien / nuoc."""

from datetime import date
from sqlalchemy.orm import Session

from app.mo_hinh.don_gia import DonGia, LoaiDonGia


def lay_danh_sach_don_gia(db: Session, loai: LoaiDonGia | None = None) -> list[DonGia]:
    """Lay danh sach don gia, co the loc theo loai."""
    query = db.query(DonGia)
    if loai:
        query = query.filter(DonGia.loai == loai)
    return query.order_by(DonGia.loai, DonGia.tu_so).all()


def lay_don_gia_theo_ma(db: Session, ma_don_gia: int) -> DonGia | None:
    """Lay 1 don gia theo ma."""
    return db.query(DonGia).filter(DonGia.ma_don_gia == ma_don_gia).first()


def lay_don_gia_dang_ap_dung(db: Session, loai: LoaiDonGia) -> list[DonGia]:
    """Lay cac muc don gia dang ap dung cua 1 loai."""
    return (
        db.query(DonGia)
        .filter(DonGia.loai == loai, DonGia.dang_ap_dung == True)
        .order_by(DonGia.tu_so)
        .all()
    )


def tao_don_gia(
    db: Session,
    loai: LoaiDonGia,
    ten_muc: str,
    don_gia: float,
    ngay_hieu_luc: date,
    tu_so: float | None = None,
    den_so: float | None = None,
    dang_ap_dung: bool = True,
) -> DonGia:
    """Tao muc don gia moi."""
    dg = DonGia(
        loai=loai,
        ten_muc=ten_muc,
        tu_so=tu_so,
        den_so=den_so,
        don_gia=don_gia,
        ngay_hieu_luc=ngay_hieu_luc,
        dang_ap_dung=dang_ap_dung,
    )
    db.add(dg)
    db.commit()
    db.refresh(dg)
    return dg


def cap_nhat_don_gia(db: Session, dg: DonGia, **kwargs) -> DonGia:
    """Cap nhat don gia."""
    for key, value in kwargs.items():
        if value is not None and hasattr(dg, key):
            setattr(dg, key, value)
    db.commit()
    db.refresh(dg)
    return dg


def xoa_don_gia(db: Session, dg: DonGia) -> None:
    """Xoa muc don gia."""
    db.delete(dg)
    db.commit()