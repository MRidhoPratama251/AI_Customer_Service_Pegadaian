# app/models/scheme.py

from pydantic import BaseModel, HttpUrl
from typing import Optional

class ScrapeRequest(BaseModel):
    url: list[HttpUrl]

class ScrapeResponse(BaseModel):
    result: list[dict]

class OrderRequest(BaseModel):
    id_percakapan: str
    nama_customer: str
    jenis_barang: str
    nama_barang: str
    jumlah_barang: int
    estimasi_nilai_barang: float
    wilayah: str
    email: str
    status: Optional[str] = "On Process"

class OrderPayload(BaseModel):
    dataOrder: str

# class OrderResponse(BaseModel):
#     result: list[dict]
