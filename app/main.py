from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.ktp import router as ktp_router
from app.services.ocr_engine import get_ocr_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload OCR engine saat server mulai (menghindari delay saat request pertama masuk)
    print("Memuat model EasyOCR ke memori...")
    get_ocr_engine()
    print("Model OCR berhasil dimuat & siap menerima request.")
    yield
    print("Mematikan server...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API RESTful untuk ekstraksi teks KTP (OCR) dan validasi otomatis batas usia (minimal 18 tahun). Siap diintegrasikan ke berbagai project (Web, Mobile, Microservices).",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Konfigurasi CORS agar API dapat dipanggil dari berbagai domain/aplikasi frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hubungkan router
app.include_router(ktp_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Selamat datang di API OCR KTP & Validasi Usia",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/ktp/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
