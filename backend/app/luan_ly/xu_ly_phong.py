"""Logic xu ly ho gia dinh."""

from datetime import date
from sqlalchemy.orm import Session

from app.mo_hinh.phong import Phong
from app.mo_hinh.cong_to import CongTo, LoaiCongTo
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.chi_so import ChiSo
from app.tien_ich.bao_mat import bam_mat_khau


def lay_danh_sach_phong(db: Session) -> list[Phong]:
    """Lay tat ca ho gia dinh, sap xep theo ma ho tang dan."""
    return db.query(Phong).order_by(Phong.ma_phong.asc()).all()

def lay_phong_theo_ma(db: Session, ma_phong: int) -> Phong | None:
    """Lay 1 ho theo ma."""
    return db.query(Phong).filter(Phong.ma_phong == ma_phong).first()


def lay_phong_theo_ten(db: Session, ten_phong: str) -> Phong | None:
    """Tim ho theo ten."""
    return db.query(Phong).filter(Phong.ten_phong == ten_phong).first()


def _tao_tai_khoan_khach(db: Session, ten_phong: str) -> tuple[NguoiDung, str]:
    """Tao user khach thue. ho_ten = ten ho (khong them chu Khach)."""
    stt = db.query(NguoiDung).count() + 1
    ten_dn = f"khach{stt:02d}"
    while db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == ten_dn).first():
        stt += 1
        ten_dn = f"khach{stt:02d}"

    mat_khau_plain = "khach123"
    user = NguoiDung(
        ten_dang_nhap=ten_dn,
        mat_khau_hash=bam_mat_khau(mat_khau_plain),
        ho_ten=ten_phong.strip(),  # chi ho ten, khong them "Khach "
        vai_tro=VaiTro.KHACH_THUE,
        dang_hoat_dong=True,
    )
    db.add(user)
    db.flush()
    return user, mat_khau_plain


def tao_phong(
    db: Session,
    ten_phong: str,
    so_nguoi_o: int = 1,
    ngay_bat_dau_thue=None,
    trang_thai: str = "dang_thue",
    ma_khach_thue: int | None = None,
    ghi_chu: str | None = None,
    tao_cong_to: bool = True,
    tao_tai_khoan: bool = True,
) -> tuple[Phong, NguoiDung | None, str | None]:
    """
    Tao ho moi + (tuy chon) tai khoan khach + cong to dien/nuoc.
    Tra ve: (phong, user_khach|None, mat_khau_plain|None)
    """
    ten_phong = ten_phong.strip()
    # Bo tien to "Ho " neu nguoi dung van nhap
    if ten_phong.startswith("Hộ "):
        ten_phong = ten_phong[3:].strip()
    if ten_phong.lower().startswith("ho "):
        ten_phong = ten_phong[3:].strip()

    if lay_phong_theo_ten(db, ten_phong):
        raise ValueError(f"Ten ho '{ten_phong}' da ton tai")

    user = None
    mat_khau = None
    if tao_tai_khoan and ma_khach_thue is None:
        user, mat_khau = _tao_tai_khoan_khach(db, ten_phong)
        ma_khach_thue = user.ma_nguoi_dung

    phong = Phong(
        ten_phong=ten_phong,
        so_nguoi_o=so_nguoi_o,
        ngay_bat_dau_thue=ngay_bat_dau_thue or date.today(),
        trang_thai=trang_thai,
        ma_khach_thue=ma_khach_thue,
        ghi_chu=ghi_chu,
    )
    db.add(phong)
    db.flush()

    if tao_cong_to:
        db.add(
            CongTo(
                ma_thiet_bi=f"CT-DIEN-H{phong.ma_phong}",
                loai_cong_to=LoaiCongTo.DIEN,
                ma_phong=phong.ma_phong,
                dang_hoat_dong=True,
            )
        )
        db.add(
            CongTo(
                ma_thiet_bi=f"CT-NUOC-H{phong.ma_phong}",
                loai_cong_to=LoaiCongTo.NUOC,
                ma_phong=phong.ma_phong,
                dang_hoat_dong=True,
            )
        )

    db.commit()
    db.refresh(phong)
    return phong, user, mat_khau


def cap_nhat_phong(db: Session, phong: Phong, **kwargs) -> Phong:
    """Cap nhat thong tin ho."""
    for key, value in kwargs.items():
        if value is not None and hasattr(phong, key):
            setattr(phong, key, value)
    db.commit()
    db.refresh(phong)
    return phong


def xoa_phong(db: Session, phong: Phong) -> None:
    """
    Xoa ho gia dinh.
    Chi cho xoa khi chua co hoa don.
    """
    so_hd = db.query(HoaDon).filter(HoaDon.ma_phong == phong.ma_phong).count()
    if so_hd > 0:
        raise ValueError(
            f"Khong the xoa ho '{phong.ten_phong}' vi da co {so_hd} hoa don. "
            "Hay xu ly hoa don truoc."
        )

    cong_to_list = db.query(CongTo).filter(CongTo.ma_phong == phong.ma_phong).all()
    for ct in cong_to_list:
        db.query(ChiSo).filter(ChiSo.ma_cong_to == ct.ma_cong_to).delete()
        db.delete(ct)

    db.delete(phong)
    db.commit()