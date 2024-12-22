import unittest
import cv2
import numpy as np
from pathlib import Path
import fitz
from ..core.validators.base_validator import BaseSectionValidator
from ..core.validators.caf_validator import CAFValidator
from ..core.validators.sip_validator import SIPValidator
from ..core.validators.multiple_sip_validator import MultipleSIPValidator
from .test_data import TEST_CASES, VALIDATION_PATTERNS

class TestValidators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_validator = BaseSectionValidator()
        cls.caf_validator = CAFValidator()
        cls.sip_validator = SIPValidator()
        cls.multiple_sip_validator = MultipleSIPValidator()
        cls.load_test_data()

    @classmethod
    def load_test_data(cls):
        """Load test PDFs and convert to images"""
        cls.test_images = {}
        for test_case in TEST_CASES:
            file_path = Path(test_case.file_path)
            if file_path.exists():
                doc = fitz.open(file_path)
                images = []
                for page in doc:
                    pix = page.get_pixmap()
                    img = np.frombuffer(pix.samples, dtype=np.uint8)
                    img = img.reshape(pix.height, pix.width, 3)
                    images.append(img)
                cls.test_images[test_case.name] = images
                doc.close()

    def test_base_validator_text_extraction(self):
        """Test text extraction from base validator"""
        for test_name, images in self.test_images.items():
            with self.subTest(test_name=test_name):
                # Test first page
                text = self.base_validator.extract_text(images[0])
                self.assertIsInstance(text, str)
                self.assertGreater(len(text), 0)

    def test_base_validator_checkbox_detection(self):
        """Test checkbox detection"""
        # Create a test image with a checked checkbox
        checkbox_img = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(checkbox_img, (10, 10), (30, 30), 255, -1)
        
        is_checked = self.base_validator.detect_checkbox_state(checkbox_img)
        self.assertTrue(is_checked)

    def test_caf_validator_section8(self):
        """Test CAF validator Section 8 validation"""
        caf_images = self.test_images.get('CAF_Complete')
        if caf_images and len(caf_images) > 1:
            is_valid, results = self.caf_validator.validate_section8(caf_images[1])
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(results, dict)
            self.assertIn('sip_details_filled', results)

    def test_sip_validator_transaction_type(self):
        """Test SIP validator transaction type validation"""
        sip_images = self.test_images.get('SIP_Complete')
        if sip_images:
            is_valid, results = self.sip_validator.validate_transaction_type(sip_images[0])
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(results, dict)
            self.assertIn('type_detected', results)

    def test_pattern_matching(self):
        """Test regex pattern matching"""
        # Test valid patterns
        test_data = {
            'bank_account': '123456789012',
            'ifsc': 'HDFC0123456',
            'pan': 'ABCDE1234F',
            'amount': 'Rs. 1,234.56'
        }
        
        for field, pattern in VALIDATION_PATTERNS.items():
            with self.subTest(field=field):
                import re
                match = re.search(pattern, test_data[field])
                self.assertIsNotNone(match, f"Pattern failed for {field}")

    def test_bank_details_validation(self):
        """Test bank details validation across validators"""
        validators = [
            self.caf_validator,
            self.sip_validator,
            self.multiple_sip_validator
        ]
        
        for validator in validators:
            with self.subTest(validator=validator.__class__.__name__):
                # Test with OTM section from test images
                for test_name, images in self.test_images.items():
                    if len(images) > 2:  # If OTM section exists
                        is_valid, results = validator.validate_otm_section(images[2])
                        self.assertIsInstance(is_valid, bool)
                        self.assertIsInstance(results, dict)
                        self.assertIn('account_number_found', results)
                        self.assertIn('ifsc_found', results)

if __name__ == '__main__':
    unittest.main()