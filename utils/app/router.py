from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.db_models import SessionLocal, Order, Verifikasi
from app.service.email_builder import send_email
import logging

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    """
    Fetch all active orders.

    Returns:
        list: List of orders with status 'On Process' or 'Verified'.
    """
    # Fetch orders that are "On Process" or potentially others if needed for history
    # Req says: "melihat daftar customer yang masih on process"
    # But later says: "jika status sudah berubah menjadi verified maka tombol send_verification untuk email akan disabled"
    # So we probably want to see Verified ones too to disable the button.
    # Let's return all for now or filter by 'On Process' AND 'Verified' if we want to show history.
    # Logic: Show active orders (On Process) and recently verified ones. 
    # For now, let's fetch 'On Process' and 'Verified'.
    orders = db.query(Order).filter(Order.status.in_(["On Process", "On Verification", "Verified"])).all()
    return orders

@router.post("/verification/{order_id}")
def send_verification_email(order_id: int, db: Session = Depends(get_db)):
    """
    Send verification email to the customer of a specific order.

    Args:
        order_id (int): IThe ID of the order.
        db (Session): Database session.

    Returns:
        dict: Message and generated unique code.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "Verified":
        raise HTTPException(status_code=400, detail="Order already verified")
    
    if order.status == "On Verification":
        raise HTTPException(status_code=400, detail="Verification email already sent")

    try:
        email_result = send_email(
            id_percakapan=order.id_percakapan,
            email=order.email,
            nama_customer=order.nama_customer,
            nama_barang=order.nama_barang,
            jumlah_barang=order.jumlah_barang,
            estimasi_nilai_barang=order.estimasi_nilai_barang,
            wilayah=order.wilayah,
            jenis_barang=order.jenis_barang
        )
        
        # Check if verification entry already exists
        existing_verification = db.query(Verifikasi).filter(Verifikasi.id_order == order.id).first()    

        if not existing_verification:
            new_verification = Verifikasi(
                id_order=order.id,
                kode_unik=email_result['kode_unik']
            )
            db.add(new_verification)
            order.status = "On Verification"
            db.add(order)    
        
            db.commit()
            return {"message": "Email sent", "kode_unik": email_result['kode_unik']}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.delete("/order/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Delete an order and its verification record if exists.

    Args:
        order_id (int): The ID of the order to delete.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Also delete from verifications if exists
    verification = db.query(Verifikasi).filter(Verifikasi.id_order == order.id).first()
    if verification:
        db.delete(verification)
        
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}

from pydantic import BaseModel

class VerificationPayload(BaseModel):
    kode_unik: str

@router.post("/verify")
def verify_code(payload: VerificationPayload, db: Session = Depends(get_db)):
    """
    Verify the unique code received from the customer.
    Called by the AI/Bot.

    Args:
        payload (VerificationPayload): Contains the 'kode_unik'.
    
    Returns:
        dict: Success message and order ID.
    """
    # Find verification entry
    verification = db.query(Verifikasi).filter(Verifikasi.kode_unik == payload.kode_unik).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Invalid code")
    
    # Update order status using the relationship
    order = verification.order
    
    if order:
        order.status = "Verified"
        db.delete(verification)
        db.commit()
        
        # Optional: Delete verification entry now that it's used? 
        # Requirement says: "jika tidak (verifikasi dalam 1x24 jam), maka kode unik akan dihapus"
        # Doesn't explicitly say delete after success, but usually good practice.
        # But maybe we want to keep record?
        # Let's keep it for now as per "Verifikasi" table definition.
        
        return {"message": "Order verified", "order_id": order.id}
    
    raise HTTPException(status_code=404, detail="Order not found for this code")
