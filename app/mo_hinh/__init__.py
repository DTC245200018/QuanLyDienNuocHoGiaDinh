"""Import tat ca model de SQLAlchemy nhan dien."""

from app.mo_hinh.nguoi_dung import NguoiDung
from app.mo_hinh.phong import Phong
from app.mo_hinh.cong_to import CongTo
from app.mo_hinh.chi_so import ChiSo
from app.mo_hinh.don_gia import DonGia
from app.mo_hinh.phu_phi import PhuPhi
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.chi_tiet_hoa_don import ChiTietHoaDon
from app.mo_hinh.thanh_toan import ThanhToan
from app.mo_hinh.canh_bao_ai import CanhBaoAI

__all__ = [
    "NguoiDung",
    "Phong",
    "CongTo",
    "ChiSo",
    "DonGia",
    "PhuPhi",
    "HoaDon",
    "ChiTietHoaDon",
    "ThanhToan",
    "CanhBaoAI",
]