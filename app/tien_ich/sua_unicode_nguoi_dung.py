# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import text
from app.co_so_du_lieu.ket_noi import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        print("=== Kieu cot hien tai ===")
        rows = db.execute(
            text(
                """
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'nguoi_dung'
                  AND COLUMN_NAME IN ('ho_ten', 'ten_dang_nhap', 'email')
                """
            )
        ).fetchall()
        for r in rows:
            print(r)

        for col, length in [("ho_ten", 100), ("email", 100)]:
            try:
                db.execute(
                    text(
                        f"ALTER TABLE nguoi_dung ALTER COLUMN {col} NVARCHAR({length}) NULL"
                    )
                )
                db.commit()
                print(f"OK: {col} -> NVARCHAR({length})")
            except Exception as e:
                db.rollback()
                # thu NOT NULL cho ho_ten
                try:
                    db.execute(
                        text(
                            f"ALTER TABLE nguoi_dung ALTER COLUMN {col} NVARCHAR({length}) NOT NULL"
                        )
                    )
                    db.commit()
                    print(f"OK: {col} -> NVARCHAR({length}) NOT NULL")
                except Exception as e2:
                    db.rollback()
                    print(f"{col}:", e2)

        # Cap nhat ten khach dang loi (doi theo ma_nguoi_dung neu can)
        print("=== Danh sach user ===")
        rows = db.execute(
            text(
                "SELECT ma_nguoi_dung, ten_dang_nhap, ho_ten FROM nguoi_dung ORDER BY ma_nguoi_dung"
            )
        ).fetchall()
        for r in rows:
            print(r[0], r[1], repr(r[2]))

        # Sua cac ten mau co dau
        sua = {
            "admin": "Nguyễn Văn Quản Lý",
            "khach01": "Nguyễn Văn An",
            "khach02": "Trần Thị Bình",
            "khach03": "Lê Văn Cường",
            "khach04": "Phạm Thị Dung",
            "khach05": "Hoàng Văn Em",
            "khach06": "Vũ Thị Phương",
            "khach07": "Đặng Văn Giang",
            "khach08": "Bùi Thị Hoa",
            "khach09": "Ngô Văn Hùng",
            "khach10": "Đỗ Thị Lan",
        }
        for ten_dn, ho_ten in sua.items():
            db.execute(
                text(
                    "UPDATE nguoi_dung SET ho_ten = :ht WHERE ten_dang_nhap = :tdn"
                ),
                {"ht": ho_ten, "tdn": ten_dn},
            )
        db.commit()
        print("=== Sau khi sua ===")
        rows = db.execute(
            text(
                "SELECT ma_nguoi_dung, ten_dang_nhap, ho_ten FROM nguoi_dung ORDER BY ma_nguoi_dung"
            )
        ).fetchall()
        for r in rows:
            print(r[0], r[1], repr(r[2]))
    finally:
        db.close()


if __name__ == "__main__":
    main()