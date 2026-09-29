"""Model ChiSo - chi so dien / nuoc theo ky."""

from datetime import date, datetime
from sqlalchemy import Integer, Date, DateTime, Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class ChiSo(Base):
    """Bang chi so cong to."""

    __tablename__ = "chi_so"

    ma_chi_so: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_cong_to: Mapped[int] = mapped_column(ForeignKey("cong_to.ma_cong_to"), nullable=False)
    chi_so_cu: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    chi_so_moi: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    ngay_ghi: Mapped[date] = mapped_column(Date, nullable=False)
    la_tu_dong: Mapped[bool] = mapped_column(Boolean, default=True)  # True = tu IoT, False = nhap tay
    la_uoc_tinh: Mapped[bool] = mapped_column(Boolean, default=False)
    da_chot: Mapped[bool] = mapped_column(Boolean, default=False)
    ghi_chu: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<ChiSo(ma={self.ma_chi_so}, cu={self.chi_so_cu}, moi={self.chi_so_moi})>"