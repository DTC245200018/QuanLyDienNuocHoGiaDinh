"""Logic xu ly phu phi."""

from sqlalchemy.orm import Session

from app.mo_hinh.phu_phi import PhuPhi


def lay_danh_sach_phu_phi(db: Session, chi_dang_ap_dung: bool = False) -> list[PhuPhi]:
    """Lay danh sach phu phi."""
    query = db.query(PhuPhi)
    if chi_dang_ap_dung:
        query = query.filter(PhuPhi.dang_ap_dung == True)
    return query.order_by(PhuPhi.ten_phu_phi).all()


def lay_phu_phi_theo_ma(db: Session, ma_phu_phi: int) -> PhuPhi | None:
    """Lay 1 phu phi theo ma."""
    return db.query(PhuPhi).filter(PhuPhi.ma_phu_phi == ma_phu_phi).first()


def tao_phu_phi(
    db: Session,
    ten_phu_phi: str,
    so_tien: float,
    dang_ap_dung: bool = True,
    mo_ta: str | None = None,
) -> PhuPhi:
    """Tao phu phi moi."""
    pp = PhuPhi(
        ten_phu_phi=ten_phu_phi,
        so_tien=so_tien,
        dang_ap_dung=dang_ap_dung,
        mo_ta=mo_ta,
    )
    db.add(pp)
    db.commit()
    db.refresh(pp)
    return pp


def cap_nhat_phu_phi(db: Session, pp: PhuPhi, **kwargs) -> PhuPhi:
    """Cap nhat phu phi."""
    for key, value in kwargs.items():
        if value is not None and hasattr(pp, key):
            setattr(pp, key, value)
    db.commit()
    db.refresh(pp)
    return pp


def xoa_phu_phi(db: Session, pp: PhuPhi) -> None:
    """Xoa phu phi."""
    db.delete(pp)
    db.commit()