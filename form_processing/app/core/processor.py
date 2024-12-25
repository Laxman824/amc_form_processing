# import cv2
# import numpy as np
# from pathlib import Path
# import logging
# from typing import Tuple,Dict, List, Optional
# from PIL import Image


# from .detector import FormDetector
# from .validator import SectionValidator

# class FormProcessor:
#     def __init__(self, template_dir: Path = Path("templates")):
#         self.template_dir = template_dir
#         self.detector = FormDetector(template_dir)
#         self.validator = SectionValidator()
#         self.logger = logging.getLogger(__name__)

#     def process_form(self, images: List[np.ndarray]) -> Dict:
#         """Process form images and return results"""
#         try:
#             # Initialize results dictionary
#             results = {
#                 'status': 'success',
#                 'form_type': None,
#                 'total_pages': len(images),
#                 'sip_details_filled': False,
#                 'otm_details_filled': False,
#                 'sections': {},
#                 'confidence': 0.0
#             }

#             # Detect form type from first page
#             form_type, confidence = self.detector.detect_form_type(images)
  
#             results['form_type'] = form_type
#             results['confidence'] = confidence

#             # Get template for detected form type
#             template = self._get_template_for_form(form_type)
#             if not template:
#                 results['status'] = 'error'
#                 results['message'] = 'No matching template found'
#                 return results

#             # Process sections based on form type
#             if form_type == "CA Form":
#                 self._process_caf_form(images, template, results)
#             elif form_type == "SIP Form":
#                 self._process_sip_form(images, template, results)
#             elif form_type == "Multiple SIP Form":
#                 self._process_multiple_sip_form(images, template, results)
#             else:
#                 results['status'] = 'error'
#                 results['message'] = 'Unknown form type'

#             return results

#         except Exception as e:
#             self.logger.error(f"Error processing form: {e}")
#             return {
#                 'status': 'error',
#                 'message': str(e)
#             }

#     def _get_template_for_form(self, form_type: str) -> Optional[Dict]:
#         """Get template for form type"""
#         for template in self.detector.templates.values():
#             if template['form_type'] == form_type:
#                 return template
#         return None

#     def _extract_section(self, image: np.ndarray, section: Dict) -> np.ndarray:
#         """Extract section from image using coordinates"""
#         height, width = image.shape[:2]
#         coords = section['coordinates']
        
#         x1 = int(coords['x'] * width)
#         y1 = int(coords['y'] * height)
#         x2 = int((coords['x'] + coords['width']) * width)
#         y2 = int((coords['y'] + coords['height']) * height)
        
#         return image[y1:y2, x1:x2]

#     def _process_caf_form(self, images: List[np.ndarray], template: Dict, results: Dict):
#         """Process CAF form"""
#         try:
#             # Process Section 8 (page 2)
#             section8_sections = [s for s in template['sections'] 
#                                if s['page'] == 1 and 'section 8' in s['name'].lower()]
            
#             if section8_sections and len(images) > 1:
#                 section_img = self._extract_section(images[1], section8_sections[0])
#                 is_filled, details = self.validator.validate_sip_details(section_img)
#                 results['sections']['section8'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 results['sip_details_filled'] = is_filled

#             # Process OTM Section (page 3)
#             otm_sections = [s for s in template['sections'] 
#                           if s['page'] == 2 and 'otm' in s['name'].lower()]
            
#             if otm_sections and len(images) > 2:
#                 section_img = self._extract_section(images[2], otm_sections[0])
#                 is_filled, details = self.validator.validate_otm_section(section_img)
#                 results['sections']['otm'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 results['otm_details_filled'] = is_filled

#         except Exception as e:
#             self.logger.error(f"Error processing CAF form: {e}")
#             results['status'] = 'error'
#             results['message'] = str(e)

#     def _process_sip_form(self, images: List[np.ndarray], template: Dict, results: Dict):
#         """Process SIP form"""
#         try:
#             # Process Transaction Type section
#             trx_sections = [s for s in template['sections'] 
#                           if s['page'] == 0 and 'transaction' in s['name'].lower()]
            
#             if trx_sections:
#                 section_img = self._extract_section(images[0], trx_sections[0])
#                 is_filled, details = self.validator.validate_transaction_type(section_img)
#                 results['sections']['transaction_type'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }

#             # Process SIP Details section
#             sip_sections = [s for s in template['sections'] 
#                           if s['page'] == 0 and 'sip detail' in s['name'].lower()]
            
#             if sip_sections:
#                 section_img = self._extract_section(images[0], sip_sections[0])
#                 is_filled, details = self.validator.validate_sip_details(section_img)
#                 results['sections']['sip_details'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 results['sip_details_filled'] = is_filled

#             # Process OTM Section (page 2)
#             otm_sections = [s for s in template['sections'] 
#                           if s['page'] == 1 and 'otm' in s['name'].lower()]
            
#             if otm_sections and len(images) > 1:
#                 section_img = self._extract_section(images[1], otm_sections[0])
#                 is_filled, details = self.validator.validate_otm_section(section_img)
#                 results['sections']['otm'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 results['otm_details_filled'] = is_filled

#         except Exception as e:
#             self.logger.error(f"Error processing SIP form: {e}")
#             results['status'] = 'error'
#             results['message'] = str(e)

#     def _process_multiple_sip_form(self, images: List[np.ndarray], template: Dict, results: Dict):
#         """Process Multiple SIP form"""
#         try:
#             # Process Transaction Type
#             trx_sections = [s for s in template['sections'] 
#                           if s['page'] == 0 and 'transaction' in s['name'].lower()]
            
#             if trx_sections:
#                 section_img = self._extract_section(images[0], trx_sections[0])
#                 is_filled, details = self.validator.validate_transaction_type(section_img)
#                 results['sections']['transaction_type'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }

#             # Process each scheme section
#             scheme_sections = [s for s in template['sections'] 
#                              if s['page'] == 0 and 'scheme' in s['name'].lower()]
            
#             results['sections']['schemes'] = {}
#             for section in scheme_sections:
#                 section_img = self._extract_section(images[0], section)
#                 is_filled, details = self.validator.validate_sip_details(section_img)
#                 results['sections']['schemes'][section['name']] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 if is_filled:
#                     results['sip_details_filled'] = True

#             # Process OTM Section
#             otm_sections = [s for s in template['sections'] 
#                           if s['page'] == 1 and 'otm' in s['name'].lower()]
            
#             if otm_sections and len(images) > 1:
#                 section_img = self._extract_section(images[1], otm_sections[0])
#                 is_filled, details = self.validator.validate_otm_section(section_img)
#                 results['sections']['otm'] = {
#                     'filled': is_filled,
#                     'details': details
#                 }
#                 results['otm_details_filled'] = is_filled

#         except Exception as e:
#             self.logger.error(f"Error processing Multiple SIP form: {e}")
#             results['status'] = 'error'
#             results['message'] = str(e)

#     def _validate_section(self, image: np.ndarray, section_type: str, page: int) -> Tuple[bool, Dict]:
#             """Validate specific section based on type"""
#             try:
#                 if section_type == "section8":
#                     return self.caf_validator.validate_section8(image)
#                 elif section_type == "otm":
#                     if self.current_form_type == "CA Form":
#                         return self.caf_validator.validate_otm_section(image)
#                     elif self.current_form_type == "SIP Form":
#                         return self.sip_validator.validate_bank_mandate(image)
#                     else:
#                         return self.multiple_sip_validator.validate_bank_details(image)
#                 elif section_type == "transaction_type":
#                     return self.sip_validator.validate_transaction_type(image)
#                 elif section_type == "sip_details":
#                     return self.sip_validator.validate_sip_details(image)
#                 elif section_type == "scheme":
#                     return self.multiple_sip_validator.validate_scheme(image, page + 1)
#                 else:
#                     self.logger.warning(f"Unknown section type: {section_type}")
#                     return False, {}
                    
#             except Exception as e:
#                 self.logger.error(f"Error validating section {section_type}: {e}")
#                 return False, {'error': str(e)}

#     def validate_form(self, images: List[np.ndarray], template: Dict) -> Dict:
#         """Validate form against template"""
#         results = {
#             'status': 'success',
#             'sections': {},
#             'sip_details_filled': False,
#             'otm_details_filled': False
#         }
        
#         try:
#             for section in template['sections']:
#                 page_num = section['page']
#                 if page_num < len(images):
#                     # Get section image
#                     section_img = self._extract_section(
#                         images[page_num],
#                         section['coordinates']
#                     )
                    
#                     # Validate section
#                     is_valid, section_results = self._validate_section(
#                         section_img,
#                         section['type'],
#                         page_num
#                     )
                    
#                     # Store results
#                     results['sections'][section['name']] = {
#                         'filled': is_valid,
#                         'details': section_results
#                     }
                    
#                     # Update overall status
#                     if 'sip' in section['type'].lower():
#                         results['sip_details_filled'] |= is_valid
#                     elif 'otm' in section['type'].lower():
#                         results['otm_details_filled'] |= is_valid
                        
#         except Exception as e:
#             self.logger.error(f"Error in form validation: {e}")
#             results['status'] = 'error'
#             results['message'] = str(e)
            
#         return results




import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import re

from .detector import FormDetector
from .validators.base_validator import BaseSectionValidator
from .validators.caf_validator import CAFValidator
from .validators.sip_validator import SIPValidator
from .validators.multiple_sip_validator import MultipleSIPValidator
from .validators.ctf_validator import CTFValidator

class FormProcessor:
    def __init__(self, template_dir: Path = Path("templates")):
        self.template_dir = template_dir
        self.setup_logging()
        
        # Initialize detector
        self.detector = FormDetector(template_dir)
        
        # Initialize form-specific validators
        self.caf_validator = CAFValidator()
        self.sip_validator = SIPValidator()
        self.ctf_validator = CTFValidator()
        self.multiple_sip_validator = MultipleSIPValidator()
        
        self.current_form_type = None

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def process_form(self, images: List[np.ndarray]) -> Dict:
        """Process form images and return results"""
        try:
            results = {
                'status': 'success',
                'form_type': None,
                'total_pages': len(images),
                'sip_details_filled': False,
                'otm_details_filled': False,
                'sections': {},
                'confidence': 0.0
            }

            # Detect form type
            form_type, confidence = self.detector.detect_form_type(images)
            self.current_form_type = form_type
            results['form_type'] = form_type
            results['confidence'] = confidence

            self.logger.info(f"Detected form type: {form_type} with confidence: {confidence}")

            if form_type == "CA Form":
                self._process_caf_form(images, results)
            elif form_type == "SIP Form":
                self._process_sip_form(images, results)
            elif form_type == "Multiple SIP Form":
                self._process_multiple_sip_form(images, results)
            elif form_type == "CTF Form":
                self._process_ctf(images, results)
            else:
                results['status'] = 'error'
                results['message'] = 'Unknown form type'

            return results

        except Exception as e:
            self.logger.error(f"Error processing form: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'total_pages': len(images) if images else 0
            }

    def _extract_section(self, image: np.ndarray, section: Dict) -> np.ndarray:
        """Extract section from image using coordinates"""
        height, width = image.shape[:2]
        coords = section['coordinates']
        
        x1 = int(coords['x'] * width)
        y1 = int(coords['y'] * height)
        x2 = int((coords['x'] + coords['width']) * width)
        y2 = int((coords['y'] + coords['height']) * height)
        
        # Ensure coordinates are within bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)
        
        if x2 > x1 and y2 > y1:
            return image[y1:y2, x1:x2]
        else:
            self.logger.error(f"Invalid section coordinates: {coords}")
            return np.array([])

    def _process_caf_form(self, images: List[np.ndarray], results: Dict):
        """Process CAF form"""
        try:
            # Process Section 8 (page 2)
            if len(images) >= 2:
                section8_coords = {
                    'x': 0,
                    'y': 0,
                    'width': 1.0,
                    'height': 0.5
                }
                section8_img = self._extract_section(images[1], {'coordinates': section8_coords})
                is_filled, details = self.caf_validator.validate_section8(section8_img)
                results['sections']['section8'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['sip_details_filled'] = is_filled

            # Process OTM Section (page 3)
            if len(images) >= 3:
                otm_coords = {
                    'x': 0,
                    'y': 0.5,
                    'width': 1.0,
                    'height': 0.5
                }
                otm_img = self._extract_section(images[2], {'coordinates': otm_coords})
                is_filled, details = self.caf_validator.validate_otm_section(otm_img)
                results['sections']['otm'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['otm_details_filled'] = is_filled

            self.logger.info(f"CAF Processing Results - SIP: {results['sip_details_filled']}, OTM: {results['otm_details_filled']}")

        except Exception as e:
            self.logger.error(f"Error processing CAF: {e}")
            results['status'] = 'error'
            results['message'] = f"Error processing CAF: {str(e)}"

    def _process_sip_form(self, images: List[np.ndarray], results: Dict):
        """Process SIP form"""
        try:
            # Process first page sections
            is_valid, trx_results = self.sip_validator.validate_transaction_type(images[0])
            results['sections']['transaction_type'] = {
                'filled': is_valid,
                'details': trx_results
            }

            # Validate SIP Details
            is_valid, sip_results = self.sip_validator.validate_sip_details(images[0])
            results['sections']['sip_details'] = {
                'filled': is_valid,
                'details': sip_results
            }
            results['sip_details_filled'] = is_valid

            # Process OTM Section (page 2)
            if len(images) >= 2:
                is_valid, otm_results = self.sip_validator.validate_bank_mandate(images[1])
                results['sections']['otm'] = {
                    'filled': is_valid,
                    'details': otm_results
                }
                results['otm_details_filled'] = is_valid

        except Exception as e:
            self.logger.error(f"Error processing SIP: {e}")
            results['status'] = 'error'
            results['message'] = f"Error processing SIP: {str(e)}"

    def _process_multiple_sip_form(self, images: List[np.ndarray], results: Dict):
        """Process Multiple SIP form"""
        try:
            # Validate all schemes
            is_valid, schemes_results = self.multiple_sip_validator.validate_all_schemes(images)
            results['sections']['schemes'] = schemes_results
            results['sip_details_filled'] = is_valid

            # Process bank details
            if len(images) >= 2:
                is_valid, bank_results = self.multiple_sip_validator.validate_bank_details(images[1])
                results['sections']['bank_details'] = bank_results
                results['otm_details_filled'] = is_valid

        except Exception as e:
            self.logger.error(f"Error processing Multiple SIP: {e}")
            results['status'] = 'error'
            results['message'] = f"Error processing Multiple SIP: {str(e)}"


    def _process_ctf(self, images: List[np.ndarray], results: Dict):
        """Process CTF form"""
        try:
            # Validate complete form
            ctf_results = self.ctf_validator.validate_form(images)
            
            # Update results
            results.update(ctf_results)
            
            # If SIP form is attached, validate it
            if ctf_results.get('has_sip_form') and len(images) > 1:
                sip_page = ctf_results['sip_form_details']['sip_form_page']
                if sip_page < len(images):
                    # Process SIP form
                    sip_image = images[sip_page]
                    self._process_sip_form([sip_image], results)
            
            self.logger.info(f"CTF Processing Results: {results['transactions']}")
            
        except Exception as e:
            self.logger.error(f"Error processing CTF: {e}")
            results['status'] = 'error'
            results['message'] = f"Error processing CTF: {str(e)}"