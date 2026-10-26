"""
Tao du lieu demo de bao ve:
- 3 ho gia dinh
- Cong to dien/nuoc
- Chi so 2 ky
- Don gia, phu phi
- Hoa don
Chay: python -m app.tien_ich.tao_du_lieu_demo
"""

from datetime import date

from app.co_so_du_lieu.ket_noi import SessionLocal, kiem_tra_ket_noi
from app.mo_hinh.phong import Phong
from app.mo_hinh.cong_to import CongTo, LoaiCongTo
from app.mo_hinh.chi_so import ChiSo
from app.mo_hinh.don_gia import DonGia, LoaiDonGia
from app.mo_hinh.phu_phi import PhuPhi
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.chi_tiet_hoa_don import ChiTietHoaDon
from app.tien_ich.bao_mat import bam_mat_khau
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro


def _get_or_create_admin(db):
    admin = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "admin").first()
    if not admin:
        admin = NguoiDung(
            ten_dang_nhap="admin",
            mat_khau_hash=bam_mat_khau("admin123"),
            ho_ten="Nguyen Van Quan Ly",
            vai_tro=VaiTro.QUAN_LY,
            dang_hoat_dong=True,
        )
        db.add(admin)
        db.commit()
    return admin


def tao_demo():
    if not kiem_tra_ket_noi():
        print("Khong ket noi duoc database.")
        return

    db = SessionLocal()
    try:
        _get_or_create_admin(db)

        # Don gia
        if not db.query(DonGia).filter(DonGia.loai == LoaiDonGia.DIEN).first():
            db.add(DonGia(
                loai=LoaiDonGia.DIEN,
                ten_muc="Gia dien co dinh",
                don_gia=3500,
                ngay_hieu_luc=date(2026, 1, 1),
                dang_ap_dung=True,
            ))
        if not db.query(DonGia).filter(DonGia.loai == LoaiDonGia.NUOC).first():
            db.add(DonGia(
                loai=LoaiDonGia.NUOC,
                ten_muc="Gia nuoc co dinh",
                don_gia=15000,
                ngay_hieu_luc=date(2026, 1, 1),
                dang_ap_dung=True,
            ))

        # Phu phi
        if not db.query(PhuPhi).filter(PhuPhi.ten_phu_phi == "Tien rac").first():
            db.add(PhuPhi(ten_phu_phi="Tien rac", so_tien=30000, dang_ap_dung=True))
        if not db.query(PhuPhi).filter(PhuPhi.ten_phu_phi == "Wifi").first():
            db.add(PhuPhi(ten_phu_phi="Wifi", so_tien=50000, dang_ap_dung=True))

        db.commit()

        # 3 ho gia dinh
        ds_ho = [
            ("Ho Nguyen Van A", 4, "Ho gia dinh 4 nguoi"),
            ("Ho Tran Thi B", 2, "Ho gia dinh 2 nguoi"),
            ("Ho Le Van C", 3, "Ho gia dinh 3 nguoi"),
        ]
        phong_list = []
        for ten, so_nguoi, ghi_chu in ds_ho:
            p = db.query(Phong).filter(Phong.ten_phong == ten).first()
            if not p:
                p = Phong(
                    ten_phong=ten,
                    so_nguoi_o=so_nguoi,
                    trang_thai="dang_thue",
                    ngay_bat_dau_thue=date(2026, 1, 1),
                    ghi_chu=ghi_chu,
                )
                db.add(p)
                db.flush()
            phong_list.append(p)
        db.commit()

        # Cong to + chi so + hoa don mau
        for i, p in enumerate(phong_list):
            # Cong to dien
            ma_dien = f"CT-DIEN-H{p.ma_phong}"
            ct_dien = db.query(CongTo).filter(CongTo.ma_thiet_bi == ma_dien).first()
            if not ct_dien:
                ct_dien = CongTo(
                    ma_thiet_bi=ma_dien,
                    loai_cong_to=LoaiCongTo.DIEN,
                    ma_phong=p.ma_phong,
                    dang_hoat_dong=True,
                )
                db.add(ct_dien)
                db.flush()

            # Cong to nuoc
            ma_nuoc = f"CT-NUOC-H{p.ma_phong}"
            ct_nuoc = db.query(CongTo).filter(CongTo.ma_thiet_bi == ma_nuoc).first()
            if not ct_nuoc:
                ct_nuoc = CongTo(
                    ma_thiet_bi=ma_nuoc,
                    loai_cong_to=LoaiCongTo.NUOC,
                    ma_phong=p.ma_phong,
                    dang_hoat_dong=True,
                )
                db.add(ct_nuoc)
                db.flush()

            # Chi so ky 1 (thang 7)
            cu_dien, moi_dien = 1000 + i * 100, 1100 + i * 100
            cu_nuoc, moi_nuoc = 50 + i * 5, 55 + i * 5

            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_dien.ma_cong_to,
                ChiSo.ngay_ghi == date(2026, 7, 31),
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_dien.ma_cong_to,
                    chi_so_cu=cu_dien,
                    chi_so_moi=moi_dien,
                    ngay_ghi=date(2026, 7, 31),
                    la_tu_dong=False,
                    da_chot=True,
                ))
            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_nuoc.ma_cong_to,
                ChiSo.ngay_ghi == date(2026, 7, 31),
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_nuoc.ma_cong_to,
                    chi_so_cu=cu_nuoc,
                    chi_so_moi=moi_nuoc,
                    ngay_ghi=date(2026, 7, 31),
                    la_tu_dong=False,
                    da_chot=True,
                ))

            # Chi so ky 2 (thang 8) - ho A tang manh de demo AI canh bao
            if i == 0:
                moi_dien_2 = moi_dien + 180  # tang manh
                moi_nuoc_2 = moi_nuoc + 12
            else:
                moi_dien_2 = moi_dien + 90
                moi_nuoc_2 = moi_nuoc + 4

            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_dien.ma_cong_to,
                ChiSo.ngay_ghi == date(2026, 8, 31),
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_dien.ma_cong_to,
                    chi_so_cu=moi_dien,
                    chi_so_moi=moi_dien_2,
                    ngay_ghi=date(2026, 8, 31),
                    la_tu_dong=False,
                    da_chot=True,
                ))
            if not db.query(ChiSo).filter(
                ChiSo.ma_cong_to == ct_nuoc.ma_cong_to,
                ChiSo.ngay_ghi == date(2026, 8, 31),
            ).first():
                db.add(ChiSo(
                    ma_cong_to=ct_nuoc.ma_cong_to,
                    chi_so_cu=moi_nuoc,
                    chi_so_moi=moi_nuoc_2,
                    ngay_ghi=date(2026, 8, 31),
                    la_tu_dong=False,
                    da_chot=True,
                ))

            db.commit()

            # Hoa don thang 7
            tieu_thu_dien = moi_dien - cu_dien
            tieu_thu_nuoc = moi_nuoc - cu_nuoc
            tien_dien = tieu_thu_dien * 3500
            tien_nuoc = tieu_thu_nuoc * 15000
            phu_phi = 80000
            tong = tien_dien + tien_nuoc + phu_phi

            hd7 = db.query(HoaDon).filter(
                HoaDon.ma_phong == p.ma_phong,
                HoaDon.ky_hoa_don == "2026-07",
            ).first()
            if not hd7:
                hd7 = HoaDon(
                    ma_phong=p.ma_phong,
                    ky_hoa_don="2026-07",
                    ngay_lap=date(2026, 7, 31),
                    tong_tien_dien=tien_dien,
                    tong_tien_nuoc=tien_nuoc,
                    tong_phu_phi=phu_phi,
                    tong_tien=tong,
                    so_tien_da_tra=tong,
                    trang_thai="da_thanh_toan",
                )
                db.add(hd7)
                db.flush()
                db.add_all([
                    ChiTietHoaDon(ma_hoa_don=hd7.ma_hoa_don, ten_khoan="Tien dien", so_luong=tieu_thu_dien, don_gia=3500, thanh_tien=tien_dien),
                    ChiTietHoaDon(ma_hoa_don=hd7.ma_hoa_don, ten_khoan="Tien nuoc", so_luong=tieu_thu_nuoc, don_gia=15000, thanh_tien=tien_nuoc),
                    ChiTietHoaDon(ma_hoa_don=hd7.ma_hoa_don, ten_khoan="Tien rac", so_luong=1, don_gia=30000, thanh_tien=30000),
                    ChiTietHoaDon(ma_hoa_don=hd7.ma_hoa_don, ten_khoan="Wifi", so_luong=1, don_gia=50000, thanh_tien=50000),
                ])

            # Hoa don thang 8
            tieu_thu_dien2 = moi_dien_2 - moi_dien
            tieu_thu_nuoc2 = moi_nuoc_2 - moi_nuoc
            tien_dien2 = tieu_thu_dien2 * 3500
            tien_nuoc2 = tieu_thu_nuoc2 * 15000
            tong2 = tien_dien2 + tien_nuoc2 + phu_phi

            hd8 = db.query(HoaDon).filter(
                HoaDon.ma_phong == p.ma_phong,
                HoaDon.ky_hoa_don == "2026-08",
            ).first()
            if not hd8:
                hd8 = HoaDon(
                    ma_phong=p.ma_phong,
                    ky_hoa_don="2026-08",
                    ngay_lap=date(2026, 8, 31),
                    tong_tien_dien=tien_dien2,
                    tong_tien_nuoc=tien_nuoc2,
                    tong_phu_phi=phu_phi,
                    tong_tien=tong2,
                    so_tien_da_tra=0,
                    trang_thai="chua_thanh_toan",
                )
                db.add(hd8)
                db.flush()
                db.add_all([
                    ChiTietHoaDon(ma_hoa_don=hd8.ma_hoa_don, ten_khoan="Tien dien", so_luong=tieu_thu_dien2, don_gia=3500, thanh_tien=tien_dien2),
                    ChiTietHoaDon(ma_hoa_don=hd8.ma_hoa_don, ten_khoan="Tien nuoc", so_luong=tieu_thu_nuoc2, don_gia=15000, thanh_tien=tien_nuoc2),
                    ChiTietHoaDon(ma_hoa_don=hd8.ma_hoa_don, ten_khoan="Tien rac", so_luong=1, don_gia=30000, thanh_tien=30000),
                    ChiTietHoaDon(ma_hoa_don=hd8.ma_hoa_don, ten_khoan="Wifi", so_luong=1, don_gia=50000, thanh_tien=50000),
                ])

            db.commit()
            print(f"OK: {p.ten_phong} (ma_phong={p.ma_phong})")

        print("\nHoan tat tao du lieu demo.")
        print("Tai khoan: admin / admin123")
        print("Ho Nguyen Van A (ma=?) co tieu thu tang manh thang 8 de demo AI canh bao.")
    except Exception as e:
        db.rollback()
        print("Loi:", e)
    finally:
        db.close()


if __name__ == "__main__":
    tao_demo()