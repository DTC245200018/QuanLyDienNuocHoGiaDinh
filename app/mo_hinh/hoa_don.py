"""Model HoaDon - hoa don hang thang."""

from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class HoaDon(Base):
    """Bang hoa don."""

    __tablename__ = "hoa_don"

    ma_hoa_don: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_phong: Mapped[int] = mapped_column(ForeignKey("phong.ma_phong"), nullable=False)
    ky_hoa_don: Mapped[str] = mapped_column(String(7), nullable=False)  # vi du: 2026-08
    ngay_lap: Mapped[date] = mapped_column(Date, nullable=False)
    tong_tien_dien: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tong_tien_nuoc: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tong_phu_phi: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tong_tien: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    so_tien_da_tra: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    trang_thai: Mapped[str] = mapped_column(String(30), default="chua_thanh_toan")
    # chua_thanh_toan / thanh_toan_mot_phan / da_thanh_toan / ban_nhap
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<HoaDon(ma={self.ma_hoa_don}, phong={self.ma_phong}, ky={self.ky_hoa_don})>"