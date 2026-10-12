# Indonesian KTP OCR & Age Validation API 🇮🇩

API RESTful performa tinggi berbasis **FastAPI** dan **EasyOCR** untuk mengekstrak data teks dari foto KTP (Kartu Tanda Penduduk) Indonesia, sekaligus melakukan **validasi otomatis batas usia (minimal 18 tahun)**. 

Dirancang modular dan siap diintegrasikan (*ready-to-integrate*) ke berbagai project: Web Apps (React/Vue/Next.js), Mobile Apps (Flutter/React Native), Microservices, atau Backend (Node.js, Python, PHP/Laravel, Go, Java).

---

## 🌟 Fitur Utama

1. **Ekstraksi Lengkap Data KTP**:
   - `NIK` (Nomor Induk Kependudukan 16 digit dengan normalisasi kesalahan OCR pada angka).
   - `Nama`, `Tempat Lahir`, `Tanggal Lahir`.
   - `Jenis Kelamin`, `Golongan Darah`.
   - `Alamat`, `RT/RW`, `Kel/Desa`, `Kecamatan`.
   - `Agama`, `Status Perkawinan`, `Pekerjaan`.
   - `Kewarganegaraan`, `Berlaku Hingga`, `Provinsi`, `Kabupaten/Kota`.
2. **Validasi Batas Usia Pintar (>= 18 Tahun)**:
   - Validasi usia secara presisi berdasarkan selisih hari & bulan dengan tanggal saat ini.
   - **Cross-Verification dengan NIK**: Mengekstrak tanggal lahir & gender terenkode dari digit 7-12 NIK (termasuk aturan wanita: tanggal lahir ditambah 40).
   - Menyelesaikan ambiguitas OCR teks secara otomatis jika teks pudar atau memiliki typo.
   - Memberikan flag `is_valid` (`true` jika usia >= 18 tahun, `false` jika di bawah 18 tahun).
3. **Fleksibilitas Input**:
   - Mendukung **Upload File langsung** (`multipart/form-data`) untuk format JPG, JPEG, PNG, WEBP.
   - Mendukung **JSON Base64** (`POST /extract-base64`) untuk integrasi frontend/mobile yang mengolah gambar di client.
   - Endpoint **Direct Age Validation** (`POST /validate-age`) untuk verifikasi umur langsung dari teks/NIK tanpa perlu gambar.
4. **Prapemrosesan Gambar KTP (OpenCV & CLAHE)**:
   - Dynamic downscaling untuk efisiensi kecepatan.
   - Contrast Limited Adaptive Histogram Equalization (CLAHE) pada kanal Luminance agar teks kontras tajam di atas latar belakang biru KTP.
5. **Interactive OpenAPI / Swagger Docs**:
   - UI dokumentasi interaktif bawaan di `http://localhost:8000/docs`.

---

## 🚀 Cara Menjalankan

### Cara 1: Menjalankan Langsung dengan Python (Lokal)

1. Pastikan Python 3.10+ telah terpasang.
2. Pasang pustaka dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server API:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Buka browser pada [http://localhost:8000/docs](http://localhost:8000/docs) untuk mencoba API interaktif melalui Swagger UI.

### Cara 2: Menjalankan dengan Docker / Docker Compose

```bash
docker-compose up -d --build
```
API akan langsung berjalan di port `8000`.

---

## 📡 Endpoint API

### 1. `POST /api/v1/ktp/extract`
Upload foto KTP via `multipart/form-data`.

**Query Parameters:**
- `min_age` *(optional, default: 18)*: Batas minimal usia yang dinyatakan valid.

**Contoh cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/ktp/extract?min_age=18" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@foto_ktp.jpg"
```

**Contoh Response JSON:**
```json
{
  "success": true,
  "data": {
    "nik": "3171012304950001",
    "nama": "BUDI SANTOSO",
    "tempat_lahir": "JAKARTA",
    "tanggal_lahir": "1995-04-23",
    "jenis_kelamin": "LAKI-LAKI",
    "golongan_darah": "O",
    "alamat": "JL. SUDIRMAN NO. 45",
    "rt_rw": "005/002",
    "kel_desa": "SENAYAN",
    "kecamatan": "KEBAYORAN BARU",
    "agama": "ISLAM",
    "status_perkawinan": "BELUM KAWIN",
    "pekerjaan": "KARYAWAN SWASTA",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP",
    "provinsi": "PROVINSI DKI JAKARTA",
    "kabupaten_kota": "KOTA JAKARTA SELATAN"
  },
  "age_validation": {
    "is_valid": true,
    "is_above_18": true,
    "age": 31,
    "birth_date": "1995-04-23",
    "validation_status": "VALID",
    "message": "Usia terverifikasi 31 tahun (Memenuhi syarat: usia >= 18 tahun).",
    "age_source": "BOTH_VERIFIED"
  },
  "raw_texts": [
    "PROVINSI DKI JAKARTA",
    "KOTA JAKARTA SELATAN",
    "NIK : 3171012304950001",
    ...
  ],
  "processing_time_ms": 3319.72
}
```

*Jika usia di bawah 18 tahun:*
```json
{
  "age_validation": {
    "is_valid": false,
    "is_above_18": false,
    "age": 14,
    "birth_date": "2012-05-12",
    "validation_status": "UNDERAGE",
    "message": "Usia terverifikasi 14 tahun (TIDAK MEMENUHI SYARAT: usia di bawah 18 tahun).",
    "age_source": "BOTH_VERIFIED"
  }
}
```

---

### 2. `POST /api/v1/ktp/extract-base64`
Kirim foto KTP dalam string Base64 JSON.

**Request Body:**
```json
{
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

---

### 3. `POST /api/v1/ktp/validate-age`
Validasi usia langsung tanpa gambar (berdasarkan NIK atau teks tanggal lahir).

**Request Body:**
```json
{
  "nik": "3171012304950001",
  "tanggal_lahir": "1995-04-23"
}
```

---

## 💻 Contoh Integrasi di Berbagai Bahasa

### 1. Python (`client_example.py`)
```python
import requests

with open("foto_ktp.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/ktp/extract",
        files={"file": ("ktp.jpg", f, "image/jpeg")}
    )

res = response.json()
if res["age_validation"]["is_valid"]:
    print(f"Valid! Usia: {res['age_validation']['age']} tahun")
else:
    print(f"Ditolak: {res['age_validation']['message']}")
```

### 2. JavaScript / Node.js / React (`client_example.js`)
```javascript
const formData = new FormData();
formData.append('file', fileBlob, 'ktp.jpg');

const res = await fetch('http://localhost:8000/api/v1/ktp/extract?min_age=18', {
  method: 'POST',
  body: formData
});
const data = await res.json();
console.log('Status Validasi:', data.age_validation.is_valid);
```

### 3. PHP / Laravel
```php
$response = Http::attach(
    'file', file_get_contents($pathToFile), 'ktp.jpg'
)->post('http://localhost:8000/api/v1/ktp/extract?min_age=18');

$result = $response->json();
if ($result['age_validation']['is_valid']) {
    // Pengguna berumur >= 18 tahun
}
```

---

## 🧪 Menjalankan Unit Tests

```bash
# Test fungsi penguraian tanggal & logika validasi umur
python -m tests.test_age_validator

# Test ekstraksi dan parsing field KTP
python -m tests.test_parser
```
Semua test lolos 100%.
