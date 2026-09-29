"""
File khoi chay ung dung FastAPI.
He thong quan ly hoa don dien nuoc ho gia dinh co tich hop AI.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.giao_dien.dang_nhap import router as dang_nhap_router
from app.giao_dien.quan_ly_phong import router as phong_router
from app.giao_dien.quan_ly_cong_to import router as cong_to_router
from app.giao_dien.cau_hinh_don_gia import router as don_gia_router
from app.giao_dien.quan_ly_phu_phi import router as phu_phi_router
from app.giao_dien.quan_ly_chi_so import router as chi_so_router
from app.giao_dien.quan_ly_hoa_don import router as hoa_don_router
from app.giao_dien.quan_ly_thanh_toan import router as thanh_toan_router
from app.giao_dien.ai_canh_bao import router as ai_router
from app.giao_dien.trang_web import router as web_router

app = FastAPI(
    title="Quan Ly Hoa Don Dien Nuoc Ho Gia Dinh",
    description="He thong quan ly hoa don dien nuoc co tich hop AI",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(web_router)
app.include_router(dang_nhap_router)
app.include_router(phong_router)
app.include_router(cong_to_router)
app.include_router(don_gia_router)
app.include_router(phu_phi_router)
app.include_router(chi_so_router)
app.include_router(hoa_don_router)
app.include_router(thanh_toan_router)
app.include_router(ai_router)