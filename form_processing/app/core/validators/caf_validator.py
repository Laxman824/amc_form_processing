from .base_validator import BaseSectionValidator
import cv2
import numpy as np
from typing import Dict, Tuple

class CAFValidator(BaseSectionValidator):
    def validate_section8(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate Section 8 (SIP details)"""
        try:
            results = {
                'sip_checkbox_checked': False,
                'sip_details_filled': False,
                'frequency_found': False,
                'amount_found': False,
                'scheme_details_found': False
            }
            
            # Extract text
            text = self.extract_text(image)
            
            # Check SIP checkbox
            # Assuming checkbox is in top portion
            height = image.shape[0]
            checkbox_region = image[0:int(height*0.2), :]
            results['sip_checkbox_checked'] = self.detect_checkbox_state(checkbox_region)
            
            # Check for frequency
            frequency_terms = ['monthly', 'quarterly', 'yearly', 'weekly']
            results['frequency_found'] = any(term in text for term in frequency_terms)
            
            # Check for amount
            amount_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
            results['amount_found'] = bool(re.search(amount_pattern, text))
            
            # Check scheme details
            scheme_keywords = ['scheme', 'folio', 'plan']
            results['scheme_details_found'] = any(keyword in text for keyword in scheme_keywords)
            
            # Check table content
            table_filled, table_details = self.detect_table_content(image)
            results['sip_details_filled'] = table_filled
            results.update(table_details)
            
            # Overall validation
            is_valid = (results['sip_checkbox_checked'] and 
                       (results['frequency_found'] or results['amount_found'] or 
                        results['sip_details_filled']))
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating Section 8: {e}")
            return False, {}

    def validate_otm_section(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate OTM section"""
        try:
            # Check bank details
            is_valid, details = self.detect_bank_details(image)
            
            # Additional OTM-specific checks
            text = self.extract_text(image)
            
            # Check for bank name
            bank_keywords = ['bank', 'branch']
            has_bank_info = any(keyword in text for keyword in bank_keywords)
            
            # Check for authorization
            auth_keywords = ['authorize', 'authorise', 'mandate']
            has_auth = any(keyword in text for keyword in auth_keywords)
            
            # Check for signature
            has_signature = self.detect_signature(image)
            
            details.update({
                'has_bank_info': has_bank_info,
                'has_authorization': has_auth,
                'has_signature': has_signature
            })
            
            # Overall validation - needs bank details and either authorization or signature
            is_valid = is_valid and (has_auth or has_signature)
            
            return is_valid, details
            
        except Exception as e:
            self.logger.error(f"Error validating OTM section: {e}")
            return False, {}

    def validate_nominee_section(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate nominee section if present"""
        try:
            text = self.extract_text(image)
            
            results = {
                'nominee_found': False,
                'details_filled': False,
                'has_signature': False
            }
            
            # Check for nominee details
            nominee_keywords = ['nominee', 'guardian', 'relation']
            results['nominee_found'] = any(keyword in text for keyword in nominee_keywords)
            
            # Check if details are filled
            has_numbers = bool(re.findall(r'\d+', text))
            has_text = len(text.split()) > 5  # More than 5 words
            results['details_filled'] = has_numbers or has_text
            
            # Check for signature
            results['has_signature'] = self.detect_signature(image)
            
            is_valid = results['nominee_found'] and results['details_filled']
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating nominee section: {e}")
            return False, {}