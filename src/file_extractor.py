import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Direct Tesseract path for Windows
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import shutil

tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text_from_pdf(file_path):
    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


def extract_text_from_image(file_path):
    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return text