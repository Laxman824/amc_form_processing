# import cv2
# import numpy as np
# from pathlib import Path
# import logging
# from typing import Dict, List, Optional
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
#             form_type, confidence = self.detector.detect_form_type(images[0])
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

import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
import logging
from typing import Dict, List, Optional, Union

from .detector import FormDetector
from .validators.caf_validator import CAFValidator
from .validators.sip_validator import SIPValidator
from .validators.multiple_sip_validator import MultipleSIPValidator

class FormProcessor:
    def __init__(self, template_dir: Path = Path("templates")):
        self.logger = logging.getLogger(__name__)
        self.detector = FormDetector(template_dir)
        self.caf_validator = CAFValidator()
        self.sip_validator = SIPValidator()
        self.multiple_sip_validator = MultipleSIPValidator()

    def convert_pdf_to_images(self, pdf_bytes: bytes) -> List[np.ndarray]:
        """Convert PDF to list of images using PyMuPDF"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            
            for page_num in range(len(doc)):
                # Get page
                page = doc[page_num]
                # Higher zoom factor for better quality
                zoom = 2
                matrix = fitz.Matrix(zoom, zoom)
                
                # Get page as pixmap
                pix = page.get_pixmap(matrix=matrix)
                
                # Convert to bytes
                img_bytes = pix.tobytes("png")
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_bytes))
                # Convert to numpy array
                img_array = np.array(img)
                
                if img_array is not None and img_array.size > 0:
                    images.append(img_array)
                else:
                    self.logger.error(f"Error: Empty image for page {page_num + 1}")
            
            doc.close()
            return images
            
        except Exception as e:
            self.logger.error(f"Error converting PDF: {e}")
            raise

    def process_form(self, images: List[Union[np.ndarray, bytes]], file_type: str = 'image') -> Dict:
        """Process form images and return results"""
        try:
            # Convert PDF if needed
            if file_type == 'pdf':
                images = self.convert_pdf_to_images(images[0])  # First element is PDF bytes

            # Validate images
            if not images or not isinstance(images[0], np.ndarray):
                raise ValueError("Invalid or empty images")

            # Initialize results
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
            try:
                form_type, confidence = self.detector.detect_form_type(images[0])
                results['form_type'] = form_type
                results['confidence'] = confidence
            except Exception as e:
                self.logger.error(f"Error in form detection: {e}")
                results['form_type'] = "Unknown"
                results['confidence'] = 0.0

            # Process based on form type
            try:
                if form_type == "CA Form":
                    self._process_caf(images, results)
                elif form_type == "SIP Form":
                    self._process_sip(images, results)
                elif form_type == "Multiple SIP Form":
                    self._process_multiple_sip(images, results)
                else:
                    results['status'] = 'warning'
                    results['message'] = 'Unknown form type'
            except Exception as e:
                self.logger.error(f"Error processing form sections: {e}")
                results['status'] = 'error'
                results['message'] = str(e)

            return results

        except Exception as e:
            self.logger.error(f"Error in process_form: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'total_pages': len(images) if isinstance(images, list) else 0
            }

    def _process_caf(self, images: List[np.ndarray], results: Dict):
        """Process CAF form"""
        if len(images) >= 2:
            # Validate Section 8 (page 2)
            is_valid, section8_results = self.caf_validator.validate_section8(images[1])
            results['sections']['section8'] = section8_results
            results['sip_details_filled'] = is_valid

        if len(images) >= 3:
            # Validate OTM Section (page 3)
            is_valid, otm_results = self.caf_validator.validate_otm_section(images[2])
            results['sections']['otm'] = otm_results
            results['otm_details_filled'] = is_valid

    def _process_sip(self, images: List[np.ndarray], results: Dict):
        """Process SIP form"""
        # Validate first page sections
        is_valid, trx_results = self.sip_validator.validate_transaction_type(images[0])
        results['sections']['transaction_type'] = trx_results

        is_valid, sip_results = self.sip_validator.validate_sip_details(images[0])
        results['sections']['sip_details'] = sip_results
        results['sip_details_filled'] = is_valid

        if len(images) >= 2:
            # Validate OTM Section (page 2)
            is_valid, otm_results = self.sip_validator.validate_bank_mandate(images[1])
            results['sections']['otm'] = otm_results
            results['otm_details_filled'] = is_valid

    def _process_multiple_sip(self, images: List[np.ndarray], results: Dict):
        """Process Multiple SIP form"""
        # Validate schemes on first page
        is_valid, schemes_results = self.multiple_sip_validator.validate_all_schemes(images)
        results['sections']['schemes'] = schemes_results
        results['sip_details_filled'] = is_valid

        if len(images) >= 2:
            # Validate bank details on second page
            is_valid, bank_results = self.multiple_sip_validator.validate_bank_details(images[1])
            results['sections']['bank_details'] = bank_results
            results['otm_details_filled'] = is_valid