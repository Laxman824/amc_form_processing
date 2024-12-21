# import streamlit as st
# import numpy as np
# from PIL import Image
# import io
# from pathlib import Path
# import logging
# from datetime import datetime
# from pdf2image import convert_from_bytes
# from typing import List, Dict

# from ..core.processor import FormProcessor
# from ..models.form import FormType, ValidationStatus


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
#                     images = self._convert_pdf_to_images(file)
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

#     def _convert_pdf_to_images(self, file) -> List[np.ndarray]:
#         """Convert PDF file to list of images"""
#         try:
#             pdf_bytes = file.read()
#             images = convert_from_bytes(pdf_bytes)
#             return [np.array(img) for img in images]
#         except Exception as e:
#             self.logger.error(f"Error converting PDF: {str(e)}")
#             raise

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
#                 if hasattr(result, 'sections'):
#                     st.subheader("Section Details")
#                     for section in result.sections:
#                         status_color = {
#                             ValidationStatus.VALID: "green",
#                             ValidationStatus.INVALID: "red",
#                             ValidationStatus.WARNING: "orange",
#                             ValidationStatus.NOT_APPLICABLE: "gray"
#                         }[section.status]
                        
#                         with st.container():
#                             st.markdown(f"""
#                             **{section.section_name}**  
#                             Status: :{status_color}[{section.status.value}]  
#                             Confidence: {section.confidence:.2f}
#                             """)
                            
#                             if section.details:
#                                 with st.expander("Details"):
#                                     for key, value in section.details.items():
#                                         st.write(f"{key}: {value}")

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
#                 # Convert results to string for download
#                 result_str = str(results)
#                 st.download_button(
#                     "Download Results",
#                     data=result_str,
#                     file_name=f"form_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                     mime="application/json"
#                 )
import streamlit as st
import numpy as np
from PIL import Image
import io
from pathlib import Path
import logging
from datetime import datetime
from pdf2image import convert_from_bytes
from typing import List, Dict

from ..core.processor import FormProcessor
from ..models.form import FormType, ValidationStatus

class ProcessingInterface:
    def __init__(self):
        self.processor = FormProcessor()
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/processing_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_files(self, uploaded_files) -> Dict:
        """Process uploaded files and return results"""
        try:
            results = []
            for file in uploaded_files:
                self.logger.info(f"Processing file: {file.name}")
                
                # Convert file to images
                if file.type == "application/pdf":
                    images = self._convert_pdf_to_images(file)
                else:
                    image = Image.open(file)
                    images = [np.array(image)]
                
                # Process form
                result = self.processor.process_form(images)
                results.append({
                    'filename': file.name,
                    'result': result
                })
                
                self.logger.info(f"Completed processing: {file.name}")
                
            return {'status': 'success', 'results': results}
            
        except Exception as e:
            self.logger.error(f"Error processing files: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _convert_pdf_to_images(self, file) -> List[np.ndarray]:
        """Convert PDF file to list of images"""
        try:
            pdf_bytes = file.read()
            images = convert_from_bytes(pdf_bytes)
            return [np.array(img) for img in images]
        except Exception as e:
            self.logger.error(f"Error converting PDF: {str(e)}")
            raise

    def render_results(self, results: Dict):
        """Render processing results in Streamlit"""
        if results['status'] == 'error':
            st.error(f"Error: {results['message']}")
            return

        for file_result in results['results']:
            with st.expander(f"Results for {file_result['filename']}", expanded=True):
                result = file_result['result']
                
                # Display form type and page count
                st.write(f"Form Type: {result.form_type.value}")
                st.write(f"Total Pages: {result.total_pages}")
                
                # Display SIP and OTM status with color coding
                col1, col2 = st.columns(2)
                with col1:
                    color = "green" if result.sip_details_filled else "red"
                    st.markdown(f"SIP Details: :{color}[{'✓' if result.sip_details_filled else '✗'}]")
                with col2:
                    color = "green" if result.otm_details_filled else "red"
                    st.markdown(f"OTM Details: :{color}[{'✓' if result.otm_details_filled else '✗'}]")
                
                # Display section validations
                st.subheader("Section Details")
                for section in result.sections:
                    status_color = {
                        ValidationStatus.VALID: "green",
                        ValidationStatus.INVALID: "red",
                        ValidationStatus.WARNING: "orange",
                        ValidationStatus.NOT_APPLICABLE: "gray"
                    }[section.status]
                    
                    with st.container():
                        st.markdown(f"""
                        **{section.section_name}**  
                        Status: :{status_color}[{section.status.value}]  
                        Confidence: {section.confidence:.2f}
                        """)
                        
                        if section.details:
                            with st.expander("Details"):
                                for key, value in section.details.items():
                                    st.write(f"{key}: {value}")

    def render(self):
        """Render the processing interface"""
        st.title("Form Processing")
        
        # File upload section
        uploaded_files = st.file_uploader(
            "Upload forms for processing",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            with st.spinner("Processing forms..."):
                results = self.process_files(uploaded_files)
                
            # Display results
            self.render_results(results)
            
            # Download results option
            if results['status'] == 'success':
                result_str = str(results)
                st.download_button(
                    "Download Results",
                    data=result_str,
                    file_name=f"form_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )