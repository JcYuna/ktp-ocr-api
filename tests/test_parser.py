from app.services.ktp_parser import parse_ktp_lines, fix_nik_string

def test_fix_nik_string():
    # Test OCR misread substitutions: 'l' -> '1', 'O' -> '0', 'B' -> '8'
    raw_ocr_nik = "3l7lO123O495OOO1"
    fixed = fix_nik_string(raw_ocr_nik)
    assert fixed == "3171012304950001", f"Expected 3171012304950001, got {fixed}"
    print("test_fix_nik_string PASSED")

def test_parse_ktp_lines():
    mock_ocr_lines = [
        "PROVINSI DKI JAKARTA",
        "KOTA JAKARTA SELATAN",
        "NIK : 3171012304950001",
        "Nama : BUDI SANTOSO",
        "Tempat/Tgl Lahir : JAKARTA, 23-04-1995",
        "Jenis Kelamin : LAKI-LAKI Gol. Darah : O",
        "Alamat : JL. SUDIRMAN NO. 45",
        "RT/RW : 005/002",
        "Kel/Desa : SENAYAN",
        "Kecamatan : KEBAYORAN BARU",
        "Agama : ISLAM",
        "Status Perkawinan: BELUM KAWIN",
        "Pekerjaan : KARYAWAN SWASTA",
        "Kewarganegaraan: WNI",
        "Berlaku Hingga : SEUMUR HIDUP"
    ]

    result = parse_ktp_lines(mock_ocr_lines)
    assert result.nik == "3171012304950001"
    assert result.nama == "BUDI SANTOSO"
    assert result.tempat_lahir == "JAKARTA"
    assert result.tanggal_lahir == "1995-04-23"
    assert result.jenis_kelamin == "LAKI-LAKI"
    assert result.golongan_darah == "O"
    assert result.alamat == "JL. SUDIRMAN NO. 45"
    assert result.rt_rw == "005/002"
    assert result.kel_desa == "SENAYAN"
    assert result.kecamatan == "KEBAYORAN BARU"
    assert result.agama == "ISLAM"
    assert result.status_perkawinan == "BELUM KAWIN"
    assert result.pekerjaan == "KARYAWAN SWASTA"
    assert result.kewarganegaraan == "WNI"
    assert result.berlaku_hingga == "SEUMUR HIDUP"
    print("test_parse_ktp_lines PASSED")

if __name__ == "__main__":
    test_fix_nik_string()
    test_parse_ktp_lines()
    print("SEMUA UNIT TEST KTP PARSER BERHASIL!")
