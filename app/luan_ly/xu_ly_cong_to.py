"""Logic xu ly cong to."""

from sqlalchemy.orm import Session

from app.mo_hinh.cong_to import CongTo, LoaiCongTo


def lay_danh_sach_cong_to(db: Session) -> list[CongTo]:
    """Lay tat ca cong to."""
    return db.query(CongTo).order_by(CongTo.ma_cong_to).all()


def lay_cong_to_theo_ma(db: Session, ma_cong_to: int) -> CongTo | None:
    """Lay 1 cong to theo ma."""
    return db.query(CongTo).filter(CongTo.ma_cong_to == ma_cong_to).first()


def lay_cong_to_theo_ma_thiet_bi(db: Session, ma_thiet_bi: str) -> CongTo | None:
    """Tim cong to theo ma thiet bi."""
    return db.query(CongTo).filter(CongTo.ma_thiet_bi == ma_thiet_bi).first()


def lay_cong_to_theo_phong(db: Session, ma_phong: int) -> list[CongTo]:
    """Lay cac cong to cua 1 phong."""
    return db.query(CongTo).filter(CongTo.ma_phong == ma_phong).all()


def tao_cong_to(
    db: Session,
    ma_thiet_bi: str,
    loai_cong_to: LoaiCongTo,
    ma_phong: int | None = None,
    dang_hoat_dong: bool = True,
) -> CongTo:
    """Tao cong to moi."""
    cong_to = CongTo(
        ma_thiet_bi=ma_thiet_bi,
        loai_cong_to=loai_cong_to,
        ma_phong=ma_phong,
        dang_hoat_dong=dang_hoat_dong,
    )
    db.add(cong_to)
    db.commit()
    db.refresh(cong_to)
    return cong_to


def cap_nhat_cong_to(db: Session, cong_to: CongTo, **kwargs) -> CongTo:
    """Cap nhat thong tin cong to."""
    for key, value in kwargs.items():
        if value is not None and hasattr(cong_to, key):
            setattr(cong_to, key, value)
    db.commit()
    db.refresh(cong_to)
    return cong_to


def xoa_cong_to(db: Session, cong_to: CongTo) -> None:
    """Xoa cong to."""
    db.delete(cong_to)
    db.commit()