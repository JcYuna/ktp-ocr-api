import base64
import cv2
import numpy as np
from typing import Tuple, Optional

def decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Mengonversi raw bytes gambar menjadi format numpy array (OpenCV BGR).
    """
    if not image_bytes:
        return None
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def decode_base64_image(base64_str: str) -> Optional[np.ndarray]:
    """
    Mengonversi string base64 (termasuk jika memiliki data URL header) menjadi OpenCV array.
    """
    if not base64_str:
        return None
    
    # Hapus header data URI jika ada (misal: "data:image/jpeg;base64,...")
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
        
    try:
        decoded_bytes = base64.b64decode(base64_str)
        return decode_image_bytes(decoded_bytes)
    except Exception:
        return None

def resize_if_needed(image: np.ndarray, max_dimension: int = 1800) -> np.ndarray:
    """
    Menyesuaikan ukuran gambar jika terlalu besar agar pemrosesan OCR cepat dan efisien.
    """
    h, w = image.shape[:2]
    if max(h, w) > max_dimension:
        scale = max_dimension / float(max(h, w))
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image

def enhance_ktp_contrast(image: np.ndarray) -> np.ndarray:
    """
    Meningkatkan kontras gambar KTP menggunakan metode CLAHE (Contrast Limited Adaptive Histogram Equalization)
    pada kanal Luminance (LAB), sehingga teks yang pudar di atas background biru KTP menjadi kontras tajam.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr

def preprocess_ktp_image(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Pipeline prapemrosesan gambar KTP:
    1. Resize ke resolusi optimal
    2. Enhancement kontras (CLAHE)
    Mengembalikan (original_resized, enhanced_image)
    """
    resized = resize_if_needed(image)
    enhanced = enhance_ktp_contrast(resized)
    return resized, enhanced
