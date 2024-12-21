# import fitz  # PyMuPDF
# import numpy as np
# from PIL import Image
# import io
# from pdf2image import convert_from_bytes
# from typing import List, Optional
# import logging

# logger = logging.getLogger(__name__)

# def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[np.ndarray]:
#     """
#     Convert PDF to list of images using multiple methods
#     """
#     try:
#         # First attempt with pdf2image
#         try:
#             images = convert_from_bytes(
#                 pdf_bytes,
#                 dpi=dpi,
#                 fmt='png',
#                 grayscale=False,
#                 size=None,
#                 paths_only=False
#             )
#             return [np.array(img) for img in images]
#         except Exception as e:
#             logger.warning(f"pdf2image conversion failed, trying PyMuPDF: {str(e)}")

#         # Second attempt with PyMuPDF
#         doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#         images = []
        
#         for page_num in range(len(doc)):
#             page = doc[page_num]
#             pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
#             img_bytes = pix.tobytes()
            
#             # Convert to PIL Image
#             img = Image.frombytes("RGB", [pix.width, pix.height], img_bytes)
#             images.append(np.array(img))

#         return images

#     except Exception as e:
#         logger.error(f"Error in PDF conversion: {str(e)}")
#         raise RuntimeError(f"Failed to convert PDF: {str(e)}")

# def check_pdf_support() -> bool:
#     """Check if PDF support is available"""
#     try:
#         # Check pdf2image
#         from pdf2image import convert_from_bytes
        
#         # Check PyMuPDF
#         import fitz
        
#         return True
#     except Exception as e:
#         logger.warning(f"PDF support not available: {str(e)}")
#         return False

import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def pdf_to_images(pdf_bytes: bytes, scale: float = 2.0) -> List[np.ndarray]:
    """
    Convert PDF to list of images using PyMuPDF
    Args:
        pdf_bytes: PDF file content in bytes
        scale: Scale factor for resolution (higher = better quality but larger images)
    Returns:
        List of images as numpy arrays
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get the matrix for scaling
            zoom_matrix = fitz.Matrix(scale, scale)
            
            # Get page as pixel map
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            images.append(img_array)
            
        doc.close()
        return images

    except Exception as e:
        logger.error(f"Error in PDF conversion: {str(e)}")
        raise RuntimeError(f"Failed to convert PDF: {str(e)}")

def is_valid_pdf(pdf_bytes: bytes) -> bool:
    """
    Check if the PDF is valid and can be processed
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        doc.close()
        return page_count > 0
    except Exception as e:
        logger.error(f"Invalid PDF: {str(e)}")
        return False