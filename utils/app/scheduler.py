import asyncio
from datetime import datetime, timedelta
from app.models.db_models import SessionLocal, Verifikasi, Order
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


"""
Scheduler module for background tasks.
Handles cleanup of expired verification sessions and orders.
"""

async def cleanup_expired_verifications():
    """
    Background task to cleanup expired verifications.
    
    Checks for verifications created more than 24 hours ago.
    If found, deletes the verification record AND the associated order
    as per business requirements.
    
    Runs continuously with a 1-hour sleep interval.
    """
    while True:
        try:
            db = SessionLocal()
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Find expired verifications
            expired_verifications = db.query(Verifikasi).filter(Verifikasi.created_at < cutoff_time).all()
            
            for verification in expired_verifications:
                # Find associated order
                order = db.query(Order).filter(Order.id_percakapan == verification.id_percakapan).first()
                if order:
                    logger.info(f"Deleting expired order: {order.id} (Conversation: {order.id_percakapan})")
                    db.delete(order)
                
                logger.info(f"Deleting expired verification: {verification.id_verifikasi}")
                db.delete(verification)
            
            if expired_verifications:
                db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error in cleanup scheduler: {e}")
            if 'db' in locals():
                db.close()
        
        # Run every hour
        await asyncio.sleep(3600)
