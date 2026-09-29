"""Model ThanhToan - ghi nhan thanh toan hoa don."""

from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class ThanhToan(Base):
    """Bang thanh toan."""

    __tablename__ = "thanh_toan"

    ma_thanh_toan: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_hoa_don: Mapped[int] = mapped_column(ForeignKey("hoa_don.ma_hoa_don"), nullable=False)
    so_tien: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    ngay_thanh_toan: Mapped[date] = mapped_column(Date, nullable=False)
    hinh_thuc: Mapped[str] = mapped_column(String(30), default="tien_mat")  # tien_mat / chuyen_khoan
    ghi_chu: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<ThanhToan(ma={self.ma_thanh_toan}, tien={self.so_tien})>"