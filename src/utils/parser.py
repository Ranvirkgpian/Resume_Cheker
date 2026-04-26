from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file.
    Note: This is a basic extraction. Complex layouts might require OCR 
    or specialized layout parsers (like layoutparser or AWS Textract).
    """
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
