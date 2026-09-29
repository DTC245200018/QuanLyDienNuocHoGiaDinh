"""Logic thanh toan va cong no."""

from datetime import date
from sqlalchemy.orm import Session

from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.thanh_toan import ThanhToan


def lay_danh_sach_thanh_toan(db: Session, ma_hoa_don: int | None = None) -> list[ThanhToan]:
    """Lay danh sach thanh toan."""
    query = db.query(ThanhToan)
    if ma_hoa_don:
        query = query.filter(ThanhToan.ma_hoa_don == ma_hoa_don)
    return query.order_by(ThanhToan.ngay_thanh_toan.desc()).all()


def ghi_nhan_thanh_toan(
    db: Session,
    ma_hoa_don: int,
    so_tien: float,
    ngay_thanh_toan: date | None = None,
    hinh_thuc: str = "tien_mat",
    ghi_chu: str | None = None,
) -> ThanhToan:
    """
    Ghi nhan thanh toan cho hoa don.
    Cap nhat so_tien_da_tra va trang_thai.
    """
    hoa_don = db.query(HoaDon).filter(HoaDon.ma_hoa_don == ma_hoa_don).first()
    if not hoa_don:
        raise ValueError("Khong tim thay hoa don")

    if so_tien <= 0:
        raise ValueError("So tien thanh toan phai lon hon 0")

    con_no = float(hoa_don.tong_tien) - float(hoa_don.so_tien_da_tra)
    if so_tien > con_no + 0.01:  # cho phep sai so nho
        raise ValueError(f"So tien thanh toan ({so_tien}) lon hon cong no con lai ({con_no})")

    if ngay_thanh_toan is None:
        ngay_thanh_toan = date.today()

    # Tao ban ghi thanh toan
    tt = ThanhToan(
        ma_hoa_don=ma_hoa_don,
        so_tien=so_tien,
        ngay_thanh_toan=ngay_thanh_toan,
        hinh_thuc=hinh_thuc,
        ghi_chu=ghi_chu,
    )
    db.add(tt)

    # Cap nhat hoa don
    hoa_don.so_tien_da_tra = float(hoa_don.so_tien_da_tra) + so_tien
    con_no_moi = float(hoa_don.tong_tien) - float(hoa_don.so_tien_da_tra)

    if con_no_moi <= 0.01:
        hoa_don.trang_thai = "da_thanh_toan"
        hoa_don.so_tien_da_tra = hoa_don.tong_tien  # chuan hoa
    else:
        hoa_don.trang_thai = "thanh_toan_mot_phan"

    db.commit()
    db.refresh(tt)
    return tt


def tinh_cong_no(db: Session, ma_hoa_don: int) -> dict:
    """Tinh cong no con lai cua hoa don."""
    hoa_don = db.query(HoaDon).filter(HoaDon.ma_hoa_don == ma_hoa_don).first()
    if not hoa_don:
        raise ValueError("Khong tim thay hoa don")

    tong = float(hoa_don.tong_tien)
    da_tra = float(hoa_don.so_tien_da_tra)
    con_no = max(0, tong - da_tra)

    return {
        "ma_hoa_don": ma_hoa_don,
        "tong_tien": tong,
        "so_tien_da_tra": da_tra,
        "cong_no": con_no,
        "trang_thai": hoa_don.trang_thai,
    }