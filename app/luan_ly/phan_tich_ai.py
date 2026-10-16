# -*- coding: utf-8 -*-
"""
Chatbot AI (Groq) + phan tich tieu thu.
- Model mac dinh: openai/gpt-oss-20b
- Tra loi ngan, moi y 1 dong; fallback khi API loi.
"""

import re
import httpx
from sqlalchemy.orm import Session

from app.cau_hinh.cai_dat import cai_dat
from app.mo_hinh.canh_bao_ai import CanhBaoAI
from app.mo_hinh.hoa_don import HoaDon
from app.mo_hinh.phong import Phong


def _lay_lich_su_hoa_don(db: Session, ma_phong: int, so_thang: int = 6) -> list[HoaDon]:
    return (
        db.query(HoaDon)
        .filter(HoaDon.ma_phong == ma_phong)
        .order_by(HoaDon.ky_hoa_don.desc())
        .limit(so_thang)
        .all()
    )


def _tinh_muc_tang(hien_tai: float, trung_binh: float) -> float:
    if trung_binh <= 0:
        return 0.0
    return ((hien_tai - trung_binh) / trung_binh) * 100


def _lam_sach_tra_loi(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    t = (
        t.replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
        .replace("<BR>", "\n")
        .replace("<BR/>", "\n")
        .replace("<BR />", "\n")
    )
    t = re.sub(r"<[^>]+>", "", t)
    while "\n\n\n" in t:
        t = t.replace("\n\n\n", "\n\n")
    return t.strip()


def _tao_nhan_xet_fallback(
    ten_ho: str,
    tien_dien: float,
    tien_nuoc: float,
    tb_dien: float,
    tb_nuoc: float,
    pct_dien: float,
    pct_nuoc: float,
) -> tuple[str, str, str]:
    canh_bao, goi_y = [], []
    muc_do = "thap"
    if pct_dien >= 30:
        canh_bao.append(
            f"Tiền điện tăng {pct_dien:.0f}% so với TB "
            f"({tien_dien:,.0f} vs {tb_dien:,.0f} VND)."
        )
        goi_y.append("Kiểm tra điều hòa, bình nóng lạnh.")
        muc_do = "cao" if pct_dien >= 50 else "trung_binh"
    if pct_nuoc >= 30:
        canh_bao.append(
            f"Tiền nước tăng {pct_nuoc:.0f}% so với TB "
            f"({tien_nuoc:,.0f} vs {tb_nuoc:,.0f} VND)."
        )
        goi_y.append("Kiểm tra bồn cầu, vòi nước, đường ống rò.")
        if pct_nuoc >= 50:
            muc_do = "cao"
        elif muc_do == "thap":
            muc_do = "trung_binh"
    if not canh_bao:
        return (
            "goi_y",
            f"Hộ {ten_ho}: điện/nước kỳ này ổn định.\n"
            f"Điện {tien_dien:,.0f} VND · Nước {tien_nuoc:,.0f} VND.\n"
            f"Không thấy bất thường đáng kể.",
            "thap",
        )
    noi = (
        f"Hộ {ten_ho} – CẢNH BÁO:\n"
        + "\n".join(f"- {c}" for c in canh_bao)
        + "\nGợi ý:\n"
        + "\n".join(f"- {g}" for g in goi_y)
    )
    return "bat_thuong", noi, muc_do


async def _goi_gemini(prompt: str) -> str | None:
    if not cai_dat.ai_api_key:
        print("AI: thieu AI_API_KEY trong .env")
        return None

    url = cai_dat.ai_api_url or "https://api.groq.com/openai/v1/chat/completions"
    model = (getattr(cai_dat, "ai_model", None) or "").strip() or "openai/gpt-oss-20b"

    headers = {
        "Authorization": f"Bearer {cai_dat.ai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Bạn là chatbot tiếng Việt hệ thống hóa đơn điện nước. "
                    "Trả lời NGẮN tối đa 5 dòng. Mỗi ý một dòng riêng. "
                    "Xuống dòng thật, CẤM viết thẻ HTML như <br>. "
                    "Không đoạn văn dài. Chỉ tiếng Việt có dấu."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    async def _mot_lan() -> str | None:
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"AI status={resp.status_code} model={model}")
            if resp.status_code == 429:
                print("AI rate limit 429")
                return None
            if resp.status_code != 200:
                print(f"AI body: {resp.text[:400]}")
                return None

            data = resp.json()
            choices = data.get("choices") or []
            if not choices:
                print(f"AI empty choices: {str(data)[:300]}")
                return None

            msg = choices[0].get("message") or {}
            text = str(msg.get("content") or "").strip()
            if not text or len(text) < 6:
                print(f"AI short content: {str(msg)[:250]}")
                return None

            text = _lam_sach_tra_loi(text)
            if not text or len(text) < 6:
                return None

            low = text.lower()
            if any(
                x in low
                for x in ["sentence 1", "sentence 2", "electricity analysis", "<html", "<!doctype"]
            ):
                print(f"AI rejected: {text[:100]}")
                return None
            return text

    try:
        kq = await _mot_lan()
        if kq:
            return kq
        # Thu lai 1 lan (rate limit / glitch)
        import asyncio as _aio
        await _aio.sleep(1.5)
        print("AI retry...")
        return await _mot_lan()
    except Exception as e:
        print(f"AI exception: {e}")
        return None


async def phan_tich_phong(
    db: Session,
    ma_phong: int,
    ma_hoa_don: int | None = None,
) -> CanhBaoAI:
    phong = db.query(Phong).filter(Phong.ma_phong == ma_phong).first()
    if not phong:
        raise ValueError("Khong tim thay ho gia dinh")
    if ma_hoa_don:
        hd = db.query(HoaDon).filter(HoaDon.ma_hoa_don == ma_hoa_don).first()
    else:
        hd = (
            db.query(HoaDon)
            .filter(HoaDon.ma_phong == ma_phong)
            .order_by(HoaDon.ky_hoa_don.desc())
            .first()
        )
    if not hd:
        raise ValueError("Ho chua co hoa don")

    lich_su = [
        h for h in _lay_lich_su_hoa_don(db, ma_phong, 6) if h.ma_hoa_don != hd.ma_hoa_don
    ]
    tien_dien = float(hd.tong_tien_dien or 0)
    tien_nuoc = float(hd.tong_tien_nuoc or 0)
    if lich_su:
        tb_dien = sum(float(h.tong_tien_dien or 0) for h in lich_su) / len(lich_su)
        tb_nuoc = sum(float(h.tong_tien_nuoc or 0) for h in lich_su) / len(lich_su)
    else:
        tb_dien, tb_nuoc = tien_dien, tien_nuoc
    pct_dien = _tinh_muc_tang(tien_dien, tb_dien)
    pct_nuoc = _tinh_muc_tang(tien_nuoc, tb_nuoc)

    prompt = (
        "Viết NHẬN XÉT NGẮN (tối đa 5 dòng, mỗi ý 1 dòng) bằng tiếng Việt.\n"
        "CẤM thẻ HTML.\n"
        f"Số liệu (cấm bịa): hộ {phong.ten_phong}, mã {ma_phong}, kỳ {hd.ky_hoa_don}, "
        f"điện {tien_dien:,.0f} VND, nước {tien_nuoc:,.0f} VND, "
        f"TB điện {tb_dien:,.0f}, TB nước {tb_nuoc:,.0f}, "
        f"đổi điện {pct_dien:+.1f}%, đổi nước {pct_nuoc:+.1f}%.\n"
        "Dòng 1: kết luận. Dòng 2: số chính. Dòng 3: cảnh báo nếu ≥30%. Dòng 4: 1 gợi ý ngắn."
    )
    noi = await _goi_gemini(prompt)
    if not noi or len(noi) < 20:
        loai, noi, muc = _tao_nhan_xet_fallback(
            phong.ten_phong, tien_dien, tien_nuoc, tb_dien, tb_nuoc, pct_dien, pct_nuoc
        )
    else:
        loai = "bat_thuong" if (pct_dien >= 30 or pct_nuoc >= 30) else "goi_y"
        muc = (
            "cao"
            if (pct_dien >= 50 or pct_nuoc >= 50)
            else ("trung_binh" if (pct_dien >= 30 or pct_nuoc >= 30) else "thap")
        )

    cb = CanhBaoAI(
        ma_phong=ma_phong,
        ma_hoa_don=hd.ma_hoa_don,
        loai_canh_bao=loai,
        noi_dung=noi.strip(),
        muc_do=muc,
        da_xu_ly=False,
    )
    db.add(cb)
    db.commit()
    db.refresh(cb)
    return cb


def lay_canh_bao_phong(db: Session, ma_phong: int) -> list[CanhBaoAI]:
    return (
        db.query(CanhBaoAI)
        .filter(CanhBaoAI.ma_phong == ma_phong)
        .order_by(CanhBaoAI.ngay_tao.desc())
        .all()
    )


def _trich_ma_phong_tu_cau(cau: str) -> int | None:
    if not cau:
        return None
    m = re.search(
        r"(?:h[oộ]\s*(?:gia\s*đình\s*)?|phòng|phong|mã\s*h[oộ]?|ma\s*ho?|#)\s*[:\.]?\s*(\d+)",
        cau,
        flags=re.IGNORECASE,
    )
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _noi_dung_ngoai_pham_vi(cau: str) -> bool:
    t = (cau or "").lower().strip()
    he = [
        "điện", "dien", "nước", "nuoc", "hóa đơn", "hoa don", "hộ", "ho ",
        "phòng", "phong", "chỉ số", "chi so", "công tơ", "cong to",
        "thanh toán", "thanh toan", "công nợ", "cong no", "nợ", " no",
        "đơn giá", "don gia", "tiết kiệm", "tiet kiem", "cảnh báo", "canh bao",
        "phân tích", "phan tich", "kỳ", "vnd", "tiền", "tien", "mã hộ", "ma ho",
        "tiêu thụ", "tieu thu", "gợi ý", "goi y",
    ]
    if any(k in t for k in he):
        return False
    if len(t) < 3:
        return False
    ngoai = [
        "thời tiết", "thoi tiet", "bóng đá", "bong da", "chứng khoán",
        "nấu ăn", "nau an", "viết code", "viet code", "dịch bài",
        "1+1", "bao nhiêu bằng", "toán",
    ]
    return any(k in t for k in ngoai)


def _dong_goi_context_ho(db: Session, ma_phong: int) -> str | None:
    phong = db.query(Phong).filter(Phong.ma_phong == ma_phong).first()
    if not phong:
        return None
    hd_list = _lay_lich_su_hoa_don(db, ma_phong, 6)
    if not hd_list:
        return f"Hộ {phong.ten_phong} (mã {ma_phong}): chưa có hóa đơn."

    hd = hd_list[0]
    lich = hd_list[1:]
    td = float(hd.tong_tien_dien or 0)
    tn = float(hd.tong_tien_nuoc or 0)
    tong = float(hd.tong_tien or 0)
    da = float(hd.so_tien_da_tra or 0)
    no = max(0.0, tong - da)
    if lich:
        tb_d = sum(float(h.tong_tien_dien or 0) for h in lich) / len(lich)
        tb_n = sum(float(h.tong_tien_nuoc or 0) for h in lich) / len(lich)
    else:
        tb_d, tb_n = td, tn
    lines = [
        f"  Kỳ {h.ky_hoa_don}: điện {float(h.tong_tien_dien or 0):,.0f}, "
        f"nước {float(h.tong_tien_nuoc or 0):,.0f}, tổng {float(h.tong_tien or 0):,.0f}, "
        f"đã trả {float(h.so_tien_da_tra or 0):,.0f}, TT={h.trang_thai}"
        for h in hd_list[:4]
    ]
    return (
        f"Hộ: {phong.ten_phong} | Mã: {ma_phong} | Số người: {phong.so_nguoi_o}\n"
        f"Kỳ gần nhất: {hd.ky_hoa_don}\n"
        f"Tiền điện: {td:,.0f} VND | Tiền nước: {tn:,.0f} VND\n"
        f"Tổng HĐ: {tong:,.0f} VND | Đã trả: {da:,.0f} VND | Còn nợ: {no:,.0f} VND\n"
        f"Trạng thái: {hd.trang_thai}\n"
        f"TB kỳ trước — điện {tb_d:,.0f} | nước {tb_n:,.0f}\n"
        f"Đổi điện {_tinh_muc_tang(td, tb_d):+.1f}% | Đổi nước {_tinh_muc_tang(tn, tb_n):+.1f}%\n"
        f"Lịch sử:\n" + "\n".join(lines)
    )


def _fallback_theo_cau(db: Session, cau: str, ma_phong: int | None) -> str:
    t = (cau or "").lower()
    if ma_phong is None:
        return (
            "Hiện chưa gọi được dịch vụ AI.\n"
            "Hỏi lại sau hoặc nêu rõ mã hộ (vd: Phân tích hộ 22)."
        )
    phong = db.query(Phong).filter(Phong.ma_phong == ma_phong).first()
    hd = (
        db.query(HoaDon)
        .filter(HoaDon.ma_phong == ma_phong)
        .order_by(HoaDon.ky_hoa_don.desc())
        .first()
    )
    if not phong:
        return f"Không tìm thấy hộ mã {ma_phong}."
    if not hd:
        return f"Hộ {phong.ten_phong} chưa có hóa đơn."

    tong = float(hd.tong_tien or 0)
    da = float(hd.so_tien_da_tra or 0)
    no = max(0.0, tong - da)
    td = float(hd.tong_tien_dien or 0)
    tn = float(hd.tong_tien_nuoc or 0)

    if any(k in t for k in ["nợ", "no ", "công nợ", "cong no", "con no"]):
        if no <= 0:
            return (
                f"Hộ {phong.ten_phong} kỳ {hd.ky_hoa_don}: không còn nợ.\n"
                f"(Số liệu hệ thống — AI tạm gián đoạn)"
            )
        return (
            f"Hộ {phong.ten_phong} kỳ {hd.ky_hoa_don}: còn nợ {no:,.0f} VND.\n"
            f"Tổng {tong:,.0f} · Đã trả {da:,.0f}.\n"
            f"(Số liệu hệ thống — AI tạm gián đoạn)"
        )

    lich = [h for h in _lay_lich_su_hoa_don(db, ma_phong, 6) if h.ma_hoa_don != hd.ma_hoa_don]
    if lich:
        tb_d = sum(float(h.tong_tien_dien or 0) for h in lich) / len(lich)
        tb_n = sum(float(h.tong_tien_nuoc or 0) for h in lich) / len(lich)
    else:
        tb_d, tb_n = td, tn
    _, text, _ = _tao_nhan_xet_fallback(
        phong.ten_phong,
        td,
        tn,
        tb_d,
        tb_n,
        _tinh_muc_tang(td, tb_d),
        _tinh_muc_tang(tn, tb_n),
    )
    return f"[AI tạm gián đoạn]\n{text}"


async def chat_ai(
    db: Session,
    cau_hoi: str,
    *,
    ma_phong_mac_dinh: int | None = None,
    chi_duoc_ma_phong: int | None = None,
) -> dict:
    cau = (cau_hoi or "").strip()
    if not cau:
        return {
            "tra_loi": "Bạn hãy nhập câu hỏi về hóa đơn điện nước, hộ hoặc tiết kiệm.",
            "ma_phong": None,
            "tu_choi": False,
        }

    if chi_duoc_ma_phong is not None:
        ma_phong = chi_duoc_ma_phong
    else:
        ma_phong = _trich_ma_phong_tu_cau(cau) or ma_phong_mac_dinh

    if _noi_dung_ngoai_pham_vi(cau):
        return {
            "tra_loi": (
                "Mình chỉ hỗ trợ: hộ, hóa đơn, công nợ, phân tích tiêu thụ, gợi ý tiết kiệm.\n"
                "Vui lòng hỏi trong phạm vi hệ thống."
            ),
            "ma_phong": None,
            "tu_choi": True,
        }

    context = ""
    if ma_phong is not None:
        ctx = _dong_goi_context_ho(db, ma_phong)
        if ctx is None and chi_duoc_ma_phong is None:
            return {
                "tra_loi": f"Không tìm thấy hộ mã {ma_phong}.",
                "ma_phong": ma_phong,
                "tu_choi": False,
            }
        context = ctx or ""

    huong_dan = (
        "Trả lời NGẮN (tối đa 5 dòng). Mỗi ý một dòng.\n"
        "CẤM viết thẻ HTML (<br>, <p>, …). Chỉ xuống dòng thật.\n"
        "Dòng 1: kết luận (còn nợ / không nợ / tăng bất thường…).\n"
        "Dòng 2–3: 1–2 số từ DỮ LIỆU.\n"
        "Dòng 4: 1 gợi ý ngắn nếu hỏi phân tích/tiết kiệm.\n"
        "Cấm bịa số ngoài DỮ LIỆU."
    )

    if context:
        prompt = (
            f"{huong_dan}\n\n"
            f"=== DỮ LIỆU HỆ THỐNG ===\n{context}\n=== HẾT DỮ LIỆU ===\n\n"
            f"Câu hỏi: {cau}\n\n"
            f"Trả lời ngắn, mỗi ý 1 dòng:"
        )
    else:
        prompt = (
            f"{huong_dan}\n\n"
            f"Chưa có mã hộ. Nếu cần số liệu, nhờ nêu mã hộ (vd: hộ 22).\n\n"
            f"Câu hỏi: {cau}\n\n"
            f"Trả lời ngắn, mỗi ý 1 dòng:"
        )

    noi = await _goi_gemini(prompt)

    if noi and len(noi.strip()) >= 8:
        return {
            "tra_loi": noi.strip(),
            "ma_phong": ma_phong,
            "tu_choi": False,
        }

    return {
        "tra_loi": _fallback_theo_cau(db, cau, ma_phong),
        "ma_phong": ma_phong,
        "tu_choi": False,
    }