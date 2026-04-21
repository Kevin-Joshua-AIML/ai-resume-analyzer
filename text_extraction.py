import pdfplumber
import docx
import io

try:
    import fitz # PyMuPDF
except ImportError:
    fitz = None

def extract_text_from_pdf(file_bytes):
    """Extract text from a PDF file byte stream, with PyMuPDF fallback."""
    text = ""
    # Store current stream position
    start_pos = file_bytes.tell() if hasattr(file_bytes, 'tell') else 0
    
    # Try pdfplumber
    try:
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception as e:
        pass
        
    # Reset stream for fallback
    if hasattr(file_bytes, 'seek'):
        file_bytes.seek(0)
        
    # Fallback to PyMuPDF (fitz)
    if fitz:
        try:
            content = file_bytes.read() if hasattr(file_bytes, 'read') else file_bytes
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            if text.strip():
                return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to read PDF even with fallback: {e}")
            
    if not text.strip():
        raise ValueError("Failed to extract text from PDF using all parsers.")
        
    return text.strip()

def extract_text_from_docx(file_bytes):
    """Extract text from a DOCX file byte stream."""
    try:
        doc = docx.Document(file_bytes)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to read DOCX: {e}")

def extract_text(file_obj, filename):
    """Dispatch to the right extractor based on filename."""
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_obj)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_obj)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")
