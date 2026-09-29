"""Model PhuPhi - cac khoan phu phi dich vu."""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class PhuPhi(Base):
    """Bang danh muc phu phi (rac, wifi, ve sinh...)."""

    __tablename__ = "phu_phi"

    ma_phu_phi: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ten_phu_phi: Mapped[str] = mapped_column(String(100), nullable=False)
    so_tien: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    dang_ap_dung: Mapped[bool] = mapped_column(Boolean, default=True)
    mo_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<PhuPhi(ma={self.ma_phu_phi}, ten={self.ten_phu_phi})>"