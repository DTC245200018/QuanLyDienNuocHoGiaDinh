# -*- coding: utf-8 -*-
"""Doi ten_phong sang NVARCHAR va ghi lai ten co dau."""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import text
from app.co_so_du_lieu.ket_noi import SessionLocal


TEN_HO = [
    "Hộ Nguyễn Văn An",
    "Hộ Trần Thị Bình",
    "Hộ Lê Văn Cường",
    "Hộ Phạm Thị Dung",
    "Hộ Hoàng Văn Em",
    "Hộ Vũ Thị Phương",
    "Hộ Đặng Văn Giang",
    "Hộ Bùi Thị Hoa",
    "Hộ Ngô Văn Hùng",
    "Hộ Đỗ Thị Lan",
]


def main() -> None:
    db = SessionLocal()
    try:
        # 1) Tim ten constraint unique tren ten_phong
        print("=== Tim constraint ===")
        rows = db.execute(
            text(
                """
                SELECT kc.name
                FROM sys.key_constraints kc
                INNER JOIN sys.index_columns ic
                    ON kc.parent_object_id = ic.object_id
                   AND kc.unique_index_id = ic.index_id
                INNER JOIN sys.columns c
                    ON ic.object_id = c.object_id
                   AND ic.column_id = c.column_id
                WHERE kc.parent_object_id = OBJECT_ID('phong')
                  AND c.name = 'ten_phong'
                  AND kc.type = 'UQ'
                """
            )
        ).fetchall()
        for r in rows:
            ten_uq = r[0]
            print("Drop:", ten_uq)
            db.execute(text(f"ALTER TABLE phong DROP CONSTRAINT [{ten_uq}]"))
        db.commit()

        # 2) Doi kieu cot
        db.execute(text("ALTER TABLE phong ALTER COLUMN ten_phong NVARCHAR(100) NOT NULL"))
        db.commit()
        print("OK: ten_phong -> NVARCHAR(100)")

        try:
            db.execute(text("ALTER TABLE phong ALTER COLUMN ghi_chu NVARCHAR(255) NULL"))
            db.commit()
            print("OK: ghi_chu -> NVARCHAR(255)")
        except Exception as e:
            db.rollback()
            print("ghi_chu:", e)

        # 3) Tao lai unique
        db.execute(
            text(
                "ALTER TABLE phong ADD CONSTRAINT UQ_phong_ten_phong UNIQUE (ten_phong)"
            )
        )
        db.commit()
        print("OK: unique ten_phong")

        # 4) Cap nhat ten
        rows = db.execute(
            text("SELECT ma_phong FROM phong ORDER BY ma_phong")
        ).fetchall()
        for idx, row in enumerate(rows):
            if idx >= len(TEN_HO):
                break
            db.execute(
                text("UPDATE phong SET ten_phong = :ten WHERE ma_phong = :ma"),
                {"ten": TEN_HO[idx], "ma": row[0]},
            )
            print("UPDATE", row[0], "->", TEN_HO[idx])
        db.commit()

        # 5) Kiem tra
        print("=== Kiem tra DATA_TYPE ===")
        rows = db.execute(
            text(
                """
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'phong' AND COLUMN_NAME = 'ten_phong'
                """
            )
        ).fetchall()
        for r in rows:
            print(r)

        print("=== Ten sau sua (repr) ===")
        rows = db.execute(
            text("SELECT ma_phong, ten_phong FROM phong ORDER BY ma_phong")
        ).fetchall()
        for r in rows:
            print(r[0], repr(r[1]))
    except Exception as e:
        db.rollback()
        print("LOI:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()