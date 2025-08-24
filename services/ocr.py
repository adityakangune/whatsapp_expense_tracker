import io, requests
from PIL import Image
import pytesseract
from config import OCR_BACKEND, OCRSPACE_API_KEY, TESSERACT_CMD, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

# Configure tesseract path (only used if OCR_BACKEND=tesseract)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def fetch_media_bytes(url: str) -> bytes:
    r = requests.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=20)
    r.raise_for_status()
    return r.content

def ocr_via_ocrspace(image_bytes: bytes) -> str:
    if not OCRSPACE_API_KEY:
        raise RuntimeError("Missing OCRSPACE_API_KEY")
    url = "https://api.ocr.space/parse/image"
    files = {"file": ("receipt.jpg", image_bytes, "application/octet-stream")}
    data = {"language": "eng", "scale": "true", "isTable": "true"}
    headers = {"apikey": OCRSPACE_API_KEY}
    r = requests.post(url, headers=headers, data=data, files=files, timeout=30)
    r.raise_for_status()
    js = r.json()
    if js.get("IsErroredOnProcessing"):
        raise RuntimeError(js.get("ErrorMessage") or "OCR.Space error")
    parsed = js.get("ParsedResults", [])
    text = parsed[0].get("ParsedText", "") if parsed else ""
    return text.strip()

def ocr_via_tesseract(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(img).strip()

def ocr_from_media_url(media_url: str) -> str:
    content = fetch_media_bytes(media_url)
    if OCR_BACKEND.lower() == "tesseract":
        return ocr_via_tesseract(content)
    return ocr_via_ocrspace(content)  # default
