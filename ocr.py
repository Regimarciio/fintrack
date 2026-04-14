import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

def extract_text(file_path):
    try:
        if file_path.endswith(".pdf"):
            text = ""

            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text += t
            except:
                pass

            if len(text.strip()) < 100:
                images = convert_from_path(file_path)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img)

            return text

        elif file_path.lower().endswith(("png","jpg","jpeg")):
            return pytesseract.image_to_string(Image.open(file_path))

        elif file_path.endswith(".txt"):
            return open(file_path).read()

    except Exception as e:
        return str(e)

