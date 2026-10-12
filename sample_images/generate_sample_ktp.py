import os
from PIL import Image, ImageDraw, ImageFont

def generate_mock_ktp(filename: str, name: str, nik: str, ttl: str, gender: str, address: str):
    width, height = 1000, 630
    # KTP khas berlatar belakang gradasi biru kehijauan
    img = Image.new("RGB", (width, height), color=(185, 220, 240))
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((320, 25), "PROVINSI DKI JAKARTA", fill=(0, 0, 0))
    draw.text((300, 50), "KOTA JAKARTA SELATAN", fill=(0, 0, 0))

    # NIK
    draw.text((50, 110), f"NIK            : {nik}", fill=(0, 0, 0))

    # Data pribadi
    fields = [
        ("Nama", name),
        ("Tempat/Tgl Lahir", ttl),
        ("Jenis Kelamin", f"{gender}    Gol. Darah : O"),
        ("Alamat", address),
        ("    RT/RW", "005/002"),
        ("    Kel/Desa", "SENAYAN"),
        ("    Kecamatan", "KEBAYORAN BARU"),
        ("Agama", "ISLAM"),
        ("Status Perkawinan", "BELUM KAWIN"),
        ("Pekerjaan", "KARYAWAN SWASTA"),
        ("Kewarganegaraan", "WNI"),
        ("Berlaku Hingga", "SEUMUR HIDUP"),
    ]

    y_pos = 150
    for label, val in fields:
        draw.text((50, y_pos), f"{label.ljust(18)} : {val}", fill=(0, 0, 0))
        y_pos += 34

    # Dummy photo placeholder
    draw.rectangle([780, 130, 950, 370], outline=(100, 100, 100), fill=(180, 180, 180))
    draw.text((820, 240), "PAS FOTO", fill=(50, 50, 50))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, "JPEG")
    print(f"Sample KTP generated: {filename}")

if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    # 1. KTP Dewasa (lahir 1995 -> usia 31 tahun)
    generate_mock_ktp(
        os.path.join(out_dir, "sample_ktp_adult.jpg"),
        name="BUDI SANTOSO",
        nik="3171012304950001",
        ttl="JAKARTA, 23-04-1995",
        gender="LAKI-LAKI",
        address="JL. SUDIRMAN NO. 45"
    )

    # 2. KTP di bawah umur (lahir 2012 -> usia 14 tahun)
    generate_mock_ktp(
        os.path.join(out_dir, "sample_ktp_underage.jpg"),
        name="ADITYA PRATAMA",
        nik="3171011205120003",
        ttl="JAKARTA, 12-05-2012",
        gender="LAKI-LAKI",
        address="JL. GATOT SUBROTO NO. 10"
    )
