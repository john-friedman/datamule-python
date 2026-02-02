import pypdfium2 as pdfium

def has_extractable_text(pdf_bytes):
    """
    Lightweight check if PDF has extractable text.
    Only checks first page.
    """
    try:
        # Load PDF from bytes
        pdf = pdfium.PdfDocument(pdf_bytes)
        
        # Only check first page
        if len(pdf) == 0:
            return False
        
        page = pdf[0]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        
        # Close resources
        textpage.close()
        page.close()
        pdf.close()
        
        # Check if we got any text (after stripping whitespace)
        return len(text.strip()) > 0
        
    except Exception as e:
        # If can't open/parse, assume no text
        return False