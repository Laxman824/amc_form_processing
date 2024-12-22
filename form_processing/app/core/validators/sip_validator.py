from .base_validator import BaseSectionValidator
import cv2
import numpy as np
from typing import Dict, Tuple
import re

class SIPValidator(BaseSectionValidator):
    def validate_transaction_type(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate transaction type section"""
        try:
            results = {
                'type_detected': None,
                'checkbox_checked': False,
                'details_filled': False
            }
            
            text = self.extract_text(image)
            
            # Check transaction types
            transaction_types = {
                'registration': ['registration', 'new sip'],
                'renewal': ['renewal', 'renew'],
                'topup': ['top-up', 'topup', 'step-up'],
                'change': ['change', 'modify', 'bank change']
            }
            
            # Detect transaction type
            for type_name, keywords in transaction_types.items():
                if any(keyword in text for keyword in keywords):
                    results['type_detected'] = type_name
                    break
            
            # Check for checked checkbox
            results['checkbox_checked'] = self.detect_checkbox_state(image)
            
            # Check if additional details are filled
            details_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
            results['details_filled'] = bool(re.search(details_pattern, text))
            
            is_valid = bool(results['type_detected'] and results['checkbox_checked'])
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating transaction type: {e}")
            return False, {}

    def validate_sip_details(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate SIP details section"""
        try:
            results = {
                'frequency_found': False,
                'amount_found': False,
                'period_found': False,
                'details_filled': False
            }
            
            text = self.extract_text(image)
            
            # Check frequency
            frequency_terms = ['monthly', 'quarterly', 'yearly', 'weekly']
            results['frequency_found'] = any(term in text for term in frequency_terms)
            
            # Check amount
            amount_pattern = r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?'
            amounts = re.findall(amount_pattern, text)
            results['amount_found'] = bool(amounts)
            
            # Check period
            period_pattern = r'\d+\s*(?:month|year|yr)'
            results['period_found'] = bool(re.search(period_pattern, text, re.IGNORECASE))
            
            # Check if table/details are filled
            table_filled, table_details = self.detect_table_content(image)
            results['details_filled'] = table_filled
            results.update(table_details)
            
            # Overall validation
            is_valid = (results['frequency_found'] and 
                       results['amount_found'] and 
                       (results['period_found'] or results['details_filled']))
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating SIP details: {e}")
            return False, {}

    def validate_bank_mandate(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate bank mandate section"""
        try:
            # First check basic bank details
            is_valid, results = self.detect_bank_details(image)
            
            text = self.extract_text(image)
            
            # Additional mandate checks
            mandate_keywords = {
                'authorization': ['authorize', 'authorise', 'mandate'],
                'bank_name': ['bank', 'branch', 'banker'],
                'account_type': ['savings', 'current', 'nre', 'nro']
            }
            
            for check, keywords in mandate_keywords.items():
                results[f'has_{check}'] = any(keyword in text for keyword in keywords)
                
            # Check for dates
            date_pattern = r'\d{2}[-/]\d{2}[-/]\d{2,4}'
            dates = re.findall(date_pattern, text)
            results['has_dates'] = bool(dates)
            
            # Check for signature
            results['has_signature'] = self.detect_signature(image)
            
            # Overall validation - needs bank details and authorization
            is_valid = (is_valid and 
                       results['has_authorization'] and 
                       results['has_bank_name'] and 
                       results['has_signature'])
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating bank mandate: {e}")
            return False, {}

    def validate_declaration(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """Validate declaration section if present"""
        try:
            results = {
                'declaration_found': False,
                'has_signature': False,
                'has_date': False
            }
            
            text = self.extract_text(image)
            
            # Check for declaration text
            declaration_keywords = ['declare', 'confirm', 'agree', 'undertake']
            results['declaration_found'] = any(keyword in text for keyword in declaration_keywords)
            
            # Check for date
            date_pattern = r'\d{2}[-/]\d{2}[-/]\d{2,4}'
            results['has_date'] = bool(re.search(date_pattern, text))
            
            # Check for signature
            results['has_signature'] = self.detect_signature(image)
            
            is_valid = results['declaration_found'] and results['has_signature']
            
            return is_valid, results
            
        except Exception as e:
            self.logger.error(f"Error validating declaration: {e}")
            return False, {}