# -*- coding: utf-8 -*-
"""
Chatbot AI (Groq) + phan tich tieu thu.
- Phan loai y dinh cau hoi (no / tiet kiem / phan tich) de tra dung trong tam.
- Giong than thien; co AI: [AI · Groq]; khong AI: [Du phong · khong ket noi AI].
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
            f"Tiền điện tăng {pct_dien:.0f}% so với trung bình "
            f"({tien_dien:,.0f} so với {tb_dien:,.0f} VND)."
        )
        goi_y.append("Nên kiểm tra điều hòa, bình nóng lạnh và thiết bị công suất lớn.")
        muc_do = "cao" if pct_dien >= 50 else "trung_binh"
    if pct_nuoc >= 30:
        canh_bao.append(
            f"Tiền nước tăng {pct_nuoc:.0f}% so với trung bình "
            f"({tien_nuoc:,.0f} so với {tb_nuoc:,.0f} VND)."
        )
        goi_y.append("Nên kiểm tra bồn cầu, vòi nước và đường ống xem có rò không.")
        if pct_nuoc >= 50:
            muc_do = "cao"
        elif muc_do == "thap":
            muc_do = "trung_binh"
    if not canh_bao:
        return (
            "goi_y",
            (
                f"Hộ {ten_ho} kỳ này tiêu thụ khá ổn định so với các kỳ trước.\n"
                f"Tiền điện khoảng {tien_dien:,.0f} VND, tiền nước khoảng {tien_nuoc:,.0f} VND.\n"
                f"Chưa thấy biến động lớn (dưới ngưỡng 30%)."
            ),
            "thap",
        )
    noi = (
        f"Hộ {ten_ho} có dấu hiệu bất thường:\n"
        + "\n".join(f"• {c}" for c in canh_bao)
        + "\nGợi ý:\n"
        + "\n".join(f"• {g}" for g in goi_y)
    )
    return "bat_thuong", noi, muc_do


def _phan_loai_y_dinh(cau: str) -> str:
    """no | tiet_kiem | phan_tich | khac"""
    t = (cau or "").lower()
    if any(k in t for k in ["còn nợ", "con no", "công nợ", "cong no", "nợ không", "no khong", "nợ bao", "no bao", "còn nợ?"]):
        return "no"
    if any(k in t for k in ["nợ", " no", "no?"]):
        # "hộ 22 còn nợ?" đã bắt ở trên; "nợ" đơn lẻ
        if "tiết kiệm" not in t and "tiet kiem" not in t and "phân tích" not in t and "phan tich" not in t:
            return "no"
    if any(k in t for k in ["tiết kiệm", "tiet kiem", "gợi ý", "goi y", "giảm điện", "giam dien", "giảm nước", "giam nuoc"]):
        return "tiet_kiem"
    if any(k in t for k in ["phân tích", "phan tich", "tiêu thụ", "tieu thu", "bất thường", "bat thuong", "cảnh báo", "canh bao"]):
        return "phan_tich"
    return "khac"


def _so_lieu_ho(db: Session, ma_phong: int) -> dict | None:
    phong = db.query(Phong).filter(Phong.ma_phong == ma_phong).first()
    if not phong:
        return None
    hd_list = _lay_lich_su_hoa_don(db, ma_phong, 6)
    if not hd_list:
        return {
            "phong": phong,
            "hd": None,
            "td": 0.0,
            "tn": 0.0,
            "tong": 0.0,
            "da": 0.0,
            "no": 0.0,
            "tb_d": 0.0,
            "tb_n": 0.0,
            "pct_d": 0.0,
            "pct_n": 0.0,
        }
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
    return {
        "phong": phong,
        "hd": hd,
        "td": td,
        "tn": tn,
        "tong": tong,
        "da": da,
        "no": no,
        "tb_d": tb_d,
        "tb_n": tb_n,
        "pct_d": _tinh_muc_tang(td, tb_d),
        "pct_n": _tinh_muc_tang(tn, tb_n),
    }


def _tra_loi_mem_no(s: dict) -> str:
    p, hd = s["phong"], s["hd"]
    if not hd:
        return (
            f"Dạ, hộ {p.ten_phong} hiện chưa có hóa đơn trong hệ thống nên mình chưa xác định được công nợ ạ.\n"
            f"Khi có hóa đơn mới, bạn hỏi lại mình nhé."
        )
    if s["no"] <= 0:
        return (
            f"Dạ, theo hóa đơn kỳ {hd.ky_hoa_don} thì hộ {p.ten_phong} hiện không còn nợ.\n"
            f"Tổng hóa đơn {s['tong']:,.0f} VND đã được thanh toán đủ ({s['da']:,.0f} VND).\n"
            f"Bạn yên tâm về phần công nợ kỳ này nhé."
        )
    return (
        f"Dạ, hộ {p.ten_phong} kỳ {hd.ky_hoa_don} còn nợ {s['no']:,.0f} VND ạ.\n"
        f"Tổng hóa đơn {s['tong']:,.0f} VND, đã trả {s['da']:,.0f} VND.\n"
        f"Trạng thái hiện tại: {hd.trang_thai}."
    )


def _tra_loi_mem_tiet_kiem(s: dict) -> str:
    p, hd = s["phong"], s["hd"]
    if not hd:
        return (
            f"Dạ, hộ {p.ten_phong} chưa có hóa đơn nên mình chưa đưa được gợi ý gắn số liệu.\n"
            f"Gợi ý chung: hạn chế để điều hòa quá lạnh lâu, tắt thiết bị khi không dùng, "
            f"và kiểm tra vòi nước/bồn cầu định kỳ."
        )
    lines = [
        f"Dạ, mình gợi ý vài cách tiết kiệm cho hộ {p.ten_phong} dựa trên kỳ {hd.ky_hoa_don}:",
        f"Kỳ này tiền điện khoảng {s['td']:,.0f} VND, tiền nước khoảng {s['tn']:,.0f} VND.",
    ]
    if s["pct_n"] >= 30:
        lines.append(
            f"Tiền nước đang tăng khoảng {s['pct_n']:.0f}% so với trung bình — nên ưu tiên kiểm tra bồn cầu, vòi nước và đường ống."
        )
    else:
        lines.append("Về nước: kiểm tra định kỳ bồn cầu và vòi xem có nhỏ giọt không.")
    if s["pct_d"] >= 30:
        lines.append(
            f"Tiền điện tăng khoảng {s['pct_d']:.0f}% so với trung bình — nên xem lại điều hòa, bình nóng lạnh và thiết bị công suất lớn."
        )
    else:
        lines.append("Về điện: hạn chế bật điều hòa nhiệt độ thấp quá lâu và tắt đèn/thiết bị khi không cần.")
    lines.append("Nếu cần, mình có thể phân tích chi tiết hơn theo từng kỳ hóa đơn.")
    return "\n".join(lines)


def _tra_loi_mem_phan_tich(s: dict) -> str:
    p, hd = s["phong"], s["hd"]
    if not hd:
        return f"Dạ, hộ {p.ten_phong} chưa có hóa đơn để phân tích ạ."
    _, text, _ = _tao_nhan_xet_fallback(
        p.ten_phong, s["td"], s["tn"], s["tb_d"], s["tb_n"], s["pct_d"], s["pct_n"]
    )
    return (
        f"Dạ, mình phân tích nhanh hộ {p.ten_phong} kỳ {hd.ky_hoa_don}:\n"
        + text
    )


SYSTEM_PROMPT = (
    "Bạn là trợ lý AI thân thiện của hệ thống quản lý hóa đơn điện–nước.\n"
    "Nói tiếng Việt có dấu, tự nhiên như nhân viên hỗ trợ lịch sự.\n"
    "Chỉ dùng số trong DỮ LIỆU. Cấm bịa số. Không HTML.\n"
    "Trả lời đúng trọng tâm câu hỏi; 4–7 dòng; có thể mở đầu bằng 'Dạ…'."
)


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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.45,
        "max_tokens": 1100,
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
        import asyncio as _aio
        await _aio.sleep(1.5)
        print("AI retry...")
        return await _mot_lan()
    except Exception as e:
        print(f"AI exception: {e}")
        return None


async def _lam_mem_bang_ai(cau: str, ban_cung: str, context: str) -> str | None:
    """Nhe nhang hoa cau tra loi chuan, giu nguyen so lieu."""
    prompt = (
        "Viết lại đoạn trả lời dưới đây cho tự nhiên, thân thiện hơn (tiếng Việt có dấu).\n"
        "GIỮ NGUYÊN mọi số liệu, không thêm số mới, không HTML.\n"
        "Đúng trọng tâm câu hỏi; 4–7 dòng.\n\n"
        f"Câu hỏi: {cau}\n\n"
        f"Dữ liệu (tham khảo):\n{context}\n\n"
        f"Nội dung cần viết lại:\n{ban_cung}\n\n"
        "Chỉ viết câu trả lời cuối cùng:"
    )
    return await _goi_gemini(prompt)


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

    ban_cung = _tra_loi_mem_phan_tich(
        {
            "phong": phong,
            "hd": hd,
            "td": tien_dien,
            "tn": tien_nuoc,
            "tong": float(hd.tong_tien or 0),
            "da": float(hd.so_tien_da_tra or 0),
            "no": max(0.0, float(hd.tong_tien or 0) - float(hd.so_tien_da_tra or 0)),
            "tb_d": tb_dien,
            "tb_n": tb_nuoc,
            "pct_d": pct_dien,
            "pct_n": pct_nuoc,
        }
    )
    ctx = (
        f"Hộ {phong.ten_phong}, kỳ {hd.ky_hoa_don}, "
        f"điện {tien_dien:,.0f}, nước {tien_nuoc:,.0f}, "
        f"TB điện {tb_dien:,.0f}, TB nước {tb_nuoc:,.0f}, "
        f"đổi điện {pct_dien:+.1f}%, đổi nước {pct_nuoc:+.1f}%."
    )
    noi = await _lam_mem_bang_ai("Phân tích tiêu thụ hộ này", ban_cung, ctx)
    if not noi or len(noi) < 20:
        loai, noi0, muc = _tao_nhan_xet_fallback(
            phong.ten_phong, tien_dien, tien_nuoc, tb_dien, tb_nuoc, pct_dien, pct_nuoc
        )
        noi = "[Dự phòng · không kết nối AI]\n" + (ban_cung if ban_cung else noi0)
    else:
        noi = "[AI · Groq]\n" + noi.strip()
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
    # "ho 3", "hộ3"
    m2 = re.search(r"\b(?:ho|hộ)\s*(\d+)\b", cau, flags=re.IGNORECASE)
    if m2:
        try:
            return int(m2.group(1))
        except ValueError:
            return None
    return None


def _noi_dung_ngoai_pham_vi(cau: str) -> bool:
    t = (cau or "").lower().strip()
    if len(t) <= 12 and t in {"ok", "ok nhé", "ok nhe", "cảm ơn", "cam on", "thanks", "hi", "hello"}:
        return False

    he = [
        "điện", "dien", "nước", "nuoc", "hóa đơn", "hoa don", "hộ", "ho ",
        "phòng", "phong", "chỉ số", "chi so", "công tơ", "cong to",
        "thanh toán", "thanh toan", "công nợ", "cong no", "nợ", " no",
        "đơn giá", "don gia", "tiết kiệm", "tiet kiem", "cảnh báo", "canh bao",
        "phân tích", "phan tich", "kỳ", "vnd", "tiền", "tien", "mã hộ", "ma ho",
        "tiêu thụ", "tieu thu", "gợi ý", "goi y", "còn nợ", "con no",
    ]
    if any(k in t for k in he):
        return False
    if len(t) < 3:
        return False
    ngoai = [
        "thời tiết", "thoi tiet", "bóng đá", "bong da", "chứng khoán",
        "nấu ăn", "nau an", "viết code", "viet code", "dịch bài",
        "1+1", "bao nhiêu bằng", "toán", "mấy giờ", "tin tức",
    ]
    return any(k in t for k in ngoai)


def _dong_goi_context_ho(db: Session, ma_phong: int) -> str | None:
    s = _so_lieu_ho(db, ma_phong)
    if not s:
        return None
    phong, hd = s["phong"], s["hd"]
    if not hd:
        return f"Hộ {phong.ten_phong} (mã {ma_phong}): chưa có hóa đơn."
    hd_list = _lay_lich_su_hoa_don(db, ma_phong, 6)
    lines = [
        f"  Kỳ {h.ky_hoa_don}: điện {float(h.tong_tien_dien or 0):,.0f}, "
        f"nước {float(h.tong_tien_nuoc or 0):,.0f}, tổng {float(h.tong_tien or 0):,.0f}, "
        f"đã trả {float(h.so_tien_da_tra or 0):,.0f}, TT={h.trang_thai}"
        for h in hd_list[:4]
    ]
    return (
        f"Hộ: {phong.ten_phong} | Mã: {ma_phong} | Số người: {phong.so_nguoi_o}\n"
        f"Kỳ gần nhất: {hd.ky_hoa_don}\n"
        f"Tiền điện: {s['td']:,.0f} VND | Tiền nước: {s['tn']:,.0f} VND\n"
        f"Tổng HĐ: {s['tong']:,.0f} VND | Đã trả: {s['da']:,.0f} VND | Còn nợ: {s['no']:,.0f} VND\n"
        f"Trạng thái: {hd.trang_thai}\n"
        f"TB kỳ trước — điện {s['tb_d']:,.0f} | nước {s['tb_n']:,.0f}\n"
        f"Đổi điện {s['pct_d']:+.1f}% | Đổi nước {s['pct_n']:+.1f}%\n"
        f"Lịch sử:\n" + "\n".join(lines)
    )


def _fallback_theo_cau(db: Session, cau: str, ma_phong: int | None) -> str:
    prefix = "[Dự phòng · không kết nối AI]\n"
    if ma_phong is None:
        return (
            prefix
            + "Hiện mình chưa kết nối được dịch vụ AI (thiếu key, lỗi mạng hoặc hết hạn mức).\n"
            "Bạn hỏi lại sau hoặc nêu rõ mã hộ (vd: Phân tích hộ 22) nhé.\n"
            "Phần lập hóa đơn và thanh toán vẫn dùng bình thường."
        )
    s = _so_lieu_ho(db, ma_phong)
    if not s:
        return prefix + f"Không tìm thấy hộ mã {ma_phong}."
    y = _phan_loai_y_dinh(cau)
    if y == "no":
        return prefix + _tra_loi_mem_no(s)
    if y == "tiet_kiem":
        return prefix + _tra_loi_mem_tiet_kiem(s)
    if y == "phan_tich":
        return prefix + _tra_loi_mem_phan_tich(s)
    return prefix + _tra_loi_mem_phan_tich(s)


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
            "tra_loi": "Bạn hãy nhập câu hỏi về hóa đơn điện nước, công nợ hoặc tiết kiệm nhé.",
            "ma_phong": None,
            "tu_choi": False,
            "nguon": "he_thong",
        }

    if chi_duoc_ma_phong is not None:
        ma_phong = chi_duoc_ma_phong
    else:
        ma_phong = _trich_ma_phong_tu_cau(cau) or ma_phong_mac_dinh

    if _noi_dung_ngoai_pham_vi(cau):
        return {
            "tra_loi": (
                "Mình chỉ hỗ trợ trong hệ thống hóa đơn điện–nước thôi ạ:\n"
                "• Công nợ / đã thanh toán\n"
                "• Phân tích tiêu thụ & cảnh báo\n"
                "• Gợi ý tiết kiệm điện–nước\n"
                "Bạn hỏi lại theo các chủ đề trên giúp mình nhé."
            ),
            "ma_phong": None,
            "tu_choi": True,
            "nguon": "he_thong",
        }

    low = cau.lower()
    if low in {"ok", "ok nhé", "ok nhe", "cảm ơn", "cam on", "thanks", "hi", "hello"}:
        return {
            "tra_loi": (
                "Dạ, mình sẵn sàng hỗ trợ.\n"
                "Bạn có thể hỏi còn nợ, phân tích tiêu thụ, hoặc gợi ý tiết kiệm ạ."
            ),
            "ma_phong": ma_phong,
            "tu_choi": False,
            "nguon": "he_thong",
        }

    context = ""
    s = None
    if ma_phong is not None:
        s = _so_lieu_ho(db, ma_phong)
        if s is None and chi_duoc_ma_phong is None:
            return {
                "tra_loi": f"Không tìm thấy hộ mã {ma_phong}.",
                "ma_phong": ma_phong,
                "tu_choi": False,
                "nguon": "he_thong",
            }
        context = _dong_goi_context_ho(db, ma_phong) or ""

    y_dinh = _phan_loai_y_dinh(cau)

    # Co so lieu: tao cau tra loi chuan theo y dinh, roi nho AI viet lai mem (neu goi duoc)
    if s and s.get("hd") is not None:
        if y_dinh == "no":
            ban_cung = _tra_loi_mem_no(s)
        elif y_dinh == "tiet_kiem":
            ban_cung = _tra_loi_mem_tiet_kiem(s)
        else:
            ban_cung = _tra_loi_mem_phan_tich(s)

        noi = await _lam_mem_bang_ai(cau, ban_cung, context)
        if noi and len(noi.strip()) >= 8:
            return {
                "tra_loi": "[AI · Groq]\n" + noi.strip(),
                "ma_phong": ma_phong,
                "tu_choi": False,
                "nguon": "ai",
            }
        # Khong goi duoc AI -> tra loi mem tu du lieu (van dung trong tam)
        return {
            "tra_loi": "[Dự phòng · không kết nối AI]\n" + ban_cung,
            "ma_phong": ma_phong,
            "tu_choi": False,
            "nguon": "fallback",
        }

    # Khong co ma ho / chua co HD: goi AI chung hoac fallback
    if context:
        prompt = (
            f"Câu hỏi: {cau}\n\n"
            f"=== DỮ LIỆU ===\n{context}\n=== HẾT ===\n\n"
            "Trả lời thân thiện, đúng trọng tâm, 4–7 dòng:"
        )
    else:
        prompt = (
            "Chưa có mã hộ. Trả lời thân thiện; nếu cần số liệu cụ thể thì nhờ nêu mã hộ.\n\n"
            f"Câu hỏi: {cau}\n\nTrả lời:"
        )

    noi = await _goi_gemini(prompt)
    if noi and len(noi.strip()) >= 8:
        return {
            "tra_loi": "[AI · Groq]\n" + noi.strip(),
            "ma_phong": ma_phong,
            "tu_choi": False,
            "nguon": "ai",
        }

    return {
        "tra_loi": _fallback_theo_cau(db, cau, ma_phong),
        "ma_phong": ma_phong,
        "tu_choi": False,
        "nguon": "fallback",
    }