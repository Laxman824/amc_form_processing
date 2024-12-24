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