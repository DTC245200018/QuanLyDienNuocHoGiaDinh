"""Model CongTo - cong to dien / nuoc."""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.co_so_du_lieu.ket_noi import Base


class LoaiCongTo(str, enum.Enum):
    """Loai cong to."""
    DIEN = "dien"
    NUOC = "nuoc"


class CongTo(Base):
    """Bang cong to dien hoac nuoc."""

    __tablename__ = "cong_to"

    ma_cong_to: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_thiet_bi: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # ma vat ly / MAC
    loai_cong_to: Mapped[LoaiCongTo] = mapped_column(Enum(LoaiCongTo), nullable=False)
    ma_phong: Mapped[int | None] = mapped_column(ForeignKey("phong.ma_phong"), nullable=True)
    dang_hoat_dong: Mapped[bool] = mapped_column(Boolean, default=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<CongTo(ma={self.ma_cong_to}, thiet_bi={self.ma_thiet_bi})>"