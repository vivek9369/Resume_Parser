import os
import re

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using pdfplumber with PyPDF2 fallback."""
    text_content = []
    
    # Try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    
        extracted = "\n\n".join(text_content).strip()
        if extracted:
            return extracted
    except Exception as e:
        print(f"pdfplumber error: {e}")
        
    # Fallback to PyPDF2
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    
        extracted = "\n\n".join(text_content).strip()
        if extracted:
            return extracted
    except Exception as e:
        print(f"PyPDF2 error: {e}")
        
    return "\n\n".join(text_content).strip()

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
                
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
                    
        return "\n".join(full_text).strip()
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from plain text file."""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
    return ""

def clean_extracted_text(raw_text):
    """Normalize whitespace and remove unprintable characters."""
    if not raw_text:
        return ""
    cleaned = raw_text.replace('\x00', ' ')
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    return cleaned.strip()

def parse_resume_file(file_path):
    """
    Extracts and normalizes raw text from PDF, DOCX, or TXT resume files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        raw_text = extract_text_from_docx(file_path)
    elif ext in ['.txt', '.rtf', '.md']:
        raw_text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported format '{ext}'. Please upload a PDF, DOCX, or TXT resume.")
        
    cleaned = clean_extracted_text(raw_text)
    if not cleaned:
        raise ValueError("Could not read text from the file. Please ensure it is not scanned/image-only or corrupted.")
        
    return cleaned
