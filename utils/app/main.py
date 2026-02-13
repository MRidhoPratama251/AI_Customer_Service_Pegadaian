# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.scheme import ScrapeRequest, ScrapeResponse, OrderRequest, OrderPayload
from app.service.scraper import scrape_url
from app.service.database import insert_order, init_db
from app.models.db_models import SessionLocal
from app.service.email_builder import send_email

init_db()



from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Simple Web Scraper API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5678",
        r"https://.*\.ngrok-free\.app",
        "http://localhost:5173", # Dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/scrape", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest):
    try:
        result = scrape_url(
            url=request.url
        )
        return ScrapeResponse(
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/order")
def order(request: OrderPayload):
    db= SessionLocal()
    
    try:
        print(f"DEBUG : {request.dataOrder}")
        #for req in request.dataOrder:
        result = insert_order(
            data = request.dataOrder,
            session = db
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    finally:
        db.close()

from app.router import router as dashboard_router
app.include_router(dashboard_router)

import asyncio
from app.scheduler import cleanup_expired_verifications

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_verifications())


static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

