"""
Script tao tat ca bang trong database QuanLyDienNuoc.
Chi chay 1 lan khi thiet lap ban dau.
"""

from app.co_so_du_lieu.ket_noi import Base, engine, kiem_tra_ket_noi
import app.mo_hinh  # noqa: F401  # import de dang ky model


def tao_tat_ca_bang() -> None:
    """Tao toan bo bang neu chua ton tai."""
    if not kiem_tra_ket_noi():
        print("Khong ket noi duoc database. Kiem tra lai .env va SQL Server.")
        return

    print("Dang tao bang...")
    Base.metadata.create_all(bind=engine)
    print("Tao bang thanh cong!")


if __name__ == "__main__":
    tao_tat_ca_bang()