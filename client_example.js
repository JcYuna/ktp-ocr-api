/**
 * Contoh integrasi API OCR KTP & Validasi Usia menggunakan JavaScript / Node.js (fetch & FormData).
 * Kompatibel dengan Node.js 18+, Next.js, Express, React, Vue, dll.
 */

const fs = require('fs');
const path = require('path');

const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Ekstraksi KTP via Multipart Form Data (Upload File)
 */
async function extractKTPFromFile(filePath, minAge = 18) {
  const fileBuffer = fs.readFileSync(filePath);
  const blob = new Blob([fileBuffer], { type: 'image/jpeg' });
  
  const formData = new FormData();
  formData.append('file', blob, path.basename(filePath));

  const response = await fetch(`${API_BASE_URL}/api/v1/ktp/extract?min_age=${minAge}`, {
    method: 'POST',
    body: formData,
  });

  const result = await response.json();
  console.log('=== HASIL DETEKSI KTP (Node.js) ===');
  console.log('NIK           :', result.data?.nik);
  console.log('Nama          :', result.data?.nama);
  console.log('Tgl Lahir     :', result.data?.tanggal_lahir);
  console.log('Usia          :', result.age_validation?.age);
  console.log('Valid (>= 18) :', result.age_validation?.is_valid);
  console.log('Pesan         :', result.age_validation?.message);
  return result;
}

/**
 * Ekstraksi KTP via Base64 JSON
 */
async function extractKTPFromBase64(filePath, minAge = 18) {
  const base64Data = fs.readFileSync(filePath, { encoding: 'base64' });

  const response = await fetch(`${API_BASE_URL}/api/v1/ktp/extract-base64?min_age=${minAge}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_base64: base64Data }),
  });

  return await response.json();
}

/**
 * Validasi Usia Langsung Berdasarkan NIK
 */
async function validateAgeDirect(nik, minAge = 18) {
  const response = await fetch(`${API_BASE_URL}/api/v1/ktp/validate-age?min_age=${minAge}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nik }),
  });

  return await response.json();
}

// Menjalankan contoh jika dipanggil langsung dengan `node client_example.js`
if (require.main === module) {
  const samplePath = path.join(__dirname, 'sample_images', 'sample_ktp_adult.jpg');
  extractKTPFromFile(samplePath).catch(console.error);
}

module.exports = { extractKTPFromFile, extractKTPFromBase64, validateAgeDirect };
