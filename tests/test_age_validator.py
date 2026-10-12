from datetime import date
from app.services.age_validator import (
    parse_indonesian_date_string,
    parse_birthdate_from_nik,
    calculate_age,
    validate_ktp_age
)

def test_parse_indonesian_date_string():
    # Format strip & slash
    assert parse_indonesian_date_string("17-08-1995") == date(1995, 8, 17)
    assert parse_indonesian_date_string("17/08/1995") == date(1995, 8, 17)
    assert parse_indonesian_date_string("1995-08-17") == date(1995, 8, 17)
    
    # Format teks nama bulan Indonesia
    assert parse_indonesian_date_string("17 AGUSTUS 1995") == date(1995, 8, 17)
    assert parse_indonesian_date_string("10 MEI 2002") == date(2002, 5, 10)
    assert parse_indonesian_date_string("05 DESEMBER 1990") == date(1990, 12, 5)
    print("test_parse_indonesian_date_string PASSED")

def test_parse_birthdate_from_nik():
    # NIK Pria lahir 23-04-1995
    nik_pria = "3171012304950001"
    bdate_pria, gender_pria = parse_birthdate_from_nik(nik_pria)
    assert bdate_pria == date(1995, 4, 23)
    assert gender_pria == "LAKI-LAKI"

    # NIK Wanita lahir 15-08-2002 (tanggal + 40 = 55)
    nik_wanita = "3201015508020002"
    bdate_wanita, gender_wanita = parse_birthdate_from_nik(nik_wanita)
    assert bdate_wanita == date(2002, 8, 15)
    assert gender_wanita == "PEREMPUAN"
    print("test_parse_birthdate_from_nik PASSED")

def test_calculate_age_and_validation():
    ref_date = date(2026, 10, 11)

    # Orang dewasa lahir 1995 (umur 31 tahun)
    val_adult = validate_ktp_age(
        text_birth_date="17-08-1995",
        nik="3171011708950001",
        min_age=18,
        reference_date=ref_date
    )
    assert val_adult.is_valid is True
    assert val_adult.is_above_18 is True
    assert val_adult.age == 31
    assert val_adult.validation_status == "VALID"

    # Anak di bawah umur lahir 2012 (umur 14 tahun)
    val_underage = validate_ktp_age(
        text_birth_date="12-05-2012",
        min_age=18,
        reference_date=ref_date
    )
    assert val_underage.is_valid is False
    assert val_underage.is_above_18 is False
    assert val_underage.age == 14
    assert val_underage.validation_status == "UNDERAGE"

    # Tepat berumur 18 tahun (lahir 10 Oktober 2008 vs ref 11 Oktober 2026)
    val_exact = validate_ktp_age(
        text_birth_date="10-10-2008",
        min_age=18,
        reference_date=ref_date
    )
    assert val_exact.is_valid is True
    assert val_exact.age == 18
    assert val_exact.validation_status == "VALID"
    print("test_calculate_age_and_validation PASSED")

if __name__ == "__main__":
    test_parse_indonesian_date_string()
    test_parse_birthdate_from_nik()
    test_calculate_age_and_validation()
    print("SEMUA UNIT TEST VALIDASI UMUR BERHASIL!")
