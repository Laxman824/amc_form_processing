import streamlit as st
import numpy as np
from PIL import Image
import logging
from datetime import datetime
from pathlib import Path
import json
import io
import fitz  # PyMuPDF
from typing import Dict, List, Optional

from ..core.processor import FormProcessor

class ProcessingInterface:
    def __init__(self):
        self.processor = FormProcessor()
        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def process_pdf(self, pdf_bytes: bytes) -> List[np.ndarray]:
        """Process PDF using PyMuPDF"""
        try:
            # Open PDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            
            for page_num in range(len(doc)):
                # Get page
                page = doc[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                # Convert to numpy array
                img = Image.open(io.BytesIO(img_data))
                images.append(np.array(img))
            
            doc.close()
            return images
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            raise

    # def process_file(self, uploaded_file) -> Dict:
    #     """Process uploaded file"""
    #     try:
    #         # Convert to images
    #         if uploaded_file.type == "application/pdf":
    #             pdf_bytes = uploaded_file.read()
    #             images = self.process_pdf(pdf_bytes)
    #         else:
    #             image = Image.open(uploaded_file)
    #             images = [np.array(image)]

    #         if not images:
    #             return {
    #                 'status': 'error',
    #                 'message': 'Failed to extract images from file'
    #             }

    #         # Process form
    #         results = self.processor.process_form(images)
    #         return results

    #     except Exception as e:
    #         self.logger.error(f"Error processing file: {e}")
    #         return {
    #             'status': 'error',
    #             'message': str(e)
    #         }
    def process_file(self, uploaded_file) -> Dict:
        """Process uploaded file"""
        try:
            if uploaded_file.type == "application/pdf":
                # For PDFs, pass the bytes directly to the processor
                pdf_bytes = uploaded_file.read()
                results = self.processor.process_form([pdf_bytes], file_type='pdf')
            else:
                # For images, convert to numpy array
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                if image_array is None or image_array.size == 0:
                    raise ValueError("Invalid image file")
                results = self.processor.process_form([image_array], file_type='image')

            return results

        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    def display_results(self, results: Dict, filename: str):
        """Display processing results"""
        st.markdown(f"### Results for {filename}")

        if results['status'] == 'error':
            st.error(f"Error: {results.get('message', 'Unknown error')}")
            return

        # Form type and confidence
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Form Type: {results['form_type']}")
        with col2:
            conf = results.get('confidence', 0)
            st.write(f"Confidence: {conf:.2%}")

        # Overall status
        st.markdown("#### Form Status")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            color = "green" if results.get('sip_details_filled', False) else "red"
            st.markdown(f"SIP Details: :{color}[{'✓' if results.get('sip_details_filled', False) else '✗'}]")
        with status_col2:
            color = "green" if results.get('otm_details_filled', False) else "red"
            st.markdown(f"OTM Details: :{color}[{'✓' if results.get('otm_details_filled', False) else '✗'}]")

        # Section details
        if 'sections' in results:
            st.markdown("#### Section Details")
            for section_name, section_data in results['sections'].items():
                with st.expander(f"{section_name.replace('_', ' ').title()}", expanded=True):
                    if isinstance(section_data, dict):
                        # Section status
                        color = "green" if section_data.get('filled', False) else "red"
                        st.markdown(f"Status: :{color}[{'Filled' if section_data.get('filled', False) else 'Not Filled'}]")
                        
                        # Section details
                        if 'details' in section_data:
                            st.markdown("Details:")
                            for key, value in section_data['details'].items():
                                st.write(f"- {key.replace('_', ' ').title()}: {value}")

    def check_templates(self):
            """Check available templates"""
            template_dir = Path("templates")
            if not template_dir.exists():
                st.warning("No templates directory found. Please create templates first.")
                st.info("Go to the Template Teaching Interface to create templates.")
                return False

            templates = list(template_dir.glob("*.json"))
            if not templates:
                st.warning("No templates found. Please create templates first.")
                st.info("Steps to create templates:")
                st.markdown("""
                1. Go to Template Teaching Interface
                2. Upload each type of form:
                - CA Form
                - SIP Form
                - Multiple SIP Form
                3. Mark required sections:
                - SIP Details
                - OTM Section
                - Transaction Type
                4. Save each template
                """)
                return False

            # Show available templates
            st.success(f"Found {len(templates)} templates:")
            for template_path in templates:
                try:
                    with open(template_path, "r") as f:
                        template = json.load(f)
                    st.write(f"- {template['name']} ({template['form_type']})")
                except Exception as e:
                    st.error(f"Error reading template {template_path.name}: {e}")

            return True




    def render(self):
        """Render processing interface"""
        st.title("Form Processing")
        if not self.check_templates():
            return

        # File upload section
        st.markdown("### Upload Forms")
        uploaded_files = st.file_uploader(
            "Upload forms for processing",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload PDF or image files of the forms"
        )

        if uploaded_files:
            results_list = []

            # Process each file with progress
            progress_text = "Processing forms..."
            my_bar = st.progress(0, text=progress_text)
            
            for i, uploaded_file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                my_bar.progress(progress, text=f"Processing {uploaded_file.name}...")
                
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    results = self.process_file(uploaded_file)
                    results_list.append({
                        'filename': uploaded_file.name,
                        'results': results
                    })
            
            my_bar.empty()

            # Display results for each file
            for file_results in results_list:
                self.display_results(
                    file_results['results'],
                    file_results['filename']
                )

            # Export results
            if results_list:
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'results': results_list
                }
                
                # Convert to JSON
                json_str = json.dumps(export_data, indent=2)
                
                st.download_button(
                    label="Download Results",
                    data=json_str,
                    file_name=f"form_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    help="Download the processing results as JSON file"
                )