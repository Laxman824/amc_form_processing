# app/utils/image.py
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple
import pdf2image
from ..models.template import BoundingBox

def convert_pdf_to_images(pdf_bytes: bytes) -> List[np.ndarray]:
    """Convert PDF bytes to list of images"""
    images = pdf2image.convert_from_bytes(pdf_bytes)
    return [np.array(img) for img in images]

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for better text detection"""
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh)

    return denoised

def extract_section(image: np.ndarray, bbox: BoundingBox) -> np.ndarray:
    """Extract section from image using relative coordinates"""
    h, w = image.shape[:2]
    x1 = int(bbox.x * w)
    y1 = int(bbox.y * h)
    x2 = int((bbox.x + bbox.width) * w)
    y2 = int((bbox.y + bbox.height) * h)
    
    return image[y1:y2, x1:x2]
