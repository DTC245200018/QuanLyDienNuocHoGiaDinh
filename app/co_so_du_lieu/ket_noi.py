"""
Cau hinh ket noi SQL Server bang SQLAlchemy + pyodbc.
Hien tai chi tao engine, chua tao bang nghiep vu.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.cau_hinh.cai_dat import cai_dat


class Base(DeclarativeBase):
    """Base class cho cac model SQLAlchemy sau nay."""
    pass


def tao_chuoi_ket_noi() -> str:
    """Tao connection string cho SQL Server (Windows Authentication)."""
    driver = cai_dat.db_driver.replace(" ", "+")
    chuoi = (
        f"mssql+pyodbc://@{cai_dat.db_server}/{cai_dat.db_database}"
        f"?driver={driver}"
        f"&Trusted_Connection=yes"
        f"&TrustServerCertificate=yes"
    )
    return chuoi


engine = create_engine(
    tao_chuoi_ket_noi(),
    echo=False,
    pool_pre_ping=True,
    connect_args={"unicode_results": True},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def kiem_tra_ket_noi() -> bool:
    """Kiem tra ket noi toi SQL Server. Tra ve True neu thanh cong."""
    try:
        with engine.connect() as ket_noi:
            ket_noi.execute(text("SELECT 1"))
        return True
    except Exception as loi:
        print(f"Loi ket noi database: {loi}")
        return False