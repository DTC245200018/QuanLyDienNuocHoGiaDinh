"""Model ChiTietHoaDon - chi tiet tung khoan trong hoa don."""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class ChiTietHoaDon(Base):
    """Bang chi tiet hoa don."""

    __tablename__ = "chi_tiet_hoa_don"

    ma_chi_tiet: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_hoa_don: Mapped[int] = mapped_column(ForeignKey("hoa_don.ma_hoa_don"), nullable=False)
    ten_khoan: Mapped[str] = mapped_column(String(100), nullable=False)  # Tien dien, Tien nuoc, Rac...
    so_luong: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    don_gia: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    thanh_tien: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<ChiTietHoaDon(ma={self.ma_chi_tiet}, khoan={self.ten_khoan})>"