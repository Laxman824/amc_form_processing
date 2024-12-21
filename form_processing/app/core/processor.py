# import cv2
# import numpy as np
# from typing import List, Dict, Optional
# from pathlib import Path
# import json
# from datetime import datetime

# from ..models.form import FormType, FormValidation, ValidationStatus, SectionValidation

# class FormProcessor:
#     def __init__(self, template_dir: Path = Path("templates")):
#         self.template_dir = template_dir
#         self.templates = self._load_templates()
        
#     def _load_templates(self) -> Dict:
#         """Load all templates from template directory"""
#         templates = {}
#         if self.template_dir.exists():
#             for file in self.template_dir.glob("*.json"):
#                 with open(file, "r") as f:
#                     templates[file.stem] = json.load(f)
#         return templates

#     def process_form(self, images: List[np.ndarray]) -> FormValidation:
#         """Process form images and return validation results"""
#         try:
#             # Basic validation
#             if not images:
#                 return FormValidation(
#                     form_type=FormType.OTHER,
#                     total_pages=0,
#                     sections=[],
#                 )

#             # Process first page for form type identification
#             form_type = self._identify_form_type(images[0])
            
#             # Create basic validation result
#             sections = [
#                 SectionValidation(
#                     section_name="Form Identification",
#                     status=ValidationStatus.VALID if form_type != FormType.OTHER else ValidationStatus.WARNING,
#                     details={"identified_type": form_type.value},
#                     confidence=0.8 if form_type != FormType.OTHER else 0.3
#                 )
#             ]

#             return FormValidation(
#                 form_type=form_type,
#                 total_pages=len(images),
#                 sections=sections,
#                 sip_details_filled=False,  # To be implemented
#                 otm_details_filled=False   # To be implemented
#             )

#         except Exception as e:
#             # Return error validation
#             return FormValidation(
#                 form_type=FormType.OTHER,
#                 total_pages=len(images) if images else 0,
#                 sections=[
#                     SectionValidation(
#                         section_name="Error",
#                         status=ValidationStatus.INVALID,
#                         details={"error": str(e)},
#                         confidence=0.0
#                     )
#                 ]
#             )

#     def _identify_form_type(self, image: np.ndarray) -> FormType:
#         """Placeholder for form type identification"""
#         # TODO: Implement actual form type identification
#         return FormType.OTHER

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Optional
from PIL import Image

from .detector import FormDetector
from .validator import SectionValidator

class FormProcessor:
    def __init__(self, template_dir: Path = Path("templates")):
        self.template_dir = template_dir
        self.detector = FormDetector(template_dir)
        self.validator = SectionValidator()
        self.logger = logging.getLogger(__name__)

    def process_form(self, images: List[np.ndarray]) -> Dict:
        """Process form images and return results"""
        try:
            # Initialize results dictionary
            results = {
                'status': 'success',
                'form_type': None,
                'total_pages': len(images),
                'sip_details_filled': False,
                'otm_details_filled': False,
                'sections': {},
                'confidence': 0.0
            }

            # Detect form type from first page
            form_type, confidence = self.detector.detect_form_type(images[0])
            results['form_type'] = form_type
            results['confidence'] = confidence

            # Get template for detected form type
            template = self._get_template_for_form(form_type)
            if not template:
                results['status'] = 'error'
                results['message'] = 'No matching template found'
                return results

            # Process sections based on form type
            if form_type == "CA Form":
                self._process_caf_form(images, template, results)
            elif form_type == "SIP Form":
                self._process_sip_form(images, template, results)
            elif form_type == "Multiple SIP Form":
                self._process_multiple_sip_form(images, template, results)
            else:
                results['status'] = 'error'
                results['message'] = 'Unknown form type'

            return results

        except Exception as e:
            self.logger.error(f"Error processing form: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _get_template_for_form(self, form_type: str) -> Optional[Dict]:
        """Get template for form type"""
        for template in self.detector.templates.values():
            if template['form_type'] == form_type:
                return template
        return None

    def _extract_section(self, image: np.ndarray, section: Dict) -> np.ndarray:
        """Extract section from image using coordinates"""
        height, width = image.shape[:2]
        coords = section['coordinates']
        
        x1 = int(coords['x'] * width)
        y1 = int(coords['y'] * height)
        x2 = int((coords['x'] + coords['width']) * width)
        y2 = int((coords['y'] + coords['height']) * height)
        
        return image[y1:y2, x1:x2]

    def _process_caf_form(self, images: List[np.ndarray], template: Dict, results: Dict):
        """Process CAF form"""
        try:
            # Process Section 8 (page 2)
            section8_sections = [s for s in template['sections'] 
                               if s['page'] == 1 and 'section 8' in s['name'].lower()]
            
            if section8_sections and len(images) > 1:
                section_img = self._extract_section(images[1], section8_sections[0])
                is_filled, details = self.validator.validate_sip_details(section_img)
                results['sections']['section8'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['sip_details_filled'] = is_filled

            # Process OTM Section (page 3)
            otm_sections = [s for s in template['sections'] 
                          if s['page'] == 2 and 'otm' in s['name'].lower()]
            
            if otm_sections and len(images) > 2:
                section_img = self._extract_section(images[2], otm_sections[0])
                is_filled, details = self.validator.validate_otm_section(section_img)
                results['sections']['otm'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['otm_details_filled'] = is_filled

        except Exception as e:
            self.logger.error(f"Error processing CAF form: {e}")
            results['status'] = 'error'
            results['message'] = str(e)

    def _process_sip_form(self, images: List[np.ndarray], template: Dict, results: Dict):
        """Process SIP form"""
        try:
            # Process Transaction Type section
            trx_sections = [s for s in template['sections'] 
                          if s['page'] == 0 and 'transaction' in s['name'].lower()]
            
            if trx_sections:
                section_img = self._extract_section(images[0], trx_sections[0])
                is_filled, details = self.validator.validate_transaction_type(section_img)
                results['sections']['transaction_type'] = {
                    'filled': is_filled,
                    'details': details
                }

            # Process SIP Details section
            sip_sections = [s for s in template['sections'] 
                          if s['page'] == 0 and 'sip detail' in s['name'].lower()]
            
            if sip_sections:
                section_img = self._extract_section(images[0], sip_sections[0])
                is_filled, details = self.validator.validate_sip_details(section_img)
                results['sections']['sip_details'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['sip_details_filled'] = is_filled

            # Process OTM Section (page 2)
            otm_sections = [s for s in template['sections'] 
                          if s['page'] == 1 and 'otm' in s['name'].lower()]
            
            if otm_sections and len(images) > 1:
                section_img = self._extract_section(images[1], otm_sections[0])
                is_filled, details = self.validator.validate_otm_section(section_img)
                results['sections']['otm'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['otm_details_filled'] = is_filled

        except Exception as e:
            self.logger.error(f"Error processing SIP form: {e}")
            results['status'] = 'error'
            results['message'] = str(e)

    def _process_multiple_sip_form(self, images: List[np.ndarray], template: Dict, results: Dict):
        """Process Multiple SIP form"""
        try:
            # Process Transaction Type
            trx_sections = [s for s in template['sections'] 
                          if s['page'] == 0 and 'transaction' in s['name'].lower()]
            
            if trx_sections:
                section_img = self._extract_section(images[0], trx_sections[0])
                is_filled, details = self.validator.validate_transaction_type(section_img)
                results['sections']['transaction_type'] = {
                    'filled': is_filled,
                    'details': details
                }

            # Process each scheme section
            scheme_sections = [s for s in template['sections'] 
                             if s['page'] == 0 and 'scheme' in s['name'].lower()]
            
            results['sections']['schemes'] = {}
            for section in scheme_sections:
                section_img = self._extract_section(images[0], section)
                is_filled, details = self.validator.validate_sip_details(section_img)
                results['sections']['schemes'][section['name']] = {
                    'filled': is_filled,
                    'details': details
                }
                if is_filled:
                    results['sip_details_filled'] = True

            # Process OTM Section
            otm_sections = [s for s in template['sections'] 
                          if s['page'] == 1 and 'otm' in s['name'].lower()]
            
            if otm_sections and len(images) > 1:
                section_img = self._extract_section(images[1], otm_sections[0])
                is_filled, details = self.validator.validate_otm_section(section_img)
                results['sections']['otm'] = {
                    'filled': is_filled,
                    'details': details
                }
                results['otm_details_filled'] = is_filled

        except Exception as e:
            self.logger.error(f"Error processing Multiple SIP form: {e}")
            results['status'] = 'error'
            results['message'] = str(e)