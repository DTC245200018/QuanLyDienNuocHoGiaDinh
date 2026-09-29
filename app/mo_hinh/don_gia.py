"""Model DonGia - don gia dien / nuoc."""

from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Boolean, Numeric, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.co_so_du_lieu.ket_noi import Base


class LoaiDonGia(str, enum.Enum):
    DIEN = "dien"
    NUOC = "nuoc"


class DonGia(Base):
    """Bang don gia dien / nuoc (co the bac thang)."""

    __tablename__ = "don_gia"

    ma_don_gia: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    loai: Mapped[LoaiDonGia] = mapped_column(Enum(LoaiDonGia), nullable=False)
    ten_muc: Mapped[str] = mapped_column(String(50), nullable=False)  # vi du: Bac 1, Gia co dinh
    tu_so: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)  # bac thang
    den_so: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    don_gia: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    ngay_hieu_luc: Mapped[date] = mapped_column(Date, nullable=False)
    dang_ap_dung: Mapped[bool] = mapped_column(Boolean, default=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<DonGia(ma={self.ma_don_gia}, loai={self.loai}, gia={self.don_gia})>"