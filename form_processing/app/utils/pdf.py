import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io
from pdf2image import convert_from_bytes
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[np.ndarray]:
    """
    Convert PDF to list of images using multiple methods
    """
    try:
        # First attempt with pdf2image
        try:
            images = convert_from_bytes(
                pdf_bytes,
                dpi=dpi,
                fmt='png',
                grayscale=False,
                size=None,
                paths_only=False
            )
            return [np.array(img) for img in images]
        except Exception as e:
            logger.warning(f"pdf2image conversion failed, trying PyMuPDF: {str(e)}")

        # Second attempt with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_bytes = pix.tobytes()
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], img_bytes)
            images.append(np.array(img))

        return images

    except Exception as e:
        logger.error(f"Error in PDF conversion: {str(e)}")
        raise RuntimeError(f"Failed to convert PDF: {str(e)}")

def check_pdf_support() -> bool:
    """Check if PDF support is available"""
    try:
        # Check pdf2image
        from pdf2image import convert_from_bytes
        
        # Check PyMuPDF
        import fitz
        
        return True
    except Exception as e:
        logger.warning(f"PDF support not available: {str(e)}")
        return False