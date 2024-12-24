# import json
# from pathlib import Path
# import numpy as np
# from PIL import Image
# import cv2
# import logging
# from typing import Dict, List, Optional, Tuple

# class FormDetector:
#     def __init__(self, template_dir: Path = Path("templates")):
#         self.template_dir = template_dir
#         self.templates = self._load_templates()
#         self.logger = logging.getLogger(__name__)

#     def _load_templates(self) -> Dict:
#         """Load all saved templates"""
#         templates = {}
#         if self.template_dir.exists():
#             for file in self.template_dir.glob("*.json"):
#                 try:
#                     with open(file, "r") as f:
#                         templates[file.stem] = json.load(f)
#                 except Exception as e:
#                     self.logger.error(f"Error loading template {file}: {e}")
#         return templates

#     def match_template(self, image: np.ndarray, template_data: Dict) -> float:
#         """Match image against a template"""
#         confidence = 0.0
#         try:
#             # Get all sections from the first page
#             first_page_sections = [
#                 s for s in template_data['sections'] 
#                 if s['page'] == 0
#             ]
            
#             if not first_page_sections:
#                 return 0.0

#             # Convert coordinates to absolute
#             height, width = image.shape[:2]
#             total_matches = 0
            
#             for section in first_page_sections:
#                 coords = section['coordinates']
#                 x1 = int(coords['x'] * width)
#                 y1 = int(coords['y'] * height)
#                 x2 = int((coords['x'] + coords['width']) * width)
#                 y2 = int((coords['y'] + coords['height']) * height)
                
#                 # Extract section from image
#                 section_img = image[y1:y2, x1:x2]
                
#                 # Convert to grayscale
#                 if len(section_img.shape) == 3:
#                     section_img = cv2.cvtColor(section_img, cv2.COLOR_BGR2GRAY)
                
#                 # Match structural features
#                 features_score = self._match_features(section_img)
#                 total_matches += features_score
            
#             confidence = total_matches / len(first_page_sections)
            
#         except Exception as e:
#             self.logger.error(f"Error matching template: {e}")
            
#         return confidence

#     def _match_features(self, image: np.ndarray) -> float:
#         """Match structural features of a section"""
#         try:
#             # Detect edges
#             edges = cv2.Canny(image, 50, 150)
            
#             # Detect lines
#             lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
#                                   minLineLength=50, maxLineGap=10)
            
#             # Detect text-like regions
#             text_regions = self._detect_text_regions(image)
            
#             # Calculate feature score
#             if lines is not None and text_regions > 0:
#                 return min(1.0, (len(lines) + text_regions) / 20)
            
#             return 0.0
            
#         except Exception as e:
#             self.logger.error(f"Error matching features: {e}")
#             return 0.0

#     def _detect_text_regions(self, image: np.ndarray) -> int:
#         """Detect potential text regions"""
#         try:
#             # Apply adaptive thresholding
#             thresh = cv2.adaptiveThreshold(
#                 image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                 cv2.THRESH_BINARY_INV, 11, 2
#             )
            
#             # Find contours
#             contours, _ = cv2.findContours(
#                 thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#             )
            
#             # Filter contours that might be text
#             text_regions = sum(
#                 1 for cnt in contours
#                 if 10 < cv2.contourArea(cnt) < 1000
#             )
            
#             return text_regions
            
#         except Exception as e:
#             self.logger.error(f"Error detecting text regions: {e}")
#             return 0

#     def detect_form_type(self, image: np.ndarray) -> Tuple[str, float]:
#         """Detect form type from image"""
#         best_match = None
#         best_confidence = 0.0
        
#         try:
#             # Match against each template
#             for template_name, template_data in self.templates.items():
#                 confidence = self.match_template(image, template_data)
                
#                 if confidence > best_confidence:
#                     best_confidence = confidence
#                     best_match = template_data['form_type']
                    
#             if best_confidence > 0.7:  # Confidence threshold
#                 return best_match, best_confidence
#             else:
#                 return "Unknown", best_confidence
                
#         except Exception as e:
#             self.logger.error(f"Error in form detection: {e}")
#             return "Error", 0.0

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
        self.setup_logging()  # Setup logging first
        self.templates = self._load_templates()
        self.confidence_threshold = 0.5

    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_templates(self) -> Dict:
        """Load all saved templates"""
        templates = {}
        if self.template_dir.exists():
            for file in self.template_dir.glob("*.json"):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        self.logger.info(f"Loaded template: {file.stem} ({data['form_type']})")
                        templates[file.stem] = data
                except Exception as e:
                    self.logger.error(f"Error loading template {file}: {e}")
        return templates

    def match_template(self, images: List[np.ndarray], template_data: Dict) -> float:
        """Match images against a template"""
        try:
            total_confidence = 0.0
            sections_checked = 0
            
            # Get sections grouped by page
            sections_by_page = {}
            for section in template_data['sections']:
                page = section['page']
                if page not in sections_by_page:
                    sections_by_page[page] = []
                sections_by_page[page].append(section)
                
            # Check each page that has sections
            for page_num, sections in sections_by_page.items():
                if page_num < len(images):  # Make sure we have this page
                    image = images[page_num]
                    page_confidence = self._match_page_sections(image, sections)
                    total_confidence += page_confidence
                    sections_checked += len(sections)

            # Calculate average confidence
            return total_confidence / sections_checked if sections_checked > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error in match_template: {e}")
            return 0.0

    def _match_page_sections(self, image: np.ndarray, sections: List[Dict]) -> float:
        """Match sections on a single page"""
        try:
            height, width = image.shape[:2]
            total_score = 0.0
            
            for section in sections:
                coords = section['coordinates']
                x1 = int(coords['x'] * width)
                y1 = int(coords['y'] * height)
                x2 = int((coords['x'] + coords['width']) * width)
                y2 = int((coords['y'] + coords['height']) * height)
                
                # Ensure coordinates are within bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                if x2 > x1 and y2 > y1:  # Valid section size
                    section_img = image[y1:y2, x1:x2]
                    if len(section_img.shape) == 3:
                        section_img = cv2.cvtColor(section_img, cv2.COLOR_BGR2GRAY)
                    
                    feature_score = self._match_features(section_img)
                    total_score += feature_score
                    
                    self.logger.debug(f"Section {section['name']} score: {feature_score}")
            
            return total_score / len(sections) if sections else 0.0
            
        except Exception as e:
            self.logger.error(f"Error matching page sections: {e}")
            return 0.0

    def _match_features(self, image: np.ndarray) -> float:
        """Match structural features of a section"""
        try:
            # Enhance image
            enhanced = cv2.equalizeHist(image)
            
            # Detect edges
            edges = cv2.Canny(enhanced, 50, 150)
            
            # Detect lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                                  minLineLength=30, maxLineGap=20)
            
            # Detect text regions
            text_regions = self._detect_text_regions(enhanced)
            
            # Calculate combined score
            line_score = len(lines) / 10 if lines is not None else 0
            text_score = text_regions / 20
            
            total_score = (line_score + text_score) / 2
            return min(1.0, total_score)
            
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
            text_regions = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 10 < area < 1000:
                    text_regions += 1
            
            return text_regions
            
        except Exception as e:
            self.logger.error(f"Error detecting text regions: {e}")
            return 0

    def detect_form_type(self, images: List[np.ndarray]) -> Tuple[str, float]:
        """Detect form type from images"""
        try:
            best_match = None
            best_confidence = 0.0
            
            self.logger.info(f"Checking {len(images)} pages against {len(self.templates)} templates")
            
            # Match against each template
            for template_name, template_data in self.templates.items():
                confidence = self.match_template(images, template_data)
                self.logger.info(f"Template {template_name} confidence: {confidence:.2%}")
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = template_data['form_type']
            
            if best_confidence > self.confidence_threshold:
                self.logger.info(f"Found match: {best_match} ({best_confidence:.2%})")
                return best_match, best_confidence
            else:
                self.logger.warning(f"No match found. Best confidence: {best_confidence:.2%}")
                return "Unknown", best_confidence
                
        except Exception as e:
            self.logger.error(f"Error in form detection: {e}")
            return "Error", 0.0