import re
from datetime import date, datetime
from typing import Optional, Tuple
from app.models.ktp_response import AgeValidationResult

# Pemetaan nama bulan bahasa Indonesia ke angka bulan
MONTH_NAMES = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2, "pebruari": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agt": 8, "ags": 8, "agu": 8,
    "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10, "october": 10,
    "november": 11, "nov": 11, "nopember": 11, "nop": 11,
    "desember": 12, "des": 12, "december": 12,
}

def parse_indonesian_date_string(date_str: str) -> Optional[date]:
    """
    Mengurai berbagai variasi format tanggal lahir Indonesia dari teks KTP.
    Contoh input:
    - '17-08-1995'
    - '17/08/1995'
    - '17 08 1995'
    - '17 AGUSTUS 1995'
    - '1995-08-17'
    - '17-08-95'
    """
    if not date_str:
        return None

    cleaned = date_str.strip().lower()
    cleaned = re.sub(r"[,;.]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Cek format dengan nama bulan teks, e.g. "17 agustus 1995"
    text_month_match = re.search(r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{2,4})", cleaned)
    if text_month_match:
        d_val = int(text_month_match.group(1))
        m_str = text_month_match.group(2).lower()
        y_val = int(text_month_match.group(3))
        
        if m_str in MONTH_NAMES:
            m_val = MONTH_NAMES[m_str]
            if y_val < 100:
                cur_yr_short = date.today().year % 100
                y_val = 2000 + y_val if y_val <= cur_yr_short else 1900 + y_val
            try:
                return date(y_val, m_val, d_val)
            except ValueError:
                pass

    # Cek format numerik: YYYY-MM-DD
    iso_match = re.search(r"(\d{4})[-/\s](\d{1,2})[-/\s](\d{1,2})", cleaned)
    if iso_match:
        y_val, m_val, d_val = map(int, iso_match.groups())
        try:
            return date(y_val, m_val, d_val)
        except ValueError:
            pass

    # Cek format numerik umum Indonesia: DD-MM-YYYY atau DD-MM-YY
    dmy_match = re.search(r"(\d{1,2})[-/\s](\d{1,2})[-/\s](\d{2,4})", cleaned)
    if dmy_match:
        d_val, m_val, y_val = map(int, dmy_match.groups())
        if y_val < 100:
            cur_yr_short = date.today().year % 100
            y_val = 2000 + y_val if y_val <= cur_yr_short else 1900 + y_val
        try:
            return date(y_val, m_val, d_val)
        except ValueError:
            pass

    return None

def parse_birthdate_from_nik(nik: str) -> Optional[Tuple[date, str]]:
    """
    Mengekstrak tanggal lahir & jenis kelamin langsung dari struktur NIK 16 digit.
    Digit ke 7-8: Tanggal (pria: 1-31, wanita: 41-71)
    Digit ke 9-10: Bulan (1-12)
    Digit ke 11-12: Tahun 2 digit
    """
    if not nik:
        return None
        
    clean_nik = re.sub(r"[^\d]", "", nik)
    if len(clean_nik) != 16:
        return None

    try:
        raw_day = int(clean_nik[6:8])
        month = int(clean_nik[8:10])
        raw_year = int(clean_nik[10:12])

        if month < 1 or month > 12:
            return None

        # Wanita: tanggal lahir ditambah 40
        if raw_day > 40:
            day = raw_day - 40
            gender = "PEREMPUAN"
        else:
            day = raw_day
            gender = "LAKI-LAKI"

        if day < 1 or day > 31:
            return None

        # Tentukan abad (1900-an atau 2000-an)
        current_year = date.today().year
        cur_yr_short = current_year % 100
        
        # Jika raw_year <= cur_yr_short (misal 00 s/d 26 di tahun 2026),
        # maka tahun lahir adalah abad 2000-an (2000 + raw_year).
        # Jika raw_year > cur_yr_short (misal 27 s/d 99),
        # maka tahun lahir adalah abad 1900-an (1900 + raw_year).
        if raw_year <= cur_yr_short:
            year = 2000 + raw_year
        else:
            year = 1900 + raw_year

        birth_date = date(year, month, day)
        return birth_date, gender
    except (ValueError, IndexError):
        return None

def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> int:
    """
    Menghitung usia secara presisi berdasarkan selisih hari & bulan dengan tanggal acuan.
    """
    if reference_date is None:
        reference_date = date.today()
    
    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def validate_ktp_age(
    text_birth_date: Optional[str] = None,
    nik: Optional[str] = None,
    min_age: int = 18,
    reference_date: Optional[date] = None
) -> AgeValidationResult:
    """
    Validasi utama apakah pemegang KTP berumur minimal min_age (default 18 tahun).
    Mendukung verifikasi silang (cross-verification) antara NIK dan teks Tanggal Lahir.
    """
    if reference_date is None:
        reference_date = date.today()

    parsed_from_text = parse_indonesian_date_string(text_birth_date) if text_birth_date else None
    nik_res = parse_birthdate_from_nik(nik) if nik else None
    parsed_from_nik = nik_res[0] if nik_res else None

    chosen_date: Optional[date] = None
    age_source = "NONE"

    if parsed_from_text and parsed_from_nik:
        if parsed_from_text == parsed_from_nik:
            chosen_date = parsed_from_text
            age_source = "BOTH_VERIFIED"
        elif parsed_from_text.year == parsed_from_nik.year:
            # Tahun sama persis, jika ada beda hari/bulan kemungkinan salah satu typo OCR
            chosen_date = parsed_from_nik
            age_source = "NIK_ENCODED"
        else:
            # Jika teks memiliki 4 digit tahun eksplisit (misal 2012 atau 1995), teks sangat akurat
            chosen_date = parsed_from_text
            age_source = "TANGGAL_LAHIR_TEXT"
    elif parsed_from_text:
        chosen_date = parsed_from_text
        age_source = "TANGGAL_LAHIR_TEXT"
    elif parsed_from_nik:
        chosen_date = parsed_from_nik
        age_source = "NIK_ENCODED"

    if not chosen_date:
        return AgeValidationResult(
            is_valid=False,
            is_above_18=False,
            age=None,
            birth_date=None,
            validation_status="NOT_FOUND",
            message="Tanggal lahir tidak dapat ditemukan dari teks KTP maupun nomor NIK.",
            age_source="NONE"
        )

    age = calculate_age(chosen_date, reference_date)
    is_valid = age >= min_age

    if is_valid:
        status = "VALID"
        msg = f"Usia terverifikasi {age} tahun (Memenuhi syarat: usia >= {min_age} tahun)."
    else:
        status = "UNDERAGE"
        msg = f"Usia terverifikasi {age} tahun (TIDAK MEMENUHI SYARAT: usia di bawah {min_age} tahun)."

    return AgeValidationResult(
        is_valid=is_valid,
        is_above_18=is_valid,
        age=age,
        birth_date=chosen_date.strftime("%Y-%m-%d"),
        validation_status=status,
        message=msg,
        age_source=age_source
    )
