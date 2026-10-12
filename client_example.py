"""
Contoh integrasi API OCR KTP & Validasi Usia menggunakan Python (requests).
Cocok untuk digunakan di backend project lain (Django, Flask, FastAPI, Celery, script, dll).
"""

import requests
import json
import base64

API_BASE_URL = "http://127.0.0.1:8000"

def extract_ktp_file(image_path: str, min_age: int = 18):
    """
    Ekstraksi teks KTP dan validasi umur dengan mengunggah file gambar langsung.
    """
    url = f"{API_BASE_URL}/api/v1/ktp/extract"
    params = {"min_age": min_age}
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/jpeg")}
        response = requests.post(url, files=files, params=params)
        
    if response.status_code == 200:
        result = response.json()
        print("=== HASIL EKSTRAKSI KTP ===")
        print(f"NIK           : {result['data']['nik']}")
        print(f"Nama          : {result['data']['nama']}")
        print(f"Tanggal Lahir : {result['data']['tanggal_lahir']}")
        print(f"Jenis Kelamin : {result['data']['jenis_kelamin']}")
        print(f"Alamat        : {result['data']['alamat']}")
        print("---------------------------")
        print(f"Usia          : {result['age_validation']['age']} tahun")
        print(f"Valid (>= 18) : {result['age_validation']['is_valid']}")
        print(f"Status        : {result['age_validation']['validation_status']}")
        print(f"Keterangan    : {result['age_validation']['message']}")
        return result
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def extract_ktp_base64(image_path: str, min_age: int = 18):
    """
    Ekstraksi teks KTP dan validasi umur menggunakan payload Base64 JSON.
    Berguna untuk aplikasi web/mobile yang memproses foto di sisi frontend terlebih dahulu.
    """
    url = f"{API_BASE_URL}/api/v1/ktp/extract-base64"
    params = {"min_age": min_age}

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    payload = {"image_base64": encoded}
    response = requests.post(url, json=payload, params=params)
    return response.json()

def validate_age_only(nik: str = None, tanggal_lahir: str = None, min_age: int = 18):
    """
    Validasi usia langsung tanpa gambar (input manual NIK atau tanggal lahir).
    """
    url = f"{API_BASE_URL}/api/v1/ktp/validate-age"
    payload = {"nik": nik, "tanggal_lahir": tanggal_lahir}
    params = {"min_age": min_age}

    response = requests.post(url, json=payload, params=params)
    return response.json()

if __name__ == "__main__":
    sample_file = "sample_images/sample_ktp_adult.jpg"
    print(f"Mengirimkan {sample_file} ke API...")
    extract_ktp_file(sample_file)
