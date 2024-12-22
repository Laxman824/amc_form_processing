import cv2
import numpy as np
import pytesseract
import re
from typing import Dict, Tuple, List
import logging
from PIL import Image

class BaseSectionValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_ocr()

    def setup_ocr(self):
        """Setup OCR configuration"""
        self.ocr_config = r'--oem 3 --psm 6'

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from image with preprocessing"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing
            # Denoise
            denoised = cv2.fastNlMeansDenoising(image)
            
            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Extract text
            text = pytesseract.image_to_string(thresh, config=self.ocr_config)
            return text.strip().lower()
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""

    def detect_checkbox_state(self, image: np.ndarray) -> bool:
        """Detect if a checkbox is checked"""
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Calculate percentage of black pixels
            total_pixels = thresh.size
            black_pixels = np.sum(thresh == 255)
            black_percentage = black_pixels / total_pixels
            
            # If more than 10% is black, consider it checked
            return black_percentage > 0.1
            
        except Exception as e:
            self.logger.error(f"Error detecting checkbox state: {e}")
            return False

    def detect_table_content(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Detect if a table has content"""
        try:
            # Extract text
            text = self.extract_text(image)
            
            # Count numbers in text
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            
            # Check for currency amounts
            amounts = re.findall(r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?', text)
            
            details = {
                'numbers_found': len(numbers),
                'amounts_found': len(amounts),
                'has_content': bool(numbers or amounts)
            }
            
            return bool(numbers or amounts), details
            
        except Exception as e:
            self.logger.error(f"Error detecting table content: {e}")
            return False, {}

    def detect_bank_details(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Detect bank account and IFSC details"""
        try:
            text = self.extract_text(image)
            
            # Look for account number (9-18 digits)
            account_pattern = r'\d{9,18}'
            account_numbers = re.findall(account_pattern, text)
            
            # Look for IFSC code
            ifsc_pattern = r'[A-Z]{4}0[A-Z0-9]{6}'
            ifsc_codes = re.findall(ifsc_pattern, text.upper())
            
            details = {
                'account_number_found': bool(account_numbers),
                'ifsc_found': bool(ifsc_codes),
                'account_numbers': account_numbers,
                'ifsc_codes': ifsc_codes
            }
            
            # Both account number and IFSC should be present
            is_valid = bool(account_numbers and ifsc_codes)
            
            return is_valid, details
            
        except Exception as e:
            self.logger.error(f"Error detecting bank details: {e}")
            return False, {}

    def detect_signature(self, image: np.ndarray) -> bool:
        """Detect presence of signature"""
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Count edge pixels
            total_pixels = edges.size
            edge_pixels = np.sum(edges == 255)
            edge_percentage = edge_pixels / total_pixels
            
            # If more than 1% is edges, consider it signed
            return edge_percentage > 0.01
            
        except Exception as e:
            self.logger.error(f"Error detecting signature: {e}")
            return False