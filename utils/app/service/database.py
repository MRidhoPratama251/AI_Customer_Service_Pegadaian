# app/service/database.py

from app.models.db_models import Base, engine, Order
from app.service.ai_checker import model_checker
from sqlalchemy.orm import Session
import json

def init_db():
    Base.metadata.create_all(bind=engine)


def insert_order(
    data: str,
    session: Session
):
    validation = model_checker(data)
    #validation = "{ \"status\" : \"valid\", \"message\" : \"Data valid\"}"
    print(f"DEBUG : {validation}")
    try:
        validation_json = json.loads(validation)
    except Exception:
        raise Exception("Invalid JSON format")

    if validation_json["status"] == "invalid":
        #raise Exception(validation_json["message"])
        print(f"DEBUG : {validation_json}")
        return validation_json


    if validation_json["status"] == "valid":
        try:
            data = json.loads(data)
            
        except Exception:
            raise Exception("Invalid JSON format")
        
        try:
            peel = data["dataOrder"]
            data_order = []
            for d in peel:
                order = Order(
                    id_percakapan=d['id_percakapan'],
                    nama_customer=d['nama_customer'],
                    jenis_barang=d['jenis_barang'],
                    nama_barang=d['nama_barang'],
                    jumlah_barang=d['jumlah_barang'],
                    estimasi_nilai_barang=d['estimasi_nilai_barang'],
                    wilayah=d['wilayah'],
                    email=d['email'],
                    status="On Process"
                )

                session.add(order)
                session.commit()

                data_order.append({
                    "id" : order.id,
                    "status" : order.status
                })
            
            # session.commit()
            session.refresh(order)

            

            return data_order

        except Exception:
            session.rollback()
            raise
