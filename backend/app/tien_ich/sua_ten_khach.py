# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import text
from app.co_so_du_lieu.ket_noi import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        sua = {
            "khach12": "Nguy\u1ec5n V\u0103n B",
            "khach13": "Nguy\u1ec5n V\u0103n Z",
        }
        for tdn, ht in sua.items():
            db.execute(
                text("UPDATE nguoi_dung SET ho_ten = :ht WHERE ten_dang_nhap = :tdn"),
                {"ht": ht, "tdn": tdn},
            )
            print("User", tdn, "->", ht)

        db.execute(
            text("UPDATE phong SET ten_phong = :t WHERE ma_phong = 32"),
            {"t": "Nguy\u1ec5n V\u0103n Z"},
        )
        print("Phong 32 -> Nguyen Van Z (co dau)")

        db.commit()

        print("=== Kiem tra ===")
        rows = db.execute(
            text(
                "SELECT ma_nguoi_dung, ten_dang_nhap, ho_ten "
                "FROM nguoi_dung WHERE ten_dang_nhap IN ('khach12','khach13')"
            )
        ).fetchall()
        for r in rows:
            print(r[0], r[1], repr(r[2]))
    finally:
        db.close()


if __name__ == "__main__":
    main()