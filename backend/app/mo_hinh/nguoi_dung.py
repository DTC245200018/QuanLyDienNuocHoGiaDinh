"""Model NguoiDung - tai khoan va phan quyen."""

from datetime import datetime
from sqlalchemy import Unicode, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.co_so_du_lieu.ket_noi import Base


class VaiTro(str, enum.Enum):
    """Vai tro nguoi dung trong he thong."""

    QUAN_LY = "quan_ly"
    KHACH_THUE = "khach_thue"


class NguoiDung(Base):
    """Bang nguoi dung (quan ly / khach thue)."""

    __tablename__ = "nguoi_dung"

    ma_nguoi_dung: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ten_dang_nhap: Mapped[str] = mapped_column(Unicode(50), unique=True, nullable=False)
    mat_khau_hash: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    ho_ten: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    so_dien_thoai: Mapped[str | None] = mapped_column(Unicode(15), nullable=True)
    email: Mapped[str | None] = mapped_column(Unicode(100), nullable=True)
    vai_tro: Mapped[VaiTro] = mapped_column(Enum(VaiTro), nullable=False)
    dang_hoat_dong: Mapped[bool] = mapped_column(Boolean, default=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<NguoiDung(ma={self.ma_nguoi_dung}, ten={self.ten_dang_nhap})>"