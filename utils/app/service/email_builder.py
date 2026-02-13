import yagmail
from dotenv import load_dotenv
import os
from hashids import Hashids
import hashlib
import base64
from pathlib import Path

# Load .env from app directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
APPS_KEY = os.getenv("APPS_KEY")


def generate_short_id(input_string: str, salt: str = APPS_KEY):
    full_string = input_string + salt
    hash_obj = hashlib.sha256(full_string.encode())
    short_id = base64.urlsafe_b64encode(hash_obj.digest()).decode()
    
    return short_id[:6]



def send_email(id_percakapan, email, nama_customer, nama_barang, jumlah_barang, estimasi_nilai_barang, wilayah, jenis_barang):
    if not EMAIL_USER or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_USER and EMAIL_PASSWORD must be set in .env file")
        
    yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASSWORD)

    kode_unik = generate_short_id(input_string=str(id_percakapan+"_"+nama_customer+"_"+nama_barang+"_"+str(jumlah_barang)+"_"+jenis_barang+"_"+wilayah))
    body = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h2 style="color: #2c3e50; text-align: center;">Verifikasi Pemesanan</h2>
        <p>Halo <strong>{nama_customer}</strong>,</p>
        <p>Terima kasih telah melakukan pemesanan. Berikut adalah rincian pesanan Anda:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Nama Barang</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{nama_barang}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Jenis Barang</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{jenis_barang}</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Jumlah</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{jumlah_barang}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Wilayah</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{wilayah}</td>
        </tr>
        </table>

        <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; border: 1px dashed #3498db;">
        <p style="margin: 0; font-size: 14px; color: #2980b9;">Gunakan kode unik di bawah ini untuk verifikasi ke Admin Telegram:</p>
        <h1 style="margin: 10px 0; letter-spacing: 5px; color: #2c3e50;">{kode_unik}</h1>
        </div>

        <p style="font-size: 12px; color: #7f8c8d; margin-top: 20px;">
        * Kode unik ini berlaku selama <strong>24 jam</strong>.<br>
        * Abaikan email ini jika Anda tidak merasa melakukan pemesanan.
        </p>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="text-align: center; font-size: 12px; color: #bdc3c7;">Otomatis dikirim oleh Sistem Layanan Kami</p>
    </div>
    </body>
</html>
"""

    yag.send(to = email, 
            subject = "Verifikasi Pemesanan", 
            contents = body)

    return {
        "kode_unik" : kode_unik
    }