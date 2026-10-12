import re
from typing import List, Dict, Optional, Any, Tuple
from app.models.ktp_response import KTPParsedData
from app.services.age_validator import parse_indonesian_date_string, parse_birthdate_from_nik

# Kamus konversi karakter OCR yang sering tertukar pada digit NIK
DIGIT_FIX_MAP = {
    'O': '0', 'o': '0', 'D': '0', 'Q': '0',
    'I': '1', 'i': '1', 'l': '1', '|': '1', '!': '1', 'L': '1',
    'Z': '2', 'z': '2',
    'S': '5', 's': '5',
    'b': '6', 'G': '6',
    'B': '8',
    'q': '9', 'g': '9'
}

def clean_ocr_text(text: str) -> str:
    """Membersihkan karakter aneh dan spasi berlebih pada teks OCR."""
    if not text:
        return ""
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    return text.strip()

def fix_nik_string(raw_candidate: str) -> Optional[str]:
    """
    Memperbaiki kesalahan baca OCR pada 16 digit NIK.
    Contoh: '3l7lO1230495OOOl' -> '3171012304950001'
    """
    candidate = re.sub(r"[^a-zA-Z0-9]", "", raw_candidate)
    fixed = [DIGIT_FIX_MAP.get(ch, ch) for ch in candidate]
    fixed_str = "".join(fixed)
    digits_only = re.sub(r"\D", "", fixed_str)
    
    match = re.search(r"\d{16}", digits_only)
    if match:
        return match.group(0)
    
    if len(digits_only) == 16:
        return digits_only
        
    return None

def extract_field_value(line: str, pattern: str) -> Optional[str]:
    """Mengambil nilai setelah titik dua ':' atau setelah kata kunci pola."""
    match = re.search(pattern, line, re.IGNORECASE)
    if not match:
        return None
    val = line[match.end():].strip()
    val = re.sub(r"^[:\-=\|;,\s]+", "", val).strip()
    return val if val else None

def parse_ktp_lines(lines: List[str]) -> KTPParsedData:
    """
    Parser cerdas untuk mengekstrak field KTP dari daftar baris teks OCR.
    Mendukung format satu baris, label & nilai terpisah, serta urutan baris OCR.
    """
    data = KTPParsedData()
    cleaned_lines = [clean_ocr_text(l) for l in lines if clean_ocr_text(l)]
    full_text = " \n ".join(cleaned_lines)
    full_upper = full_text.upper()

    # 1. Ekstrak Provinsi & Kabupaten/Kota
    for line in cleaned_lines[:6]:
        upper_line = line.upper()
        if "PROVINSI" in upper_line or "PAOVINSI" in upper_line:
            data.provinsi = re.sub(r"^.*(PROVINSI|PAOVINSI)", "PROVINSI", upper_line).strip()
        elif "KOTA" in upper_line or "KABUPATEN" in upper_line:
            match = re.search(r"(KOTA|KABUPATEN)\s+[A-Z\s]+", upper_line)
            if match:
                data.kabupaten_kota = match.group(0).strip()

    # 2. Ekstrak NIK
    for i, line in enumerate(cleaned_lines):
        if re.search(r"\bNIK\b", line, re.IGNORECASE):
            val = extract_field_value(line, r"\bNIK\b")
            nik_clean = fix_nik_string(val) if val else None
            if nik_clean:
                data.nik = nik_clean
                break
            if i + 1 < len(cleaned_lines):
                nik_next = fix_nik_string(cleaned_lines[i + 1])
                if nik_next:
                    data.nik = nik_next
                    break

    # Fallback pencarian 16 digit di seluruh baris teks
    if not data.nik:
        nik_match = re.search(r"\b\d{16}\b", full_text)
        if nik_match:
            data.nik = nik_match.group(0)
        else:
            for line in cleaned_lines:
                cand = fix_nik_string(line)
                if cand:
                    data.nik = cand
                    break

    # 3. Ekstrak Nama
    for i, line in enumerate(cleaned_lines):
        if re.search(r"\b(Nama|Namo)\b", line, re.IGNORECASE) and not data.nama:
            val = extract_field_value(line, r"\b(Nama|Namo)\b")
            if val:
                data.nama = re.sub(r"[0-9:;]", "", val).strip()
            elif i + 1 < len(cleaned_lines):
                next_val = cleaned_lines[i + 1].strip()
                if not any(k in next_val.upper() for k in ["TEMPAT", "LAHIR", "NIK", "ALAMAT", "JENIS"]):
                    data.nama = re.sub(r"[0-9:;]", "", next_val).strip()

    # 4. Ekstrak Tempat & Tanggal Lahir
    for i, line in enumerate(cleaned_lines):
        if re.search(r"(Tempat/Tgl Lahir|Tempat\s*/?\s*Tgl|Tgl Lahir|Tempat Tgl)", line, re.IGNORECASE) and not data.tanggal_lahir:
            val = extract_field_value(line, r"(Tempat/Tgl Lahir|Tempat\s*/?\s*Tgl|Tgl Lahir|Tempat Tgl)")
            if not val and i + 1 < len(cleaned_lines):
                val = cleaned_lines[i + 1].strip()

            if val:
                if "," in val:
                    parts = val.split(",", 1)
                    data.tempat_lahir = parts[0].strip()
                    date_part = parts[1].strip()
                else:
                    date_part = val

                parsed_date = parse_indonesian_date_string(date_part)
                if parsed_date:
                    data.tanggal_lahir = parsed_date.strftime("%Y-%m-%d")
                    if not data.tempat_lahir and not "," in val:
                        m_date = re.search(r"\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}", val)
                        if m_date:
                            data.tempat_lahir = val[:m_date.start()].strip()

    # 5. Jenis Kelamin & Golongan Darah
    if "LAKI" in full_upper:
        data.jenis_kelamin = "LAKI-LAKI"
    elif "PEREMPUAN" in full_upper:
        data.jenis_kelamin = "PEREMPUAN"

    gol_match = re.search(r"(Gol\.?\s*Darah|Darah)\s*[:\s]*([ABO0\-]+)", full_text, re.IGNORECASE)
    if gol_match:
        data.golongan_darah = gol_match.group(2).upper().replace("0", "O")

    # 6. Alamat
    for i, line in enumerate(cleaned_lines):
        upper = line.upper()
        if re.search(r"\bAlamat\b", line, re.IGNORECASE) and not data.alamat:
            val = extract_field_value(line, r"\bAlamat\b")
            if val:
                data.alamat = val
            else:
                # Cek baris berikutnya atau sebelumnya (jika baris sebelumnya adalah jalan)
                if i + 1 < len(cleaned_lines) and not any(k in cleaned_lines[i+1].upper() for k in ["RT", "RW", "KEL", "DESA"]):
                    data.alamat = re.sub(r"^[:\-;\s]+", "", cleaned_lines[i + 1]).strip()
                elif i > 0 and any(k in cleaned_lines[i-1].upper() for k in ["JL", "JALAN", "DUSUN", "KP"]):
                    data.alamat = re.sub(r"^[:\-;\s]+", "", cleaned_lines[i - 1]).strip()

    # Fallback Alamat jika belum ditemukan: cari baris yang dimulai dengan JL / JALAN
    if not data.alamat:
        for line in cleaned_lines:
            if re.match(r"^(JL|JALAN|DUSUN|KP)\b", line.upper().strip()):
                data.alamat = re.sub(r"^[:\-;\s]+", "", line).strip()
                break

    # 7. RT / RW
    for line in cleaned_lines:
        rt_match = re.search(r"\b(\d{2,3})\s*[/,.]\s*(\d{2,3})\b", line)
        if rt_match:
            data.rt_rw = f"{rt_match.group(1)}/{rt_match.group(2)}"
            break

    # 8. Kel/Desa
    for i, line in enumerate(cleaned_lines):
        if re.search(r"(Kel/Desa|Kelurahan|KeVDesa|Desa)", line, re.IGNORECASE) and not data.kel_desa:
            val = extract_field_value(line, r"(Kel/Desa|Kelurahan|KeVDesa|Desa)")
            if val:
                data.kel_desa = val
            elif i + 1 < len(cleaned_lines):
                val_next = re.sub(r"^[:\-;\s]+", "", cleaned_lines[i + 1]).strip()
                if not any(k in val_next.upper() for k in ["KECAMATAN", "AGAMA", "STATUS"]):
                    data.kel_desa = val_next

    # 9. Kecamatan
    for i, line in enumerate(cleaned_lines):
        if re.search(r"\bKecamatan\b", line, re.IGNORECASE) and not data.kecamatan:
            val = extract_field_value(line, r"\bKecamatan\b")
            if val:
                data.kecamatan = val
            elif i + 1 < len(cleaned_lines):
                val_next = re.sub(r"^[:\-;\s]+", "", cleaned_lines[i + 1]).strip()
                if not any(k in val_next.upper() for k in ["AGAMA", "STATUS", "PEKERJAAN"]):
                    data.kecamatan = val_next

    # 10. Agama
    for ag in ["ISLAM", "KRISTEN", "KATOLIK", "KATHOLIK", "HINDU", "BUDDHA", "KONGHUCU"]:
        if ag in full_upper:
            data.agama = "KATOLIK" if "KATHOLIK" in ag else ag
            break

    # 11. Status Perkawinan
    if "BELUM KAWIN" in full_upper:
        data.status_perkawinan = "BELUM KAWIN"
    elif "CERAI HIDUP" in full_upper:
        data.status_perkawinan = "CERAI HIDUP"
    elif "CERAI MATI" in full_upper:
        data.status_perkawinan = "CERAI MATI"
    elif "KAWIN" in full_upper:
        data.status_perkawinan = "KAWIN"

    # 12. Pekerjaan
    for job in [
        "KARYAWAN SWASTA", "PEGAWAI NEGERI SIPIL", "PNS", "WIRASWASTA",
        "PELAJAR/MAHASISWA", "PELAJAR", "MAHASISWA", "BURUH HARIAN LEPAS",
        "MENGURUS RUMAH TANGGA", "BELUM/TIDAK BEKERJA", "TIDAK BEKERJA",
        "TENTARA NASIONAL INDONESIA", "TNI", "KEPOLISIAN", "POLRI",
        "DOKTER", "GURU", "DOSEN", "PEDAGANG", "PETANI"
    ]:
        if job in full_upper:
            data.pekerjaan = job
            break
            
    if not data.pekerjaan:
        for i, line in enumerate(cleaned_lines):
            if re.search(r"\bPekerjaan\b", line, re.IGNORECASE):
                val = extract_field_value(line, r"\bPekerjaan\b")
                if val:
                    data.pekerjaan = val
                elif i + 1 < len(cleaned_lines):
                    data.pekerjaan = re.sub(r"^[:\-;\s]+", "", cleaned_lines[i + 1]).strip()

    # 13. Kewarganegaraan
    if "WNI" in full_upper:
        data.kewarganegaraan = "WNI"
    elif "WNA" in full_upper:
        data.kewarganegaraan = "WNA"

    # 14. Berlaku Hingga
    if "SEUMUR" in full_upper or "SEUMURHIDUP" in full_upper:
        data.berlaku_hingga = "SEUMUR HIDUP"
    else:
        for line in cleaned_lines:
            if re.search(r"Berlaku", line, re.IGNORECASE):
                val = extract_field_value(line, r"Berlaku\s*(Hingga)?")
                if val:
                    data.berlaku_hingga = val

    # Cross-fill tanggal lahir & jenis kelamin dari NIK jika belum terdeteksi dari teks
    if data.nik:
        nik_info = parse_birthdate_from_nik(data.nik)
        if nik_info:
            bdate, gender = nik_info
            if not data.tanggal_lahir:
                data.tanggal_lahir = bdate.strftime("%Y-%m-%d")
            if not data.jenis_kelamin:
                data.jenis_kelamin = gender

    return data
