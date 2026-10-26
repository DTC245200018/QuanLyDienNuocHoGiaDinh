"""
Tao tai khoan mau de test dang nhap.
Chay 1 lan: python -m app.tien_ich.tao_du_lieu_mau
"""

from app.co_so_du_lieu.ket_noi import SessionLocal, kiem_tra_ket_noi
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro
from app.tien_ich.bao_mat import bam_mat_khau


def tao_tai_khoan_mau() -> None:
    """Tao 1 quan ly va 1 khach thue neu chua co."""
    if not kiem_tra_ket_noi():
        print("Khong ket noi duoc database.")
        return

    db = SessionLocal()
    try:
        # Tai khoan Quan ly
        quan_ly = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "admin").first()
        if not quan_ly:
            quan_ly = NguoiDung(
                ten_dang_nhap="admin",
                mat_khau_hash=bam_mat_khau("admin123"),
                ho_ten="Nguyen Van Quan Ly",
                so_dien_thoai="0901234567",
                email="admin@example.com",
                vai_tro=VaiTro.QUAN_LY,
                dang_hoat_dong=True,
            )
            db.add(quan_ly)
            print("Da tao tai khoan: admin / admin123 (quan_ly)")
        else:
            print("Tai khoan admin da ton tai.")

        # Tai khoan Khach thue
        khach = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "khach01").first()
        if not khach:
            khach = NguoiDung(
                ten_dang_nhap="khach01",
                mat_khau_hash=bam_mat_khau("khach123"),
                ho_ten="Tran Thi Khach",
                so_dien_thoai="0912345678",
                email="khach01@example.com",
                vai_tro=VaiTro.KHACH_THUE,
                dang_hoat_dong=True,
            )
            db.add(khach)
            print("Da tao tai khoan: khach01 / khach123 (khach_thue)")
        else:
            print("Tai khoan khach01 da ton tai.")

        db.commit()
        print("Hoan tat tao du lieu mau.")
    except Exception as loi:
        db.rollback()
        print(f"Loi: {loi}")
    finally:
        db.close()


if __name__ == "__main__":
    tao_tai_khoan_mau()