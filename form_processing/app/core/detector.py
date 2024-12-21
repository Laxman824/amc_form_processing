# import cv2
# import numpy as np
# import pytesseract
# from typing import Dict, Tuple, Optional
# import re
# from Levenshtein import ratio
# import logging
# from pathlib import Path
# from ..models.form import FormType
# from ..models.template import Template
# from ..utils.image import preprocess_image

# class FormDetector:
#     def __init__(self, template_dir: Path = Path("templates")):
#         self.template_dir = template_dir
#         self.templates = self._load_templates()
#         self.setup_logging()
        
#         # Form type keywords and patterns
#         self.form_patterns = {
#             FormType.CAF: {
#                 'keywords': ['common application form', 'caf', 'multiple schemes'],
#                 'identifiers': ['section 8', 'nominee details', 'bank details'],
#                 'threshold': 0.8,
#                 'weight': 1.0
#             },
#             FormType.SIP: {
#                 'keywords': ['sip & sip-top up registration', 'sip registration', 'sip with top-up'],
#                 'identifiers': ['frequency', 'sip period', 'sip amount'],
#                 'threshold': 0.8,
#                 'weight': 1.0
#             },
#             FormType.MULTIPLE_SIP: {
#                 'keywords': ['multiple sip', 'multiple registration', 'scheme 1', 'scheme 2'],
#                 'identifiers': ['multiple schemes', 'scheme selection'],
#                 'threshold': 0.8,
#                 'weight': 1.2  # Higher weight for more specific form
#             }
#         }

#     def setup_logging(self):
#         """Setup logging configuration"""
#         self.logger = logging.getLogger(__name__)

#     def _load_templates(self) -> Dict[str, Template]:
#         """Load templates for reference"""
#         templates = {}
#         if self.template_dir.exists():
#             for file in self.template_dir.glob("*.json"):
#                 with open(file, "r") as f:
#                     templates[file.stem] = Template.from_dict(json.load(f))
#         return templates

#     def identify_form_type(self, image: np.ndarray) -> Tuple[FormType, float]:
#         """
#         Identify form type from image using multiple methods
#         Returns: (FormType, confidence_score)
#         """
#         # Preprocess image
#         processed_img = preprocess_image(image)
        
#         # Extract text from header region (top 20% of image)
#         h, w = processed_img.shape[:2]
#         header = processed_img[0:int(0.2*h), :]
#         header_text = pytesseract.image_to_string(header).lower()
        
#         # Extract text from full page for context
#         full_text = pytesseract.image_to_string(processed_img).lower()
        
#         # Store scores for each form type
#         scores = {form_type: 0.0 for form_type in FormType}
        
#         for form_type, patterns in self.form_patterns.items():
#             # Check keywords in header
#             header_score = self._check_keywords(
#                 header_text,
#                 patterns['keywords'],
#                 patterns['threshold']
#             ) * 2.0  # Header matches are more important
            
#             # Check identifiers in full text
#             text_score = self._check_keywords(
#                 full_text,
#                 patterns['identifiers'],
#                 patterns['threshold']
#             )
            
#             # Check layout similarity with templates
#             layout_score = self._check_layout_similarity(
#                 processed_img,
#                 form_type
#             )
            
#             # Combine scores with weights
#             total_score = (
#                 header_score * 0.5 +
#                 text_score * 0.3 +
#                 layout_score * 0.2
#             ) * patterns['weight']
            
#             scores[form_type] = total_score
            
#             self.logger.debug(f"Form type {form_type.value} scores:")
#             self.logger.debug(f"Header: {header_score}, Text: {text_score}, Layout: {layout_score}")
#             self.logger.debug(f"Total weighted score: {total_score}")

#         # Get form type with highest score
#         best_form_type = max(scores.items(), key=lambda x: x[1])
        
#         # If score is too low, return OTHER
#         if best_form_type[1] < 0.4:  # Threshold for minimum confidence
#             return FormType.OTHER, 0.0
            
#         return best_form_type[0], best_form_type[1]

#     def _check_keywords(self, text: str, keywords: list, threshold: float) -> float:
#         """Check for keywords in text using fuzzy matching"""
#         max_scores = []
        
#         for keyword in keywords:
#             # Try exact match first
#             if keyword in text:
#                 max_scores.append(1.0)
#                 continue
                
#             # Try fuzzy matching
#             word_scores = []
#             for word in text.split():
#                 word_scores.append(ratio(keyword, word))
            
#             if word_scores:
#                 max_scores.append(max(word_scores))
        
#         # Return average of top scores above threshold
#         valid_scores = [s for s in max_scores if s >= threshold]
#         return sum(valid_scores) / len(keywords) if valid_scores else 0.0

#     def _check_layout_similarity(self, image: np.ndarray, form_type: FormType) -> float:
#         """Check layout similarity with template"""
#         # Get template for form type
#         template = next((t for t in self.templates.values() 
#                         if t.form_type == form_type.value), None)
        
#         if not template:
#             return 0.0
            
#         # Extract structural features
#         lines = self._extract_lines(image)
#         boxes = self._extract_boxes(image)
        
#         # Compare with template features
#         # This is a simplified comparison - could be enhanced
#         template_features = self._get_template_features(template)
        
#         similarity = self._compare_features(
#             (lines, boxes),
#             template_features
#         )
        
#         return similarity

#     def _extract_lines(self, image: np.ndarray) -> list:
#         """Extract horizontal and vertical lines from image"""
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
#         # Edge detection
#         edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
#         # Detect lines using HoughLinesP
#         lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
#         return lines if lines is not None else []

#     def _extract_boxes(self, image: np.ndarray) -> list:
#         """Extract rectangles/boxes from image"""
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
#         # Threshold
#         _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
#         # Find contours
#         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         # Filter rectangles
#         boxes = []
#         for cnt in contours:
#             rect = cv2.minAreaRect(cnt)
#             boxes.append(rect)
            
#         return boxes

#     def _get_template_features(self, template: Template) -> Tuple[list, list]:
#         """Get features from template for comparison"""
#         # This would extract features from the template's identifier marks
#         # For now, return empty lists as placeholder
#         return [], []

#     def _compare_features(self, image_features: Tuple[list, list],
#                          template_features: Tuple[list, list]) -> float:
#         """Compare extracted features with template features"""
#         # This is a placeholder for more sophisticated comparison
#         # Could implement feature matching, structural similarity, etc.
#         return 0.5  # Default middle score

import json
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import logging
from typing import Dict, List, Optional, Tuple

class FormDetector:
    def __init__(self, template_dir: Path = Path("templates")):
        self.template_dir = template_dir
        self.templates = self._load_templates()
        self.logger = logging.getLogger(__name__)

    def _load_templates(self) -> Dict:
        """Load all saved templates"""
        templates = {}
        if self.template_dir.exists():
            for file in self.template_dir.glob("*.json"):
                try:
                    with open(file, "r") as f:
                        templates[file.stem] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading template {file}: {e}")
        return templates

    def match_template(self, image: np.ndarray, template_data: Dict) -> float:
        """Match image against a template"""
        confidence = 0.0
        try:
            # Get all sections from the first page
            first_page_sections = [
                s for s in template_data['sections'] 
                if s['page'] == 0
            ]
            
            if not first_page_sections:
                return 0.0

            # Convert coordinates to absolute
            height, width = image.shape[:2]
            total_matches = 0
            
            for section in first_page_sections:
                coords = section['coordinates']
                x1 = int(coords['x'] * width)
                y1 = int(coords['y'] * height)
                x2 = int((coords['x'] + coords['width']) * width)
                y2 = int((coords['y'] + coords['height']) * height)
                
                # Extract section from image
                section_img = image[y1:y2, x1:x2]
                
                # Convert to grayscale
                if len(section_img.shape) == 3:
                    section_img = cv2.cvtColor(section_img, cv2.COLOR_BGR2GRAY)
                
                # Match structural features
                features_score = self._match_features(section_img)
                total_matches += features_score
            
            confidence = total_matches / len(first_page_sections)
            
        except Exception as e:
            self.logger.error(f"Error matching template: {e}")
            
        return confidence

    def _match_features(self, image: np.ndarray) -> float:
        """Match structural features of a section"""
        try:
            # Detect edges
            edges = cv2.Canny(image, 50, 150)
            
            # Detect lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                                  minLineLength=50, maxLineGap=10)
            
            # Detect text-like regions
            text_regions = self._detect_text_regions(image)
            
            # Calculate feature score
            if lines is not None and text_regions > 0:
                return min(1.0, (len(lines) + text_regions) / 20)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error matching features: {e}")
            return 0.0

    def _detect_text_regions(self, image: np.ndarray) -> int:
        """Detect potential text regions"""
        try:
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Find contours
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours that might be text
            text_regions = sum(
                1 for cnt in contours
                if 10 < cv2.contourArea(cnt) < 1000
            )
            
            return text_regions
            
        except Exception as e:
            self.logger.error(f"Error detecting text regions: {e}")
            return 0

    def detect_form_type(self, image: np.ndarray) -> Tuple[str, float]:
        """Detect form type from image"""
        best_match = None
        best_confidence = 0.0
        
        try:
            # Match against each template
            for template_name, template_data in self.templates.items():
                confidence = self.match_template(image, template_data)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = template_data['form_type']
                    
            if best_confidence > 0.7:  # Confidence threshold
                return best_match, best_confidence
            else:
                return "Unknown", best_confidence
                
        except Exception as e:
            self.logger.error(f"Error in form detection: {e}")
            return "Error", 0.0