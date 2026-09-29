"""Xoa du lieu nghiep vu, giu lai tai khoan admin."""

from sqlalchemy import text
from app.co_so_du_lieu.ket_noi import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        tables = [
            "canh_bao_ai",
            "thanh_toan",
            "chi_tiet_hoa_don",
            "hoa_don",
            "chi_so",
            "cong_to",
            "phong",
            "phu_phi",
            "don_gia",
        ]
        for t in tables:
            try:
                db.execute(text(f"DELETE FROM {t}"))
                print("Xoa:", t)
            except Exception as e:
                print("Bo qua", t, ":", e)

        # Giu admin, xoa user khac
        db.execute(
            text("DELETE FROM nguoi_dung WHERE ten_dang_nhap != :admin"),
            {"admin": "admin"},
        )
        print("Xoa user (giu admin)")

        db.commit()
        print("=== DA XOA SACH DU LIEU NGHIEP VU ===")
    except Exception as e:
        db.rollback()
        print("LOI:", e)
    finally:
        db.close()


if __name__ == "__main__":
    main()