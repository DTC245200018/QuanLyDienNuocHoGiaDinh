# -*- coding: utf-8 -*-
"""
Tao bo du lieu: 10 ho tieng Viet co dau (unicode escape).
Chi tinh TIEN DIEN + TIEN NUOC (khong phu phi).
Don gia: dien 3500d/kWh, nuoc 15000d/m3.

Chay: python -m app.tien_ich.tao_bo_du_lieu_10_ho
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from datetime import date
from sqlalchemy.orm import Session

from app.co_so_du_lieu.ket_noi import SessionLocal, kiem_tra_ket_noi
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro
from app.mo_hinh.phong import Phong
from app.mo_hinh.cong_to import CongTo, LoaiCongTo
from app.mo_hinh.chi_so import ChiSo
from app.mo_hinh.don_gia import DonGia, LoaiDonGia
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.chi_tiet_hoa_don import ChiTietHoaDon
from app.tien_ich.bao_mat import bam_mat_khau


# Ten ho dung unicode escape de tranh loi encoding tren Windows
DANH_SACH_HO = [
    ("H\u1ed9 Nguy\u1ec5n V\u0103n An", 4, 1000, 1125, 50, 58),
    ("H\u1ed9 Tr\u1ea7n Th\u1ecb B\u00ecnh", 2, 800, 920, 40, 47),
    ("H\u1ed9 L\u00ea V\u0103n C\u01b0\u1eddng", 3, 1100, 1250, 55, 63),
    ("H\u1ed9 Ph\u1ea1m Th\u1ecb Dung", 5, 1300, 1480, 60, 72),
    ("H\u1ed9 Ho\u00e0ng V\u0103n Em", 2, 900, 1010, 42, 49),
    ("H\u1ed9 V\u0169 Th\u1ecb Ph\u01b0\u01a1ng", 3, 1050, 1180, 48, 56),
    ("H\u1ed9 \u0110\u1eb7ng V\u0103n Giang", 4, 1200, 1360, 58, 68),
    ("H\u1ed9 B\u00f9i Th\u1ecb Hoa", 1, 700, 780, 35, 40),
    ("H\u1ed9 Ng\u00f4 V\u0103n H\u00f9ng", 6, 1500, 1720, 70, 85),
    ("H\u1ed9 \u0110\u1ed7 Th\u1ecb Lan", 2, 850, 960, 38, 45),
]

GIA_DIEN = 3500.0
GIA_NUOC = 15000.0


def _get_or_create_admin(db: Session) -> NguoiDung:
    admin = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "admin").first()
    if admin:
        return admin
    admin = NguoiDung(
        ten_dang_nhap="admin",
        mat_khau_hash=bam_mat_khau("admin123"),
        ho_ten="Nguyen Van Quan Ly",
        vai_tro=VaiTro.QUAN_LY,
        dang_hoat_dong=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def _tao_don_gia(db: Session) -> None:
    if not db.query(DonGia).filter(DonGia.loai == LoaiDonGia.DIEN).first():
        db.add(DonGia(
            loai=LoaiDonGia.DIEN,
            ten_muc="Gia dien co dinh",
            don_gia=GIA_DIEN,
            ngay_hieu_luc=date(2026, 1, 1),
            dang_ap_dung=True,
        ))
        print(f"Don gia dien: {GIA_DIEN:.0f} d/kWh")

    if not db.query(DonGia).filter(DonGia.loai == LoaiDonGia.NUOC).first():
        db.add(DonGia(
            loai=LoaiDonGia.NUOC,
            ten_muc="Gia nuoc co dinh",
            don_gia=GIA_NUOC,
            ngay_hieu_luc=date(2026, 1, 1),
            dang_ap_dung=True,
        ))
        print(f"Don gia nuoc: {GIA_NUOC:.0f} d/m3")

    db.commit()


def main() -> None:
    if not kiem_tra_ket_noi():
        print("Khong ket noi DB")
        return

    db = SessionLocal()
    try:
        _get_or_create_admin(db)
        _tao_don_gia(db)

        ky = "2026-08"
        ngay = date(2026, 8, 31)

        for i, (ten, so_nguoi, d_cu, d_moi, n_cu, n_moi) in enumerate(DANH_SACH_HO, start=1):
            ten_dn = f"khach{i:02d}"
            user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == ten_dn).first()
            if not user:
                user = NguoiDung(
                    ten_dang_nhap=ten_dn,
                    mat_khau_hash=bam_mat_khau("khach123"),
                    ho_ten=f"Khach {i:02d}",
                    vai_tro=VaiTro.KHACH_THUE,
                    dang_hoat_dong=True,
                )
                db.add(user)
                db.flush()

            phong = db.query(Phong).filter(Phong.ten_phong == ten).first()
            if not phong:
                phong = Phong(
                    ten_phong=ten,
                    so_nguoi_o=so_nguoi,
                    ngay_bat_dau_thue=date(2026, 1, 1),
                    trang_thai="dang_thue",
                    ma_khach_thue=user.ma_nguoi_dung,
                    ghi_chu=f"{so_nguoi} nguoi",
                )
                db.add(phong)
                db.flush()
            else:
                phong.ma_khach_thue = user.ma_nguoi_dung

            ma_dien = f"CT-DIEN-H{phong.ma_phong}"
            ct_dien = db.query(CongTo).filter(CongTo.ma_thiet_bi == ma_dien).first()
            if not ct_dien:
                ct_dien = CongTo(
                    ma_thiet_bi=ma_dien,
                    loai_cong_to=LoaiCongTo.DIEN,
                    ma_phong=phong.ma_phong,
                    dang_hoat_dong=True,
                )
                db.add(ct_dien)
                db.flush()

            ma_nuoc = f"CT-NUOC-H{phong.ma_phong}"
            ct_nuoc = db.query(CongTo).filter(CongTo.ma_thiet_bi == ma_nuoc).first()
            if not ct_nuoc:
                ct_nuoc = CongTo(
                    ma_thiet_bi=ma_nuoc,
                    loai_cong_to=LoaiCongTo.NUOC,
                    ma_phong=phong.ma_phong,
                    dang_hoat_dong=True,
                )
                db.add(ct_nuoc)
                db.flush()

            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_dien.ma_cong_to,
                ChiSo.ngay_ghi == ngay,
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_dien.ma_cong_to,
                    chi_so_cu=float(d_cu),
                    chi_so_moi=float(d_moi),
                    ngay_ghi=ngay,
                    da_chot=True,
                    la_tu_dong=False,
                    la_uoc_tinh=False,
                    ghi_chu="Du lieu mau",
                ))

            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_nuoc.ma_cong_to,
                ChiSo.ngay_ghi == ngay,
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_nuoc.ma_cong_to,
                    chi_so_cu=float(n_cu),
                    chi_so_moi=float(n_moi),
                    ngay_ghi=ngay,
                    da_chot=True,
                    la_tu_dong=False,
                    la_uoc_tinh=False,
                    ghi_chu="Du lieu mau",
                ))

            tieu_thu_dien = d_moi - d_cu
            tieu_thu_nuoc = n_moi - n_cu
            tien_dien = tieu_thu_dien * GIA_DIEN
            tien_nuoc = tieu_thu_nuoc * GIA_NUOC
            tong = tien_dien + tien_nuoc

            hd = db.query(HoaDon).filter(
                HoaDon.ma_phong == phong.ma_phong,
                HoaDon.ky_hoa_don == ky,
            ).first()
            if not hd:
                hd = HoaDon(
                    ma_phong=phong.ma_phong,
                    ky_hoa_don=ky,
                    ngay_lap=ngay,
                    tong_tien_dien=tien_dien,
                    tong_tien_nuoc=tien_nuoc,
                    tong_phu_phi=0,
                    tong_tien=tong,
                    so_tien_da_tra=0,
                    trang_thai="chua_thanh_toan",
                )
                db.add(hd)
                db.flush()

                db.add_all([
                    ChiTietHoaDon(
                        ma_hoa_don=hd.ma_hoa_don,
                        ten_khoan="Tien dien",
                        so_luong=tieu_thu_dien,
                        don_gia=GIA_DIEN,
                        thanh_tien=tien_dien,
                    ),
                    ChiTietHoaDon(
                        ma_hoa_don=hd.ma_hoa_don,
                        ten_khoan="Tien nuoc",
                        so_luong=tieu_thu_nuoc,
                        don_gia=GIA_NUOC,
                        thanh_tien=tien_nuoc,
                    ),
                ])

            print(f"OK: {ten} | {ten_dn}/khach123 | HD {ky} = {tong:,.0f}d")

        db.commit()
        print("\n=== XONG 10 HO (chi dien + nuoc) ===")
        print(f"Don gia: dien {GIA_DIEN:.0f}d/kWh | nuoc {GIA_NUOC:.0f}d/m3")
        print("Admin: admin / admin123")
        print("Khach: khach01 .. khach10 / khach123")
    except Exception as e:
        db.rollback()
        print("LOI:", type(e).__name__, e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()