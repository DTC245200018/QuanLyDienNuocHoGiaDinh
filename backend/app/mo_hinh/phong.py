"""Model Phong - thong tin phong / ho gia dinh."""

from datetime import date, datetime
from sqlalchemy import Integer, Date, DateTime, ForeignKey, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class Phong(Base):
    """Bang phong tro / ho gia dinh."""

    __tablename__ = "phong"

    ma_phong: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ten_phong: Mapped[str] = mapped_column(Unicode(100), unique=True, nullable=False)
    so_nguoi_o: Mapped[int] = mapped_column(Integer, default=1)
    ngay_bat_dau_thue: Mapped[date | None] = mapped_column(Date, nullable=True)
    trang_thai: Mapped[str] = mapped_column(Unicode(20), default="dang_thue")
    ma_khach_thue: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=True
    )
    ghi_chu: Mapped[str | None] = mapped_column(Unicode(255), nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Phong(ma={self.ma_phong}, ten={self.ten_phong})>"