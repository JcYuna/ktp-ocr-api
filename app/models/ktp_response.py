from typing import Optional, List
from pydantic import BaseModel, Field

class KTPParsedData(BaseModel):
    nik: Optional[str] = Field(None, description="Nomor Induk Kependudukan (16 digit)")
    nama: Optional[str] = Field(None, description="Nama lengkap pemilik KTP")
    tempat_lahir: Optional[str] = Field(None, description="Tempat kelahiran")
    tanggal_lahir: Optional[str] = Field(None, description="Tanggal lahir (format YYYY-MM-DD)")
    jenis_kelamin: Optional[str] = Field(None, description="LAKI-LAKI atau PEREMPUAN")
    golongan_darah: Optional[str] = Field(None, description="Golongan darah (A, B, AB, O, atau -)")
    alamat: Optional[str] = Field(None, description="Alamat lengkap")
    rt_rw: Optional[str] = Field(None, description="Nomor RT/RW")
    kel_desa: Optional[str] = Field(None, description="Kelurahan / Desa")
    kecamatan: Optional[str] = Field(None, description="Kecamatan")
    agama: Optional[str] = Field(None, description="Agama")
    status_perkawinan: Optional[str] = Field(None, description="Status perkawinan")
    pekerjaan: Optional[str] = Field(None, description="Pekerjaan")
    kewarganegaraan: Optional[str] = Field(None, description="Kewarganegaraan (WNI/WNA)")
    berlaku_hingga: Optional[str] = Field(None, description="Masa berlaku KTP")
    provinsi: Optional[str] = Field(None, description="Provinsi penerbit KTP")
    kabupaten_kota: Optional[str] = Field(None, description="Kabupaten atau Kota penerbit KTP")

class AgeValidationResult(BaseModel):
    is_valid: bool = Field(..., description="True jika usia >= 18 tahun, False jika di bawah 18 tahun atau tidak dapat ditentukan")
    is_above_18: bool = Field(..., description="Alias untuk validasi usia >= 18")
    age: Optional[int] = Field(None, description="Usia dalam tahun yang berhasil dihitung")
    birth_date: Optional[str] = Field(None, description="Tanggal lahir terverifikasi (YYYY-MM-DD)")
    validation_status: str = Field(..., description="VALID (>=18), UNDERAGE (<18), INVALID_DATE, atau NOT_FOUND")
    message: str = Field(..., description="Penjelasan hasil validasi usia")
    age_source: str = Field(..., description="Sumber penentuan usia: 'TANGGAL_LAHIR_TEXT', 'NIK_ENCODED', 'BOTH_VERIFIED', atau 'NONE'")

class KTPDetectionResponse(BaseModel):
    success: bool = Field(..., description="Status keberhasilan pemrosesan OCR")
    data: KTPParsedData = Field(..., description="Data teks KTP yang berhasil diekstrak")
    age_validation: AgeValidationResult = Field(..., description="Hasil validasi umur >= 18 tahun")
    raw_texts: List[str] = Field(default_factory=list, description="Seluruh teks mentah yang terdeteksi oleh OCR")
    processing_time_ms: float = Field(..., description="Waktu pemrosesan dalam milidetik")

class Base64ImageRequest(BaseModel):
    image_base64: str = Field(..., description="String gambar KTP terenkode Base64 (dengan atau tanpa prefix data:image/...)")

class DirectAgeValidationRequest(BaseModel):
    nik: Optional[str] = Field(None, description="NIK 16 digit untuk verifikasi umur langsung")
    tanggal_lahir: Optional[str] = Field(None, description="Tanggal lahir (contoh: '1995-08-17' atau '17-08-1995')")
