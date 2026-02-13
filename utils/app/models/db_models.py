# app/models/db_models.py

from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os

# Default to local if env not set (for backward compatibility)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    id_percakapan = Column(String, nullable=False)
    nama_customer = Column(String, nullable=False)
    jenis_barang = Column(String, nullable=False)
    nama_barang = Column(String, nullable=False)
    jumlah_barang = Column(Integer, nullable=False)
    estimasi_nilai_barang = Column(Numeric(15, 2), nullable=False)
    wilayah = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship to verifications
    verifications = relationship("Verifikasi", back_populates="order")


class Verifikasi(Base):
    __tablename__ = "verifications"

    id_verifikasi = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey('orders.id'))
    
    kode_unik = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    order = relationship("Order", back_populates="verifications")  