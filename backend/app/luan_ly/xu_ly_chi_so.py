"""Logic xu ly chi so dien / nuoc."""

from datetime import date
from sqlalchemy.orm import Session

from app.mo_hinh.chi_so import ChiSo
from app.mo_hinh.cong_to import CongTo


def lay_danh_sach_chi_so(db: Session, ma_cong_to: int | None = None) -> list[ChiSo]:
    """Lay danh sach chi so, co the loc theo cong to."""
    query = db.query(ChiSo)
    if ma_cong_to:
        query = query.filter(ChiSo.ma_cong_to == ma_cong_to)
    return query.order_by(ChiSo.ngay_ghi.desc()).all()


def lay_chi_so_theo_ma(db: Session, ma_chi_so: int) -> ChiSo | None:
    """Lay 1 chi so theo ma."""
    return db.query(ChiSo).filter(ChiSo.ma_chi_so == ma_chi_so).first()


def lay_chi_so_moi_nhat(db: Session, ma_cong_to: int) -> ChiSo | None:
    """Lay chi so moi nhat cua 1 cong to."""
    return (
        db.query(ChiSo)
        .filter(ChiSo.ma_cong_to == ma_cong_to)
        .order_by(ChiSo.ngay_ghi.desc(), ChiSo.ma_chi_so.desc())
        .first()
    )


def tao_chi_so(
    db: Session,
    ma_cong_to: int,
    chi_so_cu: float,
    chi_so_moi: float,
    ngay_ghi: date,
    la_tu_dong: bool = False,
    la_uoc_tinh: bool = False,
    da_chot: bool = False,
    ghi_chu: str | None = None,
) -> ChiSo:
    """
    Tao chi so moi.
    Rang buoc: chi_so_moi phai >= chi_so_cu.
    """
    if chi_so_moi < chi_so_cu:
        raise ValueError(
            f"Chi so moi ({chi_so_moi}) khong duoc nho hon chi so cu ({chi_so_cu}). "
            "Vui long kiem tra lai cong to."
        )

    cs = ChiSo(
        ma_cong_to=ma_cong_to,
        chi_so_cu=chi_so_cu,
        chi_so_moi=chi_so_moi,
        ngay_ghi=ngay_ghi,
        la_tu_dong=la_tu_dong,
        la_uoc_tinh=la_uoc_tinh,
        da_chot=da_chot,
        ghi_chu=ghi_chu,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def chot_chi_so(db: Session, chi_so: ChiSo) -> ChiSo:
    """Danh dau chi so da chot (dung de lap hoa don)."""
    chi_so.da_chot = True
    db.commit()
    db.refresh(chi_so)
    return chi_so