"""
Cac trang web HTML day du.
Session cookie don gian de giu dang nhap.
Chatbot AI: lich su chat chi trong phien.
"""
import uuid
from pathlib import Path
from datetime import date
from urllib.parse import quote
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.luan_ly.xac_thuc import lay_db, xac_thuc_nguoi_dung
from app.luan_ly.xu_ly_phong import (
    lay_danh_sach_phong,
    tao_phong,
    lay_phong_theo_ma,
    xoa_phong,
)
from app.luan_ly.xu_ly_hoa_don import lay_danh_sach_hoa_don, lap_hoa_don
from app.luan_ly.xu_ly_chi_so import lay_danh_sach_chi_so, tao_chi_so
from app.luan_ly.xu_ly_cong_to import lay_danh_sach_cong_to
from app.luan_ly.xu_ly_thanh_toan import ghi_nhan_thanh_toan, lay_danh_sach_thanh_toan
from app.luan_ly.xu_ly_don_gia import lay_danh_sach_don_gia, tao_don_gia
from app.luan_ly.phan_tich_ai import chat_ai
from app.mo_hinh.canh_bao_ai import CanhBaoAI
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.nguoi_dung import NguoiDung, VaiTro
from app.mo_hinh.phong import Phong
from app.mo_hinh.don_gia import LoaiDonGia

router = APIRouter(tags=["Trang web"])

# backend/app/giao_dien/trang_web.py -> 4 cap parent = thu muc project
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend"
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

# session_id cookie -> ma_nguoi_dung
_sessions: dict[str, int] = {}
# session_id -> list[{"role": "user"|"bot", "text": str}]
_chat_logs: dict[str, list] = {}


def _lay_user(request: Request, db: Session) -> NguoiDung | None:
    token = request.cookies.get("session_id")
    if not token or token not in _sessions:
        return None
    return db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == _sessions[token]).first()


def _require_user(request: Request, db: Session) -> NguoiDung | None:
    return _lay_user(request, db)


def _la_khach(user: NguoiDung) -> bool:
    if user.vai_tro == VaiTro.KHACH_THUE:
        return True
    if str(user.vai_tro).lower() in ("khach_thue", "vaitro.khach_thue"):
        return True
    return getattr(user.vai_tro, "value", "") == "khach_thue"


def _loc_phong(danh_sach: list, q: str) -> list:
    q = (q or "").strip()
    if not q:
        return danh_sach
    ket_qua = []
    for p in danh_sach:
        if q.isdigit():
            if p.ma_phong == int(q):
                ket_qua.append(p)
        elif q.lower() in (p.ten_phong or "").lower():
            ket_qua.append(p)
    return ket_qua


def _chat_key(request: Request) -> str:
    return request.cookies.get("session_id") or ""


def _lay_chat_log(request: Request) -> list:
    key = _chat_key(request)
    if not key:
        return []
    return _chat_logs.setdefault(key, [])


def _them_chat(request: Request, role: str, text: str) -> None:
    log = _lay_chat_log(request)
    log.append({"role": role, "text": text})
    if len(log) > 40:
        del log[:-40]


# ========== AUTH ==========
@router.get("/", response_class=HTMLResponse)
def trang_goc(request: Request, db: Session = Depends(lay_db)):
    user = _lay_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/dang-nhap", response_class=HTMLResponse)
def form_dang_nhap(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/dang_nhap.html",
        context={"user": None, "error": None},
    )


@router.post("/dang-nhap", response_class=HTMLResponse)
def xu_ly_dang_nhap(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(lay_db),
):
    user = xac_thuc_nguoi_dung(db, username, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/dang_nhap.html",
            context={"user": None, "error": "Tên đăng nhập hoặc mật khẩu không đúng"},
            status_code=400,
        )
    sid = str(uuid.uuid4())
    _sessions[sid] = user.ma_nguoi_dung
    _chat_logs[sid] = []
    dest = "/khach" if _la_khach(user) else "/dashboard"
    resp = RedirectResponse(dest, status_code=302)
    resp.set_cookie("session_id", sid, httponly=True)
    return resp


@router.get("/dang-xuat")
def dang_xuat(request: Request):
    token = request.cookies.get("session_id")
    if token and token in _sessions:
        del _sessions[token]
    if token and token in _chat_logs:
        del _chat_logs[token]
    resp = RedirectResponse("/dang-nhap", status_code=302)
    resp.delete_cookie("session_id")
    return resp


# ========== DASHBOARD ==========
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    ds_hd = (
        db.query(HoaDon)
        .order_by(HoaDon.ma_phong.asc(), HoaDon.ma_hoa_don.asc())
        .all()
    )
    so_chua_tt = sum(1 for h in ds_hd if h.trang_thai != "da_thanh_toan")
    tong_cong_no = sum(
        float(h.tong_tien) - float(h.so_tien_da_tra)
        for h in ds_hd
        if h.trang_thai != "da_thanh_toan"
    )
    hd_no = [h for h in ds_hd if h.trang_thai != "da_thanh_toan"][:8]
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/dashboard.html",
        context={
            "user": user,
            "so_phong": db.query(Phong).count(),
            "so_hoa_don": db.query(HoaDon).count(),
            "so_canh_bao": db.query(CanhBaoAI).count(),
            "so_chua_tt": so_chua_tt,
            "tong_cong_no": tong_cong_no,
            "hd_no": hd_no,
        },
    )


# ========== HO GIA DINH ==========
@router.get("/phong", response_class=HTMLResponse)
def trang_phong(
    request: Request,
    q: str | None = None,
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    q = (q or "").strip()
    danh_sach = _loc_phong(lay_danh_sach_phong(db), q)
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/phong.html",
        context={
            "user": user,
            "danh_sach": danh_sach,
            "q": q,
            "thong_bao": None,
            "loi": None,
        },
    )


@router.post("/phong/them", response_class=HTMLResponse)
def them_phong(
    request: Request,
    ten_phong: str = Form(...),
    so_nguoi_o: int = Form(1),
    ghi_chu: str = Form(""),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    loi = thong_bao = None
    try:
        phong, khach, mk = tao_phong(
            db,
            ten_phong=ten_phong.strip(),
            so_nguoi_o=so_nguoi_o,
            ghi_chu=ghi_chu or None,
            tao_cong_to=True,
            tao_tai_khoan=True,
        )
        if khach and mk:
            thong_bao = (
                f"Đã thêm hộ '{phong.ten_phong}' (mã {phong.ma_phong}). "
                f"Đã tạo công tơ điện/nước. "
                f"Tài khoản khách: {khach.ten_dang_nhap} / {mk}"
            )
        else:
            thong_bao = f"Đã thêm hộ '{phong.ten_phong}'."
    except ValueError as e:
        loi = str(e)
    except Exception as e:
        loi = f"Lỗi: {e}"
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/phong.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_phong(db),
            "q": None,
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


@router.post("/phong/xoa/{ma_phong}", response_class=HTMLResponse)
def xoa_phong_web(ma_phong: int, request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    loi = thong_bao = None
    phong = lay_phong_theo_ma(db, ma_phong)
    if not phong:
        loi = "Không tìm thấy hộ gia đình"
    else:
        try:
            ten = phong.ten_phong
            xoa_phong(db, phong)
            thong_bao = f"Đã xóa hộ '{ten}'"
        except ValueError as e:
            loi = str(e)
        except Exception as e:
            loi = f"Lỗi: {e}"
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/phong.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_phong(db),
            "q": None,
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


# ========== CHI SO ==========
@router.get("/chi-so", response_class=HTMLResponse)
def trang_chi_so(
    request: Request,
    q: str | None = None,
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    phong_list = lay_danh_sach_phong(db)
    q = (q or "").strip()
    phong_loc = _loc_phong(phong_list, q) if q else []
    if q:
        ma_set = {p.ma_phong for p in phong_loc}
        cong_to_list = [c for c in lay_danh_sach_cong_to(db) if c.ma_phong in ma_set]
        ct_ids = {c.ma_cong_to for c in cong_to_list}
        danh_sach = [cs for cs in lay_danh_sach_chi_so(db) if cs.ma_cong_to in ct_ids]
    else:
        cong_to_list = lay_danh_sach_cong_to(db)
        danh_sach = lay_danh_sach_chi_so(db)
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/chi_so.html",
        context={
            "user": user,
            "danh_sach": danh_sach,
            "cong_to_list": cong_to_list,
            "phong_list": phong_list,
            "q": q,
            "phong_loc": phong_loc,
            "thong_bao": None,
            "loi": None,
        },
    )


@router.post("/chi-so/them", response_class=HTMLResponse)
def them_chi_so(
    request: Request,
    ma_cong_to: int = Form(...),
    chi_so_cu: float = Form(...),
    chi_so_moi: float = Form(...),
    ngay_ghi: str = Form(...),
    ghi_chu: str = Form(""),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    loi = thong_bao = None
    try:
        tao_chi_so(
            db,
            ma_cong_to=ma_cong_to,
            chi_so_cu=chi_so_cu,
            chi_so_moi=chi_so_moi,
            ngay_ghi=date.fromisoformat(ngay_ghi),
            ghi_chu=ghi_chu or None,
        )
        thong_bao = "Đã lưu chỉ số thành công"
    except ValueError as e:
        loi = str(e)
    except Exception as e:
        loi = f"Lỗi: {e}"
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/chi_so.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_chi_so(db),
            "cong_to_list": lay_danh_sach_cong_to(db),
            "phong_list": lay_danh_sach_phong(db),
            "q": None,
            "phong_loc": [],
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


# ========== HOA DON ==========
@router.get("/hoa-don", response_class=HTMLResponse)
def trang_hoa_don(
    request: Request,
    q: str | None = None,
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    q = (q or "").strip()
    danh_sach = lay_danh_sach_hoa_don(db)
    if q:
        loc = []
        for h in danh_sach:
            if q.isdigit():
                if h.ma_hoa_don == int(q) or h.ma_phong == int(q):
                    loc.append(h)
            else:
                if q.lower() in (h.ky_hoa_don or "").lower():
                    loc.append(h)
                elif q.lower() in (h.trang_thai or "").lower():
                    loc.append(h)
        danh_sach = loc
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/hoa_don.html",
        context={
            "user": user,
            "danh_sach": danh_sach,
            "phong_list": lay_danh_sach_phong(db),
            "q": q,
            "thong_bao": None,
            "loi": None,
        },
    )


@router.post("/hoa-don/lap", response_class=HTMLResponse)
def web_lap_hoa_don(
    request: Request,
    ma_phong: int = Form(...),
    ky_hoa_don: str = Form(...),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    loi = thong_bao = None
    try:
        hd = lap_hoa_don(db, ma_phong=ma_phong, ky_hoa_don=ky_hoa_don)
        thong_bao = f"Đã lập hóa đơn #{hd.ma_hoa_don} - Tổng: {hd.tong_tien:,.0f} VND"
    except ValueError as e:
        loi = str(e)
    except Exception as e:
        loi = f"Lỗi: {e}"
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/hoa_don.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_hoa_don(db),
            "phong_list": lay_danh_sach_phong(db),
            "q": None,
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


# ========== THANH TOAN ==========
@router.get("/thanh-toan", response_class=HTMLResponse)
def trang_thanh_toan(
    request: Request,
    q: str | None = None,
    ok: int | None = None,
    hd: int | None = None,
    loi: str | None = None,
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    q = (q or "").strip()
    hoa_don_list = lay_danh_sach_hoa_don(db)
    thanh_toan_list = lay_danh_sach_thanh_toan(db)
    if q:
        hd_loc = []
        for h in hoa_don_list:
            if q.isdigit():
                if h.ma_hoa_don == int(q) or h.ma_phong == int(q):
                    hd_loc.append(h)
            else:
                if q.lower() in (h.ky_hoa_don or "").lower():
                    hd_loc.append(h)
                elif q.lower() in (h.trang_thai or "").lower():
                    hd_loc.append(h)
        hoa_don_list = hd_loc
        ma_hd = {h.ma_hoa_don for h in hd_loc}
        thanh_toan_list = [t for t in thanh_toan_list if t.ma_hoa_don in ma_hd]
    thong_bao = None
    if ok is not None:
        thong_bao = f"Đã ghi nhận thanh toán {ok:,.0f} VND" + (
            f" (HĐ #{hd})" if hd else ""
        )
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/thanh_toan.html",
        context={
            "user": user,
            "hoa_don_list": hoa_don_list,
            "thanh_toan_list": thanh_toan_list,
            "q": q,
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


@router.post("/thanh-toan/ghi")
def web_ghi_thanh_toan(
    request: Request,
    ma_hoa_don: int = Form(...),
    so_tien: float = Form(...),
    hinh_thuc: str = Form("tien_mat"),
    ghi_chu: str = Form(""),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    try:
        ghi_nhan_thanh_toan(
            db,
            ma_hoa_don=ma_hoa_don,
            so_tien=so_tien,
            hinh_thuc=hinh_thuc,
            ghi_chu=ghi_chu or None,
        )
        return RedirectResponse(
            f"/thanh-toan?ok={int(so_tien)}&hd={ma_hoa_don}",
            status_code=302,
        )
    except ValueError as e:
        return RedirectResponse(f"/thanh-toan?loi={quote(str(e))}", status_code=302)
    except Exception as e:
        return RedirectResponse(f"/thanh-toan?loi={quote(str(e))}", status_code=302)


# ========== DON GIA ==========
@router.get("/don-gia", response_class=HTMLResponse)
def trang_don_gia(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/don_gia.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_don_gia(db),
            "thong_bao": None,
            "loi": None,
        },
    )


@router.post("/don-gia/them", response_class=HTMLResponse)
def web_them_don_gia(
    request: Request,
    loai: str = Form(...),
    ten_muc: str = Form(...),
    don_gia: float = Form(...),
    ngay_hieu_luc: str = Form(...),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach", status_code=302)
    loi = thong_bao = None
    try:
        if don_gia <= 0:
            raise ValueError("Đơn giá phải lớn hơn 0")
        loai_enum = LoaiDonGia.DIEN if loai == "dien" else LoaiDonGia.NUOC
        ng = date.fromisoformat(ngay_hieu_luc)
        for cu in lay_danh_sach_don_gia(db, loai_enum):
            if cu.dang_ap_dung:
                cu.dang_ap_dung = False
        db.flush()
        tao_don_gia(
            db,
            loai=loai_enum,
            ten_muc=ten_muc.strip(),
            don_gia=don_gia,
            ngay_hieu_luc=ng,
            tu_so=0,
            den_so=None,
            dang_ap_dung=True,
        )
        thong_bao = f"Đã cập nhật đơn giá {loai_enum.value}: {don_gia:,.0f} đ"
    except Exception as e:
        loi = str(e)
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/don_gia.html",
        context={
            "user": user,
            "danh_sach": lay_danh_sach_don_gia(db),
            "thong_bao": thong_bao,
            "loi": loi,
        },
    )


# ========== AI CHATBOT (ADMIN) ==========
@router.get("/ai", response_class=HTMLResponse)
def trang_ai(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach/ai", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/ai_canh_bao.html",
        context={
            "user": user,
            "tin_nhan": _lay_chat_log(request),
            "phong_list": lay_danh_sach_phong(db),
        },
    )


@router.post("/ai/chat", response_class=HTMLResponse)
async def trang_ai_chat(
    request: Request,
    cau_hoi: str = Form(""),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach/ai", status_code=302)
    cau = (cau_hoi or "").strip()
    if cau:
        _them_chat(request, "user", cau)
        try:
            kq = await chat_ai(db, cau)
            _them_chat(request, "bot", kq.get("tra_loi") or "Không có phản hồi.")
        except Exception as e:
            _them_chat(request, "bot", f"Lỗi xử lý: {e}")
    return templates.TemplateResponse(
        request=request,
        name="quan_ly/ai_canh_bao.html",
        context={
            "user": user,
            "tin_nhan": _lay_chat_log(request),
            "phong_list": lay_danh_sach_phong(db),
        },
    )


@router.post("/ai/xoa-chat", response_class=HTMLResponse)
def trang_ai_xoa_chat(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    if _la_khach(user):
        return RedirectResponse("/khach/ai", status_code=302)
    key = _chat_key(request)
    if key:
        _chat_logs[key] = []
    return RedirectResponse("/ai", status_code=302)


# ========== KHACH THUE ==========
@router.get("/khach", response_class=HTMLResponse)
def trang_khach(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    phong = (
        db.query(Phong)
        .filter(Phong.ma_khach_thue == user.ma_nguoi_dung)
        .first()
    )
    hoa_don = lay_danh_sach_hoa_don(db, ma_phong=phong.ma_phong) if phong else []
    return templates.TemplateResponse(
        request=request,
        name="khach/trang_chu.html",
        context={"user": user, "phong": phong, "hoa_don_list": hoa_don},
    )


@router.get("/khach/ai", response_class=HTMLResponse)
def trang_khach_ai(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    phong = (
        db.query(Phong)
        .filter(Phong.ma_khach_thue == user.ma_nguoi_dung)
        .first()
    )
    return templates.TemplateResponse(
        request=request,
        name="khach/ai.html",
        context={
            "user": user,
            "phong": phong,
            "tin_nhan": _lay_chat_log(request),
        },
    )


@router.post("/khach/ai/chat", response_class=HTMLResponse)
async def trang_khach_ai_chat(
    request: Request,
    cau_hoi: str = Form(""),
    db: Session = Depends(lay_db),
):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    phong = (
        db.query(Phong)
        .filter(Phong.ma_khach_thue == user.ma_nguoi_dung)
        .first()
    )
    cau = (cau_hoi or "").strip()
    if cau:
        _them_chat(request, "user", cau)
        if not phong:
            _them_chat(
                request,
                "bot",
                "Tài khoản chưa được gán vào hộ. Liên hệ quản lý.",
            )
        else:
            try:
                kq = await chat_ai(
                    db,
                    cau,
                    chi_duoc_ma_phong=phong.ma_phong,
                )
                _them_chat(request, "bot", kq.get("tra_loi") or "Không có phản hồi.")
            except Exception as e:
                _them_chat(request, "bot", f"Lỗi xử lý: {e}")
    return templates.TemplateResponse(
        request=request,
        name="khach/ai.html",
        context={
            "user": user,
            "phong": phong,
            "tin_nhan": _lay_chat_log(request),
        },
    )


@router.post("/khach/ai/xoa-chat", response_class=HTMLResponse)
def trang_khach_xoa_chat(request: Request, db: Session = Depends(lay_db)):
    user = _require_user(request, db)
    if not user:
        return RedirectResponse("/dang-nhap", status_code=302)
    key = _chat_key(request)
    if key:
        _chat_logs[key] = []
    return RedirectResponse("/khach/ai", status_code=302)