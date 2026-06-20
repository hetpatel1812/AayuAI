"""
Aayu AI — PDF Text Extractor
Uses pdfplumber for digital PDFs from Indian labs.
"""
import pdfplumber


def extract_text_from_pdf(file_path):
    """Extract text from a digital PDF report.
    
    Args:
        file_path: Path to the PDF file.
    
    Returns:
        str: Extracted text content from all pages.
    """
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

                # Also try extracting tables
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            cleaned = [str(cell).strip() if cell else '' for cell in row]
                            text += ' | '.join(cleaned) + '\n'
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

    return text.strip() if text.strip() else None
