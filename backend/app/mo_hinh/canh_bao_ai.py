"""Model CanhBaoAI - ket qua phan tich va canh bao cua AI."""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.ket_noi import Base


class CanhBaoAI(Base):
    """Bang luu ket qua phan tich AI."""

    __tablename__ = "canh_bao_ai"

    ma_canh_bao: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_phong: Mapped[int] = mapped_column(ForeignKey("phong.ma_phong"), nullable=False)
    ma_hoa_don: Mapped[int | None] = mapped_column(ForeignKey("hoa_don.ma_hoa_don"), nullable=True)
    loai_canh_bao: Mapped[str] = mapped_column(String(50), nullable=False)
    noi_dung: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    muc_do: Mapped[str] = mapped_column(String(20), default="trung_binh")
    da_xu_ly: Mapped[bool] = mapped_column(Boolean, default=False)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<CanhBaoAI(ma={self.ma_canh_bao}, phong={self.ma_phong})>"