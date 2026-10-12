import time
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, status
from app.config import settings
from app.models.ktp_response import (
    KTPDetectionResponse,
    Base64ImageRequest,
    DirectAgeValidationRequest,
    AgeValidationResult
)
from app.services.image_preprocessor import decode_image_bytes, decode_base64_image
from app.services.ocr_engine import get_ocr_engine
from app.services.ktp_parser import parse_ktp_lines
from app.services.age_validator import validate_ktp_age

router = APIRouter(prefix="/api/v1/ktp", tags=["KTP OCR & Age Validation"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

def validate_image_file_extension(filename: str):
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format file tidak didukung (. {ext}). Gunakan format: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post(
    "/extract",
    response_model=KTPDetectionResponse,
    summary="Deteksi teks KTP & validasi usia >= 18 tahun via File Upload",
    description="Menerima upload foto/gambar KTP (JPEG, PNG, dsb.), mengekstrak seluruh data teks (NIK, Nama, Tanggal Lahir, Alamat, dll.), dan memvalidasi apakah pemilik KTP berumur 18 tahun ke atas."
)
async def extract_ktp_from_file(
    file: UploadFile = File(..., description="File foto KTP"),
    min_age: int = Query(default=18, description="Batas usia minimal (default 18 tahun)")
):
    validate_image_file_extension(file.filename or "")

    start_time = time.time()
    file_bytes = await file.read()
    
    if len(file_bytes) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Ukuran file melebihi batas maksimal {settings.MAX_IMAGE_SIZE_MB} MB."
        )

    image = decode_image_bytes(file_bytes)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gambar tidak valid atau korup. Pastikan file berupa format gambar yang benar."
        )

    # Jalankan OCR
    ocr_engine = get_ocr_engine()
    raw_lines, _ = ocr_engine.extract_text_from_image(image)

    # Parsing field KTP
    ktp_data = parse_ktp_lines(raw_lines)

    # Validasi usia
    age_val = validate_ktp_age(
        text_birth_date=ktp_data.tanggal_lahir,
        nik=ktp_data.nik,
        min_age=min_age
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return KTPDetectionResponse(
        success=True,
        data=ktp_data,
        age_validation=age_val,
        raw_texts=raw_lines,
        processing_time_ms=elapsed_ms
    )

@router.post(
    "/extract-base64",
    response_model=KTPDetectionResponse,
    summary="Deteksi teks KTP & validasi usia >= 18 tahun via Base64 JSON",
    description="Alternatif untuk sistem client/mobile/web yang mengirimkan gambar KTP dalam format string Base64."
)
async def extract_ktp_from_base64(
    request: Base64ImageRequest,
    min_age: int = Query(default=18, description="Batas usia minimal (default 18 tahun)")
):
    start_time = time.time()
    image = decode_base64_image(request.image_base64)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="String Base64 gambar tidak valid atau tidak dapat didekode."
        )

    # Jalankan OCR
    ocr_engine = get_ocr_engine()
    raw_lines, _ = ocr_engine.extract_text_from_image(image)

    # Parsing field KTP
    ktp_data = parse_ktp_lines(raw_lines)

    # Validasi usia
    age_val = validate_ktp_age(
        text_birth_date=ktp_data.tanggal_lahir,
        nik=ktp_data.nik,
        min_age=min_age
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return KTPDetectionResponse(
        success=True,
        data=ktp_data,
        age_validation=age_val,
        raw_texts=raw_lines,
        processing_time_ms=elapsed_ms
    )

@router.post(
    "/validate-age",
    response_model=AgeValidationResult,
    summary="Validasi usia langsung tanpa gambar (dari input NIK / Tanggal Lahir)",
    description="Endpoint ringan untuk memverifikasi apakah seseorang berumur >= 18 tahun berdasarkan NIK 16 digit atau tanggal lahir teks."
)
async def validate_age_direct(
    request: DirectAgeValidationRequest,
    min_age: int = Query(default=18, description="Batas usia minimal (default 18 tahun)")
):
    if not request.nik and not request.tanggal_lahir:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimal masukkan salah satu dari NIK atau Tanggal Lahir."
        )

    age_val = validate_ktp_age(
        text_birth_date=request.tanggal_lahir,
        nik=request.nik,
        min_age=min_age
    )
    return age_val

@router.get("/health", summary="Healthcheck endpoint")
async def health_check():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "min_age_requirement": settings.MINIMUM_AGE_REQUIRED
    }
