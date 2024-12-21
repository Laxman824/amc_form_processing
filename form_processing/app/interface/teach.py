
# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# import numpy as np
# from PIL import Image
# import io
# import logging
# from pathlib import Path
# from datetime import datetime
# import json

# from ..utils.pdf import pdf_to_images, check_pdf_support,is_valid_pdf

# class TemplateTeachingInterface:
#     def __init__(self):
#         self.setup_logging()
#         self.initialize_session_state()
#         self.pdf_support = check_pdf_support()

#     def setup_logging(self):
#         """Setup logging configuration"""
#         self.logger = logging.getLogger(__name__)
#         if not self.logger.handlers:
#             handler = logging.StreamHandler()
#             formatter = logging.Formatter(
#                 '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#             )
#             handler.setFormatter(formatter)
#             self.logger.addHandler(handler)
#             self.logger.setLevel(logging.INFO)

#     def initialize_session_state(self):
#         """Initialize session state variables"""
#         if 'current_page' not in st.session_state:
#             st.session_state.current_page = 0
#         if 'pages' not in st.session_state:
#             st.session_state.pages = []
#         if 'current_sections' not in st.session_state:
#             st.session_state.current_sections = []

#     def process_uploaded_file(self, uploaded_file):
#         """Process uploaded file and convert to list of images"""
#         try:
#             if uploaded_file.type == "application/pdf":
#                 self.logger.info("Processing PDF file")
#                 st.info("Processing PDF file... This may take a moment.")
                
#                 # Get PDF bytes
#                 pdf_bytes = uploaded_file.read()
                
#                 # Convert PDF to images
#                 images = pdf_to_images(pdf_bytes)
                
#                 if not images:
#                     st.error("Failed to extract images from PDF")
#                     return None
                    
#                 st.success(f"Successfully extracted {len(images)} pages from PDF")
#                 return images
                
#             else:
#                 self.logger.info("Processing image file")
#                 # Handle image files
#                 image = Image.open(uploaded_file)
#                 return [np.array(image)]
                
#         except Exception as e:
#             self.logger.error(f"Error processing file: {str(e)}")
#             st.error(f"Error processing file: {str(e)}")
#             return None

#     def render(self):
#         """Main render method for template teaching interface"""
#         st.title("Template Teaching Interface")
        
#         # Show PDF support status
#         if not self.pdf_support:
#             st.warning("PDF support is not available. Please ensure all dependencies are installed.")

#         # File upload section
#         uploaded_file = st.file_uploader(
#             "Upload a form template",
#             type=['pdf', 'png', 'jpg', 'jpeg'],
#             help="Upload a PDF or image file of the form"
#         )

#         if uploaded_file:
#             col1, col2 = st.columns([3, 1])
            
#             with col1:
#                 # Process file
#                 images = self.process_uploaded_file(uploaded_file)
                
#                 if images is not None:
#                     st.session_state.pages = images
                    
#                     # Page navigation for multi-page documents
#                     if len(images) > 1:
#                         st.session_state.current_page = st.slider(
#                             "Page",
#                             0,
#                             len(images) - 1,
#                             st.session_state.current_page
#                         )
                    
#                     # Display current page and annotation canvas
#                     current_image = images[st.session_state.current_page]
                    
#                     # Convert to PIL Image for display
#                     if isinstance(current_image, np.ndarray):
#                         current_image = Image.fromarray(current_image)
                    
#                     # Show annotation canvas
#                     canvas_result = st_canvas(
#                         fill_color="rgba(255, 165, 0, 0.3)",
#                         stroke_width=2,
#                         stroke_color="#e00",
#                         background_image=current_image,
#                         drawing_mode="rect",
#                         key=f"canvas_{st.session_state.current_page}",
#                         height=current_image.height,
#                         width=current_image.width,
#                     )
                    
#                     if canvas_result.json_data:
#                         self.handle_annotations(canvas_result)

#             with col2:
#                 # Template properties and sections list
#                 st.subheader("Template Properties")
#                 with st.form("template_properties"):
#                     template_name = st.text_input("Template Name")
#                     form_type = st.selectbox(
#                         "Form Type",
#                         ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
#                     )
                    
#                     if st.form_submit_button("Save Template"):
#                         if template_name and st.session_state.current_sections:
#                             self.save_template(template_name, form_type)
#                             st.success(f"Template '{template_name}' saved!")
#                         else:
#                             st.error("Please provide a template name and mark at least one section")

#                 # Display current sections
#                 if st.session_state.current_sections:
#                     st.subheader("Marked Sections")
#                     for i, section in enumerate(st.session_state.current_sections):
#                         with st.container():
#                             st.write(f"{i+1}. {section['name']} (Page {section['page']+1})")
#                             if st.button(f"Remove {section['name']}"):
#                                 st.session_state.current_sections.pop(i)
#                                 st.experimental_rerun()

#     def handle_annotations(self, canvas_result):
#         """Handle canvas annotations"""
#         if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
#             last_object = canvas_result.json_data["objects"][-1]
            
#             with st.form("section_properties"):
#                 st.subheader("Section Properties")
#                 section_name = st.text_input("Section Name")
#                 section_type = st.selectbox(
#                     "Section Type",
#                     ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                 )
                
#                 if st.form_submit_button("Add Section"):
#                     if not section_name:
#                         st.warning("Please enter a section name")
#                         return

#                     new_section = {
#                         "name": section_name,
#                         "type": section_type,
#                         "coordinates": {
#                             "x": last_object["left"] / canvas_result.width,
#                             "y": last_object["top"] / canvas_result.height,
#                             "width": last_object["width"] / canvas_result.width,
#                             "height": last_object["height"] / canvas_result.height
#                         },
#                         "page": st.session_state.current_page
#                     }
#                     st.session_state.current_sections.append(new_section)
#                     st.success(f"Added section: {section_name}")

#     def save_template(self, template_name: str, form_type: str):
#         """Save the template"""
#         template_dir = Path("templates")
#         template_dir.mkdir(exist_ok=True)
        
#         template_data = {
#             "name": template_name,
#             "form_type": form_type,
#             "sections": st.session_state.current_sections,
#             "created_at": datetime.now().isoformat()
#         }
        
#         template_path = template_dir / f"{template_name.lower().replace(' ', '_')}.json"
#         with open(template_path, "w") as f:
#             json.dump(template_data, f, indent=4)
#     def process_uploaded_file(self, uploaded_file):
#             """Process uploaded file and convert to list of images"""
#             try:
#                 if uploaded_file.type == "application/pdf":
#                     self.logger.info("Processing PDF file")
#                     st.info("Processing PDF file... This may take a moment.")
                    
#                     # Get PDF bytes
#                     pdf_bytes = uploaded_file.read()
                    
#                     # Validate PDF
#                     if not is_valid_pdf(pdf_bytes):
#                         st.error("Invalid or corrupted PDF file")
#                         return None
                    
#                     # Convert PDF to images
#                     with st.spinner("Converting PDF pages to images..."):
#                         images = pdf_to_images(pdf_bytes)
                    
#                     if not images:
#                         st.error("Failed to extract images from PDF")
#                         return None
                        
#                     st.success(f"Successfully extracted {len(images)} pages from PDF")
#                     return images
                    
#                 else:
#                     self.logger.info("Processing image file")
#                     # Handle image files
#                     image = Image.open(uploaded_file)
#                     return [np.array(image)]
                    
#             except Exception as e:
#                 self.logger.error(f"Error processing file: {str(e)}")
#                 st.error(f"Error processing file: {str(e)}")
#                 return None

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import io
import logging
from pathlib import Path
from datetime import datetime
import json

from ..utils.pdf import pdf_to_images, is_valid_pdf

class TemplateTeachingInterface:
    def __init__(self):
        self.setup_logging()
        self.initialize_session_state()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def initialize_session_state(self):
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        if 'pages' not in st.session_state:
            st.session_state.pages = []
        if 'current_sections' not in st.session_state:
            st.session_state.current_sections = []

    def process_uploaded_file(self, uploaded_file):
        try:
            if uploaded_file.type == "application/pdf":
                self.logger.info("Processing PDF file")
                with st.spinner("Processing PDF file..."):
                    pdf_bytes = uploaded_file.read()
                    images = pdf_to_images(pdf_bytes)
                    if images:
                        st.success(f"Successfully loaded {len(images)} pages")
                        return images
                    else:
                        st.error("Failed to process PDF")
                        return None
            else:
                image = Image.open(uploaded_file)
                return [np.array(image)]
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None

    def render(self):
        st.title("Template Teaching Interface")

        col1, col2 = st.columns([3, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload a form template",
                type=['pdf', 'png', 'jpg', 'jpeg']
            )

            if uploaded_file:
                images = self.process_uploaded_file(uploaded_file)
                if images:
                    st.session_state.pages = images

                    # Page selection if PDF has multiple pages
                    if len(images) > 1:
                        page_col1, page_col2 = st.columns([3, 1])
                        with page_col1:
                            st.session_state.current_page = st.slider(
                                "Select Page",
                                0,
                                len(images) - 1,
                                st.session_state.current_page
                            )
                        with page_col2:
                            st.write(f"Page {st.session_state.current_page + 1} of {len(images)}")

                    # Display current page
                    current_image = st.session_state.pages[st.session_state.current_page]
                    if isinstance(current_image, np.ndarray):
                        current_image = Image.fromarray(current_image)

                    # First display the image normally
                    st.image(current_image, caption=f"Page {st.session_state.current_page + 1}", use_column_width=True)

                    # Then create the annotation canvas
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",
                        stroke_width=2,
                        stroke_color="#e00",
                        background_image=current_image,
                        drawing_mode="rect",
                        key=f"canvas_{st.session_state.current_page}",
                        update_streamlit=True,
                        width=current_image.width,
                        height=current_image.height
                    )

                    if canvas_result.json_data and canvas_result.json_data.get("objects"):
                        self.handle_annotations(canvas_result)

        with col2:
            st.subheader("Template Details")
            
            # Form for template properties
            with st.form("template_properties"):
                template_name = st.text_input("Template Name")
                form_type = st.selectbox(
                    "Form Type",
                    ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
                )
                submit_button = st.form_submit_button("Save Template")
                
                if submit_button:
                    if not template_name:
                        st.error("Please enter a template name")
                    elif not st.session_state.current_sections:
                        st.error("Please mark at least one section")
                    else:
                        self.save_template(template_name, form_type)
                        st.success("Template saved successfully!")

            # Display marked sections
            if st.session_state.current_sections:
                st.subheader("Marked Sections")
                for i, section in enumerate(st.session_state.current_sections):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"{section['name']} (Page {section['page'] + 1})")
                        with col2:
                            if st.button("Remove", key=f"remove_{i}"):
                                st.session_state.current_sections.pop(i)
                                st.experimental_rerun()

    def handle_annotations(self, canvas_result):
        if len(canvas_result.json_data["objects"]) > 0:
            last_object = canvas_result.json_data["objects"][-1]
            
            with st.form("section_properties"):
                st.subheader("Add Section")
                section_name = st.text_input("Section Name")
                section_type = st.selectbox(
                    "Section Type",
                    ["SIP Details", "OTM Section", "Transaction Type", "Other"]
                )
                
                if st.form_submit_button("Add Section"):
                    if not section_name:
                        st.warning("Please enter a section name")
                        return

                    # Calculate relative coordinates
                    new_section = {
                        "name": section_name,
                        "type": section_type,
                        "coordinates": {
                            "x": last_object["left"] / canvas_result.width,
                            "y": last_object["top"] / canvas_result.height,
                            "width": last_object["width"] / canvas_result.width,
                            "height": last_object["height"] / canvas_result.height
                        },
                        "page": st.session_state.current_page
                    }
                    st.session_state.current_sections.append(new_section)
                    st.success(f"Added section: {section_name}")

    def save_template(self, template_name: str, form_type: str):
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)
        
        template_data = {
            "name": template_name,
            "form_type": form_type,
            "sections": st.session_state.current_sections,
            "created_at": datetime.now().isoformat()
        }
        
        template_path = template_dir / f"{template_name.lower().replace(' ', '_')}.json"
        with open(template_path, "w") as f:
            json.dump(template_data, f, indent=4)