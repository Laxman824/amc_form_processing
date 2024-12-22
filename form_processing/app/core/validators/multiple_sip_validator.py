from .base_validator import BaseSectionValidator
from .sip_validator import SIPValidator
import cv2
import numpy as np
from typing import Dict, List, Tuple
import re

class MultipleSIPValidator(BaseSectionValidator):
    def __init__(self):
        super().__init__()
        self.sip_validator = SIPValidator()

    def validate_scheme(self, image: np.ndarray, scheme_number: int) -> Tuple[bool, Dict]:
        """Validate individual scheme section"""
        try:
            results = {
                'scheme_number': scheme_number,
                'scheme_name_found': False,
                'amount_found': False,
                'frequency_found': False,
                'details_filled': False
            }
            
            text = self.extract_text(image)
            
            # Check scheme name
            scheme_pattern = rf'scheme.*{scheme_number}|scheme\s*name'
            results['scheme_name_found'] = bool(re.search(scheme_pattern, text, re.IGNORECASE))
            
            # Validate SIP details for this scheme
            is_valid, details = self.sip_validator.validate_sip_details(image)
            results.update(details)
            
            # Check for scheme-specific details
            folio_pattern = r'folio.*\d+'
            results['has_folio'] = bool(re.search(folio_pattern, text, re.IGNORECASE))
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating scheme {scheme_number}: {e}")
            return False, {}

    def validate_all_schemes(self, images: List[np.ndarray]) -> Tuple[bool, Dict]:
        """Validate all scheme sections"""
        try:
            results = {
                'total_schemes': 0,
                'filled_schemes': 0,
                'schemes': {}
            }
            
            for i, image in enumerate(images, 1):
                is_valid, scheme_results = self.validate_scheme(image, i)
                results['schemes'][f'scheme_{i}'] = scheme_results
                
                if is_valid:
                    results['filled_schemes'] += 1
                results['total_schemes'] += 1
            
            # Overall validation - at least one scheme should be properly filled
            is_valid = results['filled_schemes'] > 0
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating schemes: {e}")
            return False, {}

    def validate_common_details(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate common details section"""
        try:
            results = {
                'investor_details_found': False,
                'pan_found': False,
                'contact_found': False,
                'details_filled': False
            }
            
            text = self.extract_text(image)
            
            # Check PAN
            pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
            results['pan_found'] = bool(re.search(pan_pattern, text.upper()))
            
            # Check contact details
            contact_pattern = r'\d{10}|\d{3}[-\s]\d{8}'
            results['contact_found'] = bool(re.search(contact_pattern, text))
            
            # Check investor details
            investor_keywords = ['name', 'address', 'email']
            results['investor_details_found'] = any(keyword in text for keyword in investor_keywords)
            
            # Check if details are filled
            has_numbers = bool(re.findall(r'\d+', text))
            has_text = len(text.split()) > 10  # More than 10 words
            results['details_filled'] = has_numbers and has_text
            
            is_valid = results['investor_details_found'] and results['details_filled']
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating common details: {e}")
            return False, {}

    def validate_bank_details(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate bank details section"""
        try:
            # First check basic bank details
            is_valid, results = self.detect_bank_details(image)
            
            # Additional checks for multiple SIP form
            text = self.extract_text(image)
            
            # Check for multiple bank accounts
            account_pattern = r'\d{9,18}'
            accounts = re.findall(account_pattern, text)
            results['total_accounts'] = len(accounts)
            
            # Check for bank names
            bank_keywords = ['bank', 'branch', 'banker']
            results['has_bank_names'] = any(keyword in text for keyword in bank_keywords)
            
            # Check for signatures
            results['has_signature'] = self.detect_signature(image)
            
            # Overall validation
            is_valid = (is_valid and 
                       results['has_bank_names'] and 
                       results['has_signature'])
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating bank details: {e}")
            return False, {}