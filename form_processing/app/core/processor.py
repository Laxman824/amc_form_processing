# import cv2
# import numpy as np
# from typing import List, Dict, Optional
# from pathlib import Path
# import json
# from datetime import datetime

# from ..models.template import Template, Section
# from ..models.form import FormType, FormValidation, ValidationStatus, SectionValidation
# from ..utils.image import preprocess_image, extract_section


# import streamlit as st
# import numpy as np
# from PIL import Image
# from pathlib import Path
# from typing import List, Dict
# import logging
# from datetime import datetime

# from ..core.processor import FormProcessor
# from ..models.form import FormType, ValidationStatus
# from ..utils.image import convert_pdf_to_images
# class FormProcessor:
#     def __init__(self, template_dir: Path = Path("templates")):
#         self.template_dir = template_dir
#         self.templates = self._load_templates()
        
#     def _load_templates(self) -> Dict[str, Template]:
#         """Load all templates from template directory"""
#         templates = {}
#         if self.template_dir.exists():
#             for file in self.template_dir.glob("*.json"):
#                 with open(file, "r") as f:
#                     template_data = json.load(f)
#                     templates[file.stem] = Template(**template_data)
#         return templates

#     def process_form(self, images: List[np.ndarray]) -> FormValidation:
#         """Process form images and return validation results"""
#         # Identify form type
#         form_type = self._identify_form_type(images[0])
        
#         # Get corresponding template
#         template = self._get_template(form_type)
#         if not template:
#             return FormValidation(
#                 form_type=FormType.OTHER,
#                 total_pages=len(images),
#                 sections=[],
#                 validation_timestamp=datetime.now().isoformat()
#             )

#         # Process each section
#         section_validations = []
#         for section in template.sections:
#             validation = self._validate_section(images, section)
#             section_validations.append(validation)

#         # Compile results
#         sip_details_filled = any(
#             v.status == ValidationStatus.VALID 
#             for v in section_validations 
#             if "SIP" in v.section_name
#         )
        
#         otm_details_filled = any(
#             v.status == ValidationStatus.VALID 
#             for v in section_validations 
#             if "OTM" in v.section_name
#         )

#         return FormValidation(
#             form_type=form_type,
#             total_pages=len(images),
#             sections=section_validations,
#             sip_details_filled=sip_details_filled,
#             otm_details_filled=otm_details_filled,
#             validation_timestamp=datetime.now().isoformat()
#         )

#     def _identify_form_type(self, first_page: np.ndarray) -> FormType:
#         """Identify form type from first page"""
#         # TODO: Implement form type identification logic
#         # For now, return default
#         return FormType.OTHER

#     def _get_template(self, form_type: FormType) -> Optional[Template]:
#         """Get template for form type"""
#         # Find matching template
#         for template in self.templates.values():
#             if template.form_type == form_type.value:
#                 return template
#         return None

#     def _validate_section(self, images: List[np.ndarray], section: Section) -> SectionValidation:
#         """Validate a specific section"""
#         # Extract section image
#         page_idx = section.bounding_box.page
#         if page_idx >= len(images):
#             return SectionValidation(
#                 section_name=section.name,
#                 status=ValidationStatus.INVALID,
#                 details={"error": "Page not found"},
#                 confidence=0.0
#             )

#         section_image = extract_section(
#             images[page_idx],
#             section.bounding_box
#         )
        
#         # Process section based on type
#         details = {}
#         confidence = 0.0
        
#         # TODO: Implement specific validation logic for each section type
        
#         return SectionValidation(
#             section_name=section.name,
#             status=ValidationStatus.NOT_APPLICABLE,
#             details=details,
#             confidence=confidence
#         )


# class ProcessingInterface:
#     def __init__(self):
#         self.processor = FormProcessor()
#         self.setup_logging()

#     def setup_logging(self):
#         """Setup logging configuration"""
#         log_dir = Path("logs")
#         log_dir.mkdir(exist_ok=True)
        
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#             handlers=[
#                 logging.FileHandler(f"logs/processing_{datetime.now().strftime('%Y%m%d')}.log"),
#                 logging.StreamHandler()
#             ]
#         )
#         self.logger = logging.getLogger(__name__)

#     def process_files(self, uploaded_files) -> Dict:
#         """Process uploaded files and return results"""
#         try:
#             results = []
#             for file in uploaded_files:
#                 self.logger.info(f"Processing file: {file.name}")
                
#                 # Convert file to images
#                 if file.type == "application/pdf":
#                     images = convert_pdf_to_images(file.read())
#                 else:
#                     image = Image.open(file)
#                     images = [np.array(image)]
                
#                 # Process form
#                 result = self.processor.process_form(images)
#                 results.append({
#                     'filename': file.name,
#                     'result': result
#                 })
                
#                 self.logger.info(f"Completed processing: {file.name}")
                
#             return {'status': 'success', 'results': results}
            
#         except Exception as e:
#             self.logger.error(f"Error processing files: {str(e)}", exc_info=True)
#             return {'status': 'error', 'message': str(e)}

#     def render_results(self, results: Dict):
#         """Render processing results in Streamlit"""
#         if results['status'] == 'error':
#             st.error(f"Error: {results['message']}")
#             return

#         for file_result in results['results']:
#             with st.expander(f"Results for {file_result['filename']}", expanded=True):
#                 result = file_result['result']
                
#                 # Display form type and page count
#                 st.write(f"Form Type: {result.form_type.value}")
#                 st.write(f"Total Pages: {result.total_pages}")
                
#                 # Display SIP and OTM status with color coding
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     color = "green" if result.sip_details_filled else "red"
#                     st.markdown(f"SIP Details: :{color}[{'✓' if result.sip_details_filled else '✗'}]")
#                 with col2:
#                     color = "green" if result.otm_details_filled else "red"
#                     st.markdown(f"OTM Details: :{color}[{'✓' if result.otm_details_filled else '✗'}]")
                
#                 # Display section validations
#                 st.subheader("Section Details")
#                 for section in result.sections:
#                     status_color = {
#                         ValidationStatus.VALID: "green",
#                         ValidationStatus.INVALID: "red",
#                         ValidationStatus.WARNING: "orange",
#                         ValidationStatus.NOT_APPLICABLE: "gray"
#                     }[section.status]
                    
#                     with st.container():
#                         st.markdown(f"""
#                         **{section.section_name}**  
#                         Status: :{status_color}[{section.status.value}]  
#                         Confidence: {section.confidence:.2f}
#                         """)
                        
#                         if section.details:
#                             with st.expander("Details"):
#                                 for key, value in section.details.items():
#                                     st.write(f"{key}: {value}")

#     def render(self):
#         """Render the processing interface"""
#         st.title("Form Processing")
        
#         # File upload section
#         uploaded_files = st.file_uploader(
#             "Upload forms for processing",
#             type=['pdf', 'png', 'jpg', 'jpeg'],
#             accept_multiple_files=True
#         )
        
#         if uploaded_files:
#             with st.spinner("Processing forms..."):
#                 results = self.process_files(uploaded_files)
                
#             # Display results
#             self.render_results(results)
            
#             # Download results option
#             if results['status'] == 'success':
#                 st.download_button(
#                     "Download Results",
#                     data=str(results),
#                     file_name=f"form_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                     mime="application/json"
#                 )
import cv2
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

from ..models.form import FormType, FormValidation, ValidationStatus, SectionValidation

class FormProcessor:
    def __init__(self, template_dir: Path = Path("templates")):
        self.template_dir = template_dir
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Load all templates from template directory"""
        templates = {}
        if self.template_dir.exists():
            for file in self.template_dir.glob("*.json"):
                with open(file, "r") as f:
                    templates[file.stem] = json.load(f)
        return templates

    def process_form(self, images: List[np.ndarray]) -> FormValidation:
        """Process form images and return validation results"""
        try:
            # Basic validation
            if not images:
                return FormValidation(
                    form_type=FormType.OTHER,
                    total_pages=0,
                    sections=[],
                )

            # Process first page for form type identification
            form_type = self._identify_form_type(images[0])
            
            # Create basic validation result
            sections = [
                SectionValidation(
                    section_name="Form Identification",
                    status=ValidationStatus.VALID if form_type != FormType.OTHER else ValidationStatus.WARNING,
                    details={"identified_type": form_type.value},
                    confidence=0.8 if form_type != FormType.OTHER else 0.3
                )
            ]

            return FormValidation(
                form_type=form_type,
                total_pages=len(images),
                sections=sections,
                sip_details_filled=False,  # To be implemented
                otm_details_filled=False   # To be implemented
            )

        except Exception as e:
            # Return error validation
            return FormValidation(
                form_type=FormType.OTHER,
                total_pages=len(images) if images else 0,
                sections=[
                    SectionValidation(
                        section_name="Error",
                        status=ValidationStatus.INVALID,
                        details={"error": str(e)},
                        confidence=0.0
                    )
                ]
            )

    def _identify_form_type(self, image: np.ndarray) -> FormType:
        """Placeholder for form type identification"""
        # TODO: Implement actual form type identification
        return FormType.OTHER