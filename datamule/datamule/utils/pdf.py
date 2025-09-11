def has_extractable_text(pdf_bytes, search_range=50000):
    """
    Check if PDF contains extractable text within first N bytes
    Returns True if found in range, False otherwise
    
    Args:
        pdf_bytes: PDF content as bytes
        search_range: Number of bytes to search from start (default 50KB)
    """
    # Text indicators to search for
    indicators = [
        b'BT',  # Begin text - most common
        b'Tj',  # Show text
        b'TJ',  # Show text with positioning
        b'Tf',  # Set font
    ]
    
    # Search only within the specified range
    search_data = pdf_bytes[:search_range]
    
    for indicator in indicators:
        if indicator in search_data:
            return True
    
    return False