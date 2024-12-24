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

    def _validate_section(self, image: np.ndarray, section_type: str, page: int) -> Tuple[bool, Dict]:
            """Validate specific section based on type"""
            try:
                if section_type == "section8":
                    return self.caf_validator.validate_section8(image)
                elif section_type == "otm":
                    if self.current_form_type == "CA Form":
                        return self.caf_validator.validate_otm_section(image)
                    elif self.current_form_type == "SIP Form":
                        return self.sip_validator.validate_bank_mandate(image)
                    else:
                        return self.multiple_sip_validator.validate_bank_details(image)
                elif section_type == "transaction_type":
                    return self.sip_validator.validate_transaction_type(image)
                elif section_type == "sip_details":
                    return self.sip_validator.validate_sip_details(image)
                elif section_type == "scheme":
                    return self.multiple_sip_validator.validate_scheme(image, page + 1)
                else:
                    self.logger.warning(f"Unknown section type: {section_type}")
                    return False, {}
                    
            except Exception as e:
                self.logger.error(f"Error validating section {section_type}: {e}")
                return False, {'error': str(e)}

    def validate_form(self, images: List[np.ndarray], template: Dict) -> Dict:
        """Validate form against template"""
        results = {
            'status': 'success',
            'sections': {},
            'sip_details_filled': False,
            'otm_details_filled': False
        }
        
        try:
            for section in template['sections']:
                page_num = section['page']
                if page_num < len(images):
                    # Get section image
                    section_img = self._extract_section(
                        images[page_num],
                        section['coordinates']
                    )
                    
                    # Validate section
                    is_valid, section_results = self._validate_section(
                        section_img,
                        section['type'],
                        page_num
                    )
                    
                    # Store results
                    results['sections'][section['name']] = {
                        'filled': is_valid,
                        'details': section_results
                    }
                    
                    # Update overall status
                    if 'sip' in section['type'].lower():
                        results['sip_details_filled'] |= is_valid
                    elif 'otm' in section['type'].lower():
                        results['otm_details_filled'] |= is_valid
                        
        except Exception as e:
            self.logger.error(f"Error in form validation: {e}")
            results['status'] = 'error'
            results['message'] = str(e)
            
        return results