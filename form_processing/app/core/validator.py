# import cv2
# import numpy as np
# from typing import Dict, Tuple
# import pytesseract
# import re
# from ..models.template import SectionType, ValidationRule
# from ..models.form import ValidationStatus

# class SectionValidator:
#     def __init__(self):
#         self.confidence_threshold = 0.6
#         self.setup_ocr()

#     def setup_ocr(self):
#         """Setup OCR configuration"""
#         custom_config = r'--oem 3 --psm 6'
#         self.ocr_config = custom_config

#     def validate_section(self, image: np.ndarray, section_type: SectionType, 
#                         rules: list) -> Tuple[ValidationStatus, Dict, float]:
#         """Validate section based on type and rules"""
#         if section_type == SectionType.SIP_DETAILS:
#             return self._validate_sip_details(image, rules)
#         elif section_type == SectionType.OTM_SECTION:
#             return self._validate_otm_section(image, rules)
#         elif section_type == SectionType.TRANSACTION_TYPE:
#             return self._validate_transaction_type(image, rules)
#         elif section_type == SectionType.SECTION_8:
#             return self._validate_section_8(image, rules)
#         else:
#             return ValidationStatus.NOT_APPLICABLE, {}, 0.0

#     def _validate_sip_details(self, image: np.ndarray, rules: list) -> Tuple[ValidationStatus, Dict, float]:
#         """Validate SIP details section"""
#         # Convert to grayscale
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
#         # Extract text
#         text = pytesseract.image_to_string(gray, config=self.ocr_config)
        
#         details = {
#             "frequency_found": False,
#             "amount_found": False,
#             "table_filled": False
#         }
        
#         # Check for frequency
#         frequency_keywords = ['monthly', 'quarterly', 'yearly', 'weekly']
#         details["frequency_found"] = any(keyword in text.lower() for keyword in frequency_keywords)
        
#         # Check for amount (look for numbers followed by currency symbols or common formats)
#         amount_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
#         details["amount_found"] = bool(re.search(amount_pattern, text.lower()))
        
#         # Check if table has entries (look for multiple numbers in structured format)
#         details["table_filled"] = len(re.findall(r'\d+', text)) > 3
        
#         # Calculate confidence
#         confidence = sum([
#             details["frequency_found"],
#             details["amount_found"],
#             details["table_filled"]
#         ]) / 3.0
        
#         # Determine status
#         if confidence > self.confidence_threshold:
#             status = ValidationStatus.VALID
#         elif confidence > 0:
#             status = ValidationStatus.WARNING
#         else:
#             status = ValidationStatus.INVALID
            
#         return status, details, confidence

#     def _validate_otm_section(self, image: np.ndarray, rules: list) -> Tuple[ValidationStatus, Dict, float]:
#         """Validate OTM section"""
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
#         text = pytesseract.image_to_string(gray, config=self.ocr_config)
        
#         details = {
#             "account_number_found": False,
#             "ifsc_found": False,
#             "bank_details_found": False
#         }
        
#         # Check for account number (sequence of digits)
#         account_pattern = r'\d{9,18}'
#         details["account_number_found"] = bool(re.search(account_pattern, text))
        
#         # Check for IFSC code (standard format)
#         ifsc_pattern = r'[A-Z]{4}0[A-Z0-9]{6}'
#         details["ifsc_found"] = bool(re.search(ifsc_pattern, text))
        
#         # Check for general bank details
#         bank_keywords = ['bank', 'branch', 'account', 'ifsc']
#         details["bank_details_found"] = any(keyword in text.lower() for keyword in bank_keywords)
        
#         confidence = sum([
#             details["account_number_found"],
#             details["ifsc_found"],
#             details["bank_details_found"]
#         ]) / 3.0
        
#         if details["account_number_found"] and details["ifsc_found"]:
#             status = ValidationStatus.VALID
#         elif confidence > 0:
#             status = ValidationStatus.WARNING
#         else:
#             status = ValidationStatus.INVALID
            
#         return status, details, confidence

#     def _validate_transaction_type(self, image: np.ndarray, rules: list) -> Tuple[ValidationStatus, Dict, float]:
#         """Validate transaction type section"""
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
#         # Look for checked boxes
#         checked_boxes = self._detect_checked_boxes(gray)
        
#         details = {
#             "checked_boxes_found": len(checked_boxes),
#             "transaction_type": None
#         }
        
#         # Extract text near checked boxes
#         if checked_boxes:
#             text = pytesseract.image_to_string(gray, config=self.ocr_config)
            
#             # Look for transaction type keywords
#             transaction_types = {
#                 'registration': 'SIP Registration',
#                 'renewal': 'SIP Renewal',
#                 'top-up': 'SIP with Top-up',
#                 'change': 'Change in Bank Details'
#             }
            
#             for keyword, trx_type in transaction_types.items():
#                 if keyword in text.lower():
#                     details["transaction_type"] = trx_type
#                     break
        
#         confidence = 1.0 if details["transaction_type"] else 0.0
        
#         if details["transaction_type"]:
#             status = ValidationStatus.VALID
#         else:
#             status = ValidationStatus.INVALID
            
#         return status, details, confidence

#     def _validate_section_8(self, image: np.ndarray, rules: list) -> Tuple[ValidationStatus, Dict, float]:
#         """Validate Section 8 (investment details)"""
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
#         text = pytesseract.image_to_string(gray, config=self.ocr_config)
        
#         details = {
#             "investment_type_found": False,
#             "scheme_details_found": False,
#             "filled_rows": 0
#         }
        
#         # Check for investment type
#         investment_keywords = ['sip', 'micro-sip', 'top-up']
#         details["investment_type_found"] = any(keyword in text.lower() for keyword in investment_keywords)
        
#         # Check for scheme details
#         scheme_keywords = ['scheme', 'folio', 'amount']
#         details["scheme_details_found"] = any(keyword in text.lower() for keyword in scheme_keywords)
        
#         # Count filled rows (look for patterns of numbers and text)
#         rows = re.findall(r'(?:\w+\s+){2,}\d+(?:,\d+)*(?:\.\d{2})?', text)
#         details["filled_rows"] = len(rows)
        
#         confidence = (
#             details["investment_type_found"] + 
#             details["scheme_details_found"] + 
#             (details["filled_rows"] > 0)
#         ) / 3.0
        
#         if confidence > self.confidence_threshold:
#             status = ValidationStatus.VALID
#         elif confidence > 0:
#             status = ValidationStatus.WARNING
#         else:
#             status = ValidationStatus.INVALID
            
#         return status, details, confidence

#     def _detect_checked_boxes(self, gray_image: np.ndarray) -> list:
#         """Detect checked boxes in image"""
#         # Threshold the image
#         _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
#         # Find contours
#         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         checked_boxes = []
#         for contour in contours:
#             # Get bounding box
#             x, y, w, h = cv2.boundingRect(contour)
            
#             # Check if it's square-ish
#             if 0.8 < w/h < 1.2 and w > 10:
#                 # Check if it's filled
#                 roi = thresh[y:y+h, x:x+w]
#                 if np.mean(roi) > 127:  # More black than white
#                     checked_boxes.append((x, y, w, h))
        
#         return checked_boxes

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Tuple
import re
import logging

class SectionValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_ocr()

    def setup_ocr(self):
        """Setup OCR configuration"""
        custom_config = r'--oem 3 --psm 6'
        self.ocr_config = custom_config

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from image"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing
            image = cv2.threshold(
                image, 0, 255, 
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]
            
            # Extract text
            text = pytesseract.image_to_string(image, config=self.ocr_config)
            return text.strip().lower()
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""

    def validate_sip_details(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate SIP details section"""
        try:
            text = self.extract_text(image)
            
            details = {
                "frequency_found": False,
                "amount_found": False,
                "fields_filled": False
            }
            
            # Check frequency
            frequency_keywords = ['monthly', 'quarterly', 'yearly']
            details["frequency_found"] = any(
                keyword in text for keyword in frequency_keywords
            )
            
            # Check amount
            amount_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
            details["amount_found"] = bool(
                re.search(amount_pattern, text)
            )
            
            # Check fields
            details["fields_filled"] = len(re.findall(r'\d+', text)) >= 3
            
            is_filled = any(details.values())
            return is_filled, details
            
        except Exception as e:
            self.logger.error(f"Error validating SIP details: {e}")
            return False, {}

    def validate_otm_section(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate OTM section"""
        try:
            text = self.extract_text(image)
            
            details = {
                "account_number_found": False,
                "ifsc_found": False
            }
            
            # Check account number
            account_pattern = r'\d{9,18}'
            details["account_number_found"] = bool(
                re.search(account_pattern, text)
            )
            
            # Check IFSC
            ifsc_pattern = r'[A-Z]{4}0[A-Z0-9]{6}'
            details["ifsc_found"] = bool(
                re.search(ifsc_pattern, text.upper())
            )
            
            is_filled = all(details.values())
            return is_filled, details
            
        except Exception as e:
            self.logger.error(f"Error validating OTM section: {e}")
            return False, {}

    def validate_transaction_type(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate transaction type section"""
        try:
            text = self.extract_text(image)
            
            details = {
                "type_found": None,
                "is_checked": False
            }
            
            # Check transaction types
            types = {
                'registration': ['registration', 'new'],
                'renewal': ['renewal', 'renew'],
                'topup': ['top-up', 'topup'],
                'change': ['change', 'modify']
            }
            
            for type_name, keywords in types.items():
                if any(keyword in text for keyword in keywords):
                    details["type_found"] = type_name
                    break
            
            # Check for marking/checkbox
            details["is_checked"] = self._check_for_marking(image)
            
            is_filled = bool(details["type_found"] and details["is_checked"])
            return is_filled, details
            
        except Exception as e:
            self.logger.error(f"Error validating transaction type: {e}")
            return False, {}

    def _check_for_marking(self, image: np.ndarray) -> bool:
        """Check for markings or checked boxes"""
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(
                image, 0, 255, 
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            
            # Count dark pixels
            dark_pixels = np.sum(thresh > 0)
            total_pixels = thresh.size
            
            # If more than 5% pixels are dark, consider it marked
            return (dark_pixels / total_pixels) > 0.05
            
        except Exception as e:
            self.logger.error(f"Error checking for marking: {e}")
            return False