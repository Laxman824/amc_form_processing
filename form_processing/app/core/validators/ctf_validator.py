from .base_validator import BaseSectionValidator
from .sip_validator import SIPValidator
import cv2
import numpy as np
from typing import Dict, Tuple, List
import re

class CTFValidator(BaseSectionValidator):
    def __init__(self):
        super().__init__()
        self.sip_validator = SIPValidator()  # For checking attached SIP forms
        
        # Define transaction sections and their coordinates
        self.transaction_sections = {
            'AP': {'y1': 0.25, 'y2': 0.32},  # Additional Purchase
            'Switch': {'y1': 0.58, 'y2': 0.75},
            'Redemption': {'y1': 0.75, 'y2': 0.92}
        }

    def validate_transaction_sections(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate transaction type sections (AP/Switch/Redemption)"""
        try:
            results = {
                'transactions_found': [],
                'has_ap': False,
                'has_switch': False,
                'has_redemption': False,
                'details': {}
            }
            
            height = image.shape[0]
            
            # Check each transaction section
            for trx_type, coords in self.transaction_sections.items():
                # Extract section
                y1 = int(coords['y1'] * height)
                y2 = int(coords['y2'] * height)
                section_img = image[y1:y2, :]
                
                # Check if section is ticked/filled
                is_checked = self.detect_checkbox_state(section_img)
                text = self.extract_text(section_img)
                
                # Look for transaction-specific keywords
                keywords = {
                    'AP': ['additional purchase', 'ap', 'purchase'],
                    'Switch': ['switch', 'switching', 'transfer'],
                    'Redemption': ['redemption', 'redeem', 'withdraw']
                }
                
                has_keywords = any(kw in text.lower() for kw in keywords[trx_type])
                
                # If section is ticked and has relevant text
                if is_checked and has_keywords:
                    results[f'has_{trx_type.lower()}'] = True
                    results['transactions_found'].append(trx_type)
                    
                    # Check for additional details
                    amount_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
                    amounts = re.findall(amount_pattern, text)
                    
                    results['details'][trx_type] = {
                        'is_checked': True,
                        'has_amount': bool(amounts),
                        'amounts_found': amounts
                    }
            
            return bool(results['transactions_found']), results
            
        except Exception as e:
            self.logger.error(f"Error validating transaction sections: {e}")
            return False, {}

    def check_sip_form_attached(self, images: List[np.ndarray]) -> Tuple[bool, Dict]:
        """Check for attached SIP/SIP TOP UP form"""
        try:
            results = {
                'sip_form_found': False,
                'sip_form_page': None,
                'sip_details': None
            }
            
            # Skip first page (CTF)
            for page_num, image in enumerate(images[1:], 1):
                # Check for SIP form indicators
                text = self.extract_text(image)
                sip_indicators = ['sip registration', 'sip with top-up', 'systematic investment plan']
                
                if any(indicator in text.lower() for indicator in sip_indicators):
                    # Found potential SIP form, validate it
                    is_valid, sip_details = self.sip_validator.validate_sip_details(image)
                    if is_valid:
                        results['sip_form_found'] = True
                        results['sip_form_page'] = page_num
                        results['sip_details'] = sip_details
                        break
            
            return results['sip_form_found'], results
            
        except Exception as e:
            self.logger.error(f"Error checking SIP form: {e}")
            return False, {}

    def validate_form(self, images: List[np.ndarray]) -> Dict:
        """Complete validation of CTF form"""
        try:
            results = {
                'status': 'success',
                'total_pages': len(images),
                'transactions': [],
                'has_sip_form': False,
                'form_types': ['CTF']
            }
            
            # Check transaction sections on first page
            is_valid, trx_results = self.validate_transaction_sections(images[0])
            if is_valid:
                results['transactions'] = trx_results['transactions_found']
                results.update(trx_results)
            
            # Check for attached SIP form
            if len(images) > 1:
                is_valid, sip_results = self.check_sip_form_attached(images)
                results['has_sip_form'] = is_valid
                if is_valid:
                    results['form_types'].append('SIP')
                    results['sip_form_details'] = sip_results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in CTF validation: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'total_pages': len(images)
            }