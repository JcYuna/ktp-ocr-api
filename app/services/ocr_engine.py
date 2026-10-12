import time
import cv2
import numpy as np
import easyocr
from typing import List, Tuple, Dict, Any, Optional
from app.config import settings
from app.services.image_preprocessor import preprocess_ktp_image

class OCREngine:
    _instance: Optional["OCREngine"] = None
    
    def __init__(self):
        # Inisialisasi EasyOCR Reader dengan bahasa Indonesia & Inggris
        self.reader = easyocr.Reader(
            lang_list=settings.OCR_LANGUAGES,
            gpu=settings.OCR_USE_GPU,
            verbose=False
        )
        print("OCREngine: EasyOCR model siap digunakan.")

    @classmethod
    def get_instance(cls) -> "OCREngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def extract_text_from_image(self, image: np.ndarray) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Menjalankan OCR pada gambar KTP:
        1. Preprocessing (Resize & CLAHE enhancement)
        2. EasyOCR text detection & recognition
        3. Pengurutan baris berdasarkan posisi Y koordinat (dari atas ke bawah)
        """
        # Prapemrosesan gambar
        resized, enhanced = preprocess_ktp_image(image)

        # Lakukan deteksi teks pada gambar yang sudah ditingkatkan kontrasnya
        # Format hasil: [ [bbox, text, confidence], ... ]
        ocr_results = self.reader.readtext(enhanced, paragraph=False)

        # Urutkan hasil berdasarkan koordinat Y atas (bbox[0][1])
        # untuk memastikan teks terbaca urut dari bagian atas KTP ke bawah
        def get_top_y(item):
            bbox = item[0]
            return min(pt[1] for pt in bbox)

        sorted_results = sorted(ocr_results, key=get_top_y)

        extracted_lines = []
        detailed_items = []
        for bbox, text, conf in sorted_results:
            cleaned_text = text.strip()
            if cleaned_text:
                extracted_lines.append(cleaned_text)
                detailed_items.append({
                    "text": cleaned_text,
                    "confidence": round(float(conf), 4),
                    "bbox": [[int(p[0]), int(p[1])] for p in bbox]
                })

        return extracted_lines, detailed_items

def get_ocr_engine() -> OCREngine:
    return OCREngine.get_instance()
