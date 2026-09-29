"""Logic lap hoa don dien nuoc (chi tien dien + tien nuoc)."""

from datetime import date

from sqlalchemy.orm import Session

from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.chi_tiet_hoa_don import ChiTietHoaDon
from app.mo_hinh.cong_to import CongTo, LoaiCongTo
from app.mo_hinh.don_gia import LoaiDonGia
from app.luan_ly.xu_ly_chi_so import lay_chi_so_moi_nhat
from app.luan_ly.xu_ly_don_gia import lay_don_gia_dang_ap_dung


def lay_danh_sach_hoa_don(db: Session, ma_phong: int | None = None) -> list[HoaDon]:
    query = db.query(HoaDon)
    if ma_phong:
        query = query.filter(HoaDon.ma_phong == ma_phong)
    return query.order_by(HoaDon.ma_phong.asc(), HoaDon.ky_hoa_don.desc()).all()
def lay_hoa_don_theo_ma(db: Session, ma_hoa_don: int) -> HoaDon | None:
    return db.query(HoaDon).filter(HoaDon.ma_hoa_don == ma_hoa_don).first()


def _lay_don_gia_co_dinh(db: Session, loai: LoaiDonGia) -> float:
    ds = lay_don_gia_dang_ap_dung(db, loai)
    if not ds:
        raise ValueError(f"Chua cau hinh don gia {loai.value}")
    return float(ds[0].don_gia)


def _lay_cong_to_phong(db: Session, ma_phong: int, loai: LoaiCongTo) -> CongTo | None:
    return (
        db.query(CongTo)
        .filter(CongTo.ma_phong == ma_phong, CongTo.loai_cong_to == loai)
        .first()
    )


def lap_hoa_don(
    db: Session,
    ma_phong: int,
    ky_hoa_don: str,
    ngay_lap: date | None = None,
) -> HoaDon:
    """Lap hoa don: tieu thu x don gia dang ap dung (khong phu phi)."""
    if ngay_lap is None:
        ngay_lap = date.today()

    ct_dien = _lay_cong_to_phong(db, ma_phong, LoaiCongTo.DIEN)
    ct_nuoc = _lay_cong_to_phong(db, ma_phong, LoaiCongTo.NUOC)
    if not ct_dien:
        raise ValueError("Phong chua gan cong to dien")
    if not ct_nuoc:
        raise ValueError("Phong chua gan cong to nuoc")

    cs_dien = lay_chi_so_moi_nhat(db, ct_dien.ma_cong_to)
    cs_nuoc = lay_chi_so_moi_nhat(db, ct_nuoc.ma_cong_to)
    if not cs_dien:
        raise ValueError("Chua co chi so dien")
    if not cs_nuoc:
        raise ValueError("Chua co chi so nuoc")

    tieu_thu_dien = float(cs_dien.chi_so_moi) - float(cs_dien.chi_so_cu)
    tieu_thu_nuoc = float(cs_nuoc.chi_so_moi) - float(cs_nuoc.chi_so_cu)
    if tieu_thu_dien < 0 or tieu_thu_nuoc < 0:
        raise ValueError("Chi so khong hop le (tieu thu am)")

    gia_dien = _lay_don_gia_co_dinh(db, LoaiDonGia.DIEN)
    gia_nuoc = _lay_don_gia_co_dinh(db, LoaiDonGia.NUOC)
    tien_dien = tieu_thu_dien * gia_dien
    tien_nuoc = tieu_thu_nuoc * gia_nuoc
    tong_tien = tien_dien + tien_nuoc

    hoa_don = HoaDon(
        ma_phong=ma_phong,
        ky_hoa_don=ky_hoa_don,
        ngay_lap=ngay_lap,
        tong_tien_dien=tien_dien,
        tong_tien_nuoc=tien_nuoc,
        tong_phu_phi=0,
        tong_tien=tong_tien,
        so_tien_da_tra=0,
        trang_thai="chua_thanh_toan",
    )
    db.add(hoa_don)
    db.flush()

    db.add_all(
        [
            ChiTietHoaDon(
                ma_hoa_don=hoa_don.ma_hoa_don,
                ten_khoan="Tien dien",
                so_luong=tieu_thu_dien,
                don_gia=gia_dien,
                thanh_tien=tien_dien,
            ),
            ChiTietHoaDon(
                ma_hoa_don=hoa_don.ma_hoa_don,
                ten_khoan="Tien nuoc",
                so_luong=tieu_thu_nuoc,
                don_gia=gia_nuoc,
                thanh_tien=tien_nuoc,
            ),
        ]
    )

    cs_dien.da_chot = True
    cs_nuoc.da_chot = True
    db.commit()
    db.refresh(hoa_don)
    return hoa_don


def lay_chi_tiet_hoa_don(db: Session, ma_hoa_don: int) -> list[ChiTietHoaDon]:
    return (
        db.query(ChiTietHoaDon)
        .filter(ChiTietHoaDon.ma_hoa_don == ma_hoa_don)
        .all()
    )