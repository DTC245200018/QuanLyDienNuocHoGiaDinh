"""
IoT gia lap cong to dien/nuoc.
- Doc chi so moi nhat trong DB
- Tang ngau nhien bang SO NGUYEN (1,2,3,...)
- Ghi chi so moi (la_tu_dong=True)

Chay 1 lan:  python -m app.tien_ich.iot_gia_lap
Chay lap:    python -m app.tien_ich.iot_gia_lap --lap 60
"""

import argparse
import random
import time
from datetime import date

from app.co_so_du_lieu.ket_noi import SessionLocal, kiem_tra_ket_noi
from app.mo_hinh.cong_to import CongTo, LoaiCongTo
from app.luan_ly.xu_ly_chi_so import lay_chi_so_moi_nhat, tao_chi_so


def _muc_tang(loai: LoaiCongTo) -> int:
    """Muc tang gia lap — chi dung so nguyen."""
    if loai == LoaiCongTo.DIEN:
        # kWh: 1 .. 8
        return random.randint(1, 8)
    # m3 nuoc: 1 hoac 2
    return random.randint(1, 2)


def doc_va_ghi_mot_cong_to(db, cong_to: CongTo) -> str:
    """Doc chi so cu, tang nguyen, ghi chi so moi."""
    cu = lay_chi_so_moi_nhat(db, cong_to.ma_cong_to)
    if cu:
        chi_so_cu = int(float(cu.chi_so_moi))
    else:
        # Lan dau
        chi_so_cu = 1000 if cong_to.loai_cong_to == LoaiCongTo.DIEN else 50

    delta = _muc_tang(cong_to.loai_cong_to)
    chi_so_moi = chi_so_cu + delta

    try:
        tao_chi_so(
            db,
            ma_cong_to=cong_to.ma_cong_to,
            chi_so_cu=float(chi_so_cu),
            chi_so_moi=float(chi_so_moi),
            ngay_ghi=date.today(),
            la_tu_dong=True,
            la_uoc_tinh=False,
            da_chot=False,
            ghi_chu="IoT gia lap tu dong",
        )
        return (
            f"OK {cong_to.ma_thiet_bi} ({cong_to.loai_cong_to.value}): "
            f"{chi_so_cu} -> {chi_so_moi} (+{delta})"
        )
    except ValueError as e:
        return f"BO QUA {cong_to.ma_thiet_bi}: {e}"


def chay_mot_vong() -> None:
    """Quet tat ca cong to dang hoat dong va ghi chi so."""
    if not kiem_tra_ket_noi():
        print("Khong ket noi duoc database.")
        return

    db = SessionLocal()
    try:
        ds = (
            db.query(CongTo)
            .filter(CongTo.dang_hoat_dong == True)  # noqa: E712
            .all()
        )
        if not ds:
            print("Khong co cong to nao dang hoat dong.")
            return

        print(f"--- IoT gia lap: {len(ds)} cong to ---")
        for ct in ds:
            print(doc_va_ghi_mot_cong_to(db, ct))
        print("--- Xong 1 vong ---\n")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="IoT gia lap cong to")
    parser.add_argument(
        "--lap",
        type=int,
        default=0,
        help="Lap lai moi N giay (0 = chay 1 lan)",
    )
    args = parser.parse_args()

    if args.lap <= 0:
        chay_mot_vong()
        return

    print(f"Che do lap moi {args.lap} giay. Ctrl+C de dung.")
    try:
        while True:
            chay_mot_vong()
            time.sleep(args.lap)
    except KeyboardInterrupt:
        print("\nDa dung IoT gia lap.")


if __name__ == "__main__":
    main()