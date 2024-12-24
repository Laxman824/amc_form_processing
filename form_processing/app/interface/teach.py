# import streamlit as st
# from streamlit_cropperjs import st_cropperjs
# import numpy as np
# from PIL import Image, ImageDraw
# import logging
# from pathlib import Path
# from datetime import datetime
# import json
# import io
# from ..utils.pdf import pdf_to_images, is_valid_pdf

# class TemplateTeachingInterface:
#     def __init__(self):
#         self.setup_logging()
#         self.initialize_session_state()

#     def setup_logging(self):
#         self.logger = logging.getLogger(__name__)

#     def initialize_session_state(self):
#         if 'current_page' not in st.session_state:
#             st.session_state.current_page = 0
#         if 'pages' not in st.session_state:
#             st.session_state.pages = []
#         if 'current_sections' not in st.session_state:
#             st.session_state.current_sections = []
#         if 'current_image' not in st.session_state:
#             st.session_state.current_image = None

#     def process_uploaded_file(self, uploaded_file):
#         try:
#             if uploaded_file.type == "application/pdf":
#                 self.logger.info("Processing PDF file")
#                 with st.spinner("Processing PDF file..."):
#                     pdf_bytes = uploaded_file.read()
#                     images = pdf_to_images(pdf_bytes)
#                     if images:
#                         st.success(f"Successfully loaded {len(images)} pages")
#                         return images
#                     else:
#                         st.error("Failed to process PDF")
#                         return None
#             else:
#                 image = Image.open(uploaded_file)
#                 return [np.array(image)]
#         except Exception as e:
#             self.logger.error(f"Error processing file: {str(e)}")
#             st.error(f"Error processing file: {str(e)}")
#             return None

#     def draw_existing_sections(self, image):
#         """Draw existing sections on image"""
#         if isinstance(image, np.ndarray):
#             image = Image.fromarray(image)
        
#         img_draw = ImageDraw.Draw(image)
        
#         # Draw all sections for current page
#         for section in st.session_state.current_sections:
#             if section['page'] == st.session_state.current_page:
#                 coords = section['coordinates']
#                 x1 = int(coords['x'] * image.width)
#                 y1 = int(coords['y'] * image.height)
#                 x2 = int((coords['x'] + coords['width']) * image.width)
#                 y2 = int((coords['y'] + coords['height']) * image.height)
                
#                 # Draw rectangle for section
#                 img_draw.rectangle([x1, y1, x2, y2], 
#                                 outline='red', 
#                                 width=2)
#                 # Draw section name
#                 img_draw.text((x1, y1-20), 
#                             section['name'], 
#                             fill='red')

#         # Convert back to bytes for cropperjs
#         img_byte_arr = io.BytesIO()
#         image.save(img_byte_arr, format='PNG')
#         img_byte_arr = img_byte_arr.getvalue()
        
#         return img_byte_arr

#     def render_section_selection(self, image):
#         """Render section selection using cropperjs"""
#         if isinstance(image, np.ndarray):
#             image = Image.fromarray(image)

#         # Convert image to bytes
#         img_byte_arr = io.BytesIO()
#         image.save(img_byte_arr, format='PNG')
#         img_byte_arr = img_byte_arr.getvalue()

#         # Draw existing sections
#         img_with_sections = self.draw_existing_sections(image)
        
#         st.markdown("### Select Section")
#         st.caption("Drag to select the section area, then click 'Mark Section'")

#         # Use cropperjs for selection
#         cropped_area = st_cropperjs(
#             pic=img_with_sections,
#             btn_text="Mark Section",
#             key=f"cropper_{st.session_state.current_page}"
#         )

#         # Show section properties form when area is selected
#         if cropped_area:
#             cropped_img = Image.open(io.BytesIO(cropped_area))
            
#             # Calculate relative coordinates based on cropped area
#             coords = {
#                 "x": cropped_img.info.get('cropX', 0) / image.width,
#                 "y": cropped_img.info.get('cropY', 0) / image.height,
#                 "width": cropped_img.info.get('cropWidth', 0) / image.width,
#                 "height": cropped_img.info.get('cropHeight', 0) / image.height
#             }

#             with st.form("section_properties"):
#                 st.markdown("### Section Details")
                
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     section_name = st.text_input("Section Name")
#                 with col2:
#                     section_type = st.selectbox(
#                         "Section Type",
#                         ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                     )

#                 if st.form_submit_button("Add Section"):
#                     if not section_name:
#                         st.error("Please enter a section name")
#                     else:
#                         new_section = {
#                             "name": section_name,
#                             "type": section_type,
#                             "coordinates": coords,
#                             "page": st.session_state.current_page
#                         }
#                         st.session_state.current_sections.append(new_section)
#                         st.success(f"Added section: {section_name}")
#                         st.experimental_rerun()

#     def render_sections_list(self):
#         if st.session_state.current_sections:
#             st.markdown("### Marked Sections")
            
#             # Group sections by page
#             sections_by_page = {}
#             for section in st.session_state.current_sections:
#                 page = section['page']
#                 if page not in sections_by_page:
#                     sections_by_page[page] = []
#                 sections_by_page[page].append(section)
            
#             # Display sections grouped by page
#             for page in sorted(sections_by_page.keys()):
#                 with st.expander(f"Page {page + 1}", expanded=(page == st.session_state.current_page)):
#                     for i, section in enumerate(sections_by_page[page]):
#                         cols = st.columns([3, 1])
#                         with cols[0]:
#                             st.write(f"• {section['name']} ({section['type']})")
#                         with cols[1]:
#                             if st.button("Remove", key=f"remove_{page}_{i}"):
#                                 st.session_state.current_sections.remove(section)
#                                 st.experimental_rerun()

#     def render(self):
#         st.title("Form Template Teaching")

#         # Instructions
#         with st.expander("How to Create Template", expanded=False):
#             st.markdown("""
#             ### Instructions:
#             1. Upload your form (PDF or image)
#             2. Select sections by dragging on the form
#             3. Click 'Mark Section' when selection is ready
#             4. Name and categorize each section
#             5. Save the template when done
#             """)

#         # Main layout
#         col1, col2 = st.columns([3, 1])

#         with col1:
#             uploaded_file = st.file_uploader(
#                 "Upload a form template",
#                 type=['pdf', 'png', 'jpg', 'jpeg']
#             )

#             if uploaded_file:
#                 images = self.process_uploaded_file(uploaded_file)
                
#                 if images:
#                     st.session_state.pages = images

#                     # Page navigation for PDFs
#                     if len(images) > 1:
#                         st.markdown("### Page Navigation")
#                         current_page = st.slider(
#                             "Select Page",
#                             0,
#                             len(images) - 1,
#                             st.session_state.current_page
#                         )
#                         st.session_state.current_page = current_page
#                         st.write(f"Page {current_page + 1} of {len(images)}")

#                     # Get current image
#                     current_image = images[st.session_state.current_page]
                    
#                     # Show section selection interface
#                     self.render_section_selection(current_image)

#         with col2:
#             # Template properties
#             with st.form("template_properties"):
#                 st.markdown("### Template Details")
#                 template_name = st.text_input("Template Name")
#                 form_type = st.selectbox(
#                     "Form Type",
#                     ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
#                 )
                
#                 if st.form_submit_button("Save Template"):
#                     if not template_name:
#                         st.error("Please enter a template name")
#                     elif not st.session_state.current_sections:
#                         st.error("Please mark at least one section")
#                     else:
#                         try:
#                             template_dir = Path("templates")
#                             template_dir.mkdir(exist_ok=True)
                            
#                             template_data = {
#                                 "name": template_name,
#                                 "form_type": form_type,
#                                 "sections": st.session_state.current_sections,
#                                 "created_at": datetime.now().isoformat()
#                             }
                            
#                             template_path = template_dir / f"{template_name.lower().replace(' ', '_')}.json"
#                             with open(template_path, "w") as f:
#                                 json.dump(template_data, f, indent=4)
                            
#                             st.success("Template saved successfully!")
#                             st.session_state.current_sections = []
#                             st.experimental_rerun()
#                         except Exception as e:
#                             st.error(f"Error saving template: {str(e)}")

#             # Show marked sections
#             self.render_sections_list()
#             # Show saved templates
#             st.markdown("---")
#             self.view_saved_templates()           
#     def view_saved_templates(self):
#             """View all saved templates"""
#             template_dir = Path("templates")
#             if not template_dir.exists() or not list(template_dir.glob("*.json")):
#                 st.info("No templates saved yet")
#                 return

#             st.markdown("## Saved Templates")
            
#             # List all template files
#             template_files = list(template_dir.glob("*.json"))
            
#             for template_file in template_files:
#                 with st.expander(f"📄 {template_file.stem}", expanded=False):
#                     try:
#                         with open(template_file, "r") as f:
#                             template_data = json.load(f)
                        
#                         # Display template details
#                         st.markdown(f"### {template_data['name']}")
#                         st.write(f"Form Type: {template_data['form_type']}")
#                         st.write(f"Created: {template_data['created_at']}")
                        
#                         # Display sections
#                         if template_data['sections']:
#                             st.markdown("#### Sections:")
#                             for section in template_data['sections']:
#                                 st.markdown(f"""
#                                 - **{section['name']}** ({section['type']})
#                                 - Page: {section['page'] + 1}
#                                 - Coordinates: 
#                                     - x: {section['coordinates']['x']:.2%}
#                                     - y: {section['coordinates']['y']:.2%}
#                                     - width: {section['coordinates']['width']:.2%}
#                                     - height: {section['coordinates']['height']:.2%}
#                                 """)
                        
#                         # Add delete button
#                         if st.button("Delete Template", key=f"delete_{template_file.stem}"):
#                             template_file.unlink()  # Delete the file
#                             st.success("Template deleted!")
#                             st.experimental_rerun()
                            
#                     except Exception as e:
#                         st.error(f"Error reading template {template_file.name}: {str(e)}")



##second version with mapping the coordinates and small preview 
import streamlit as st
from streamlit_cropperjs import st_cropperjs
import numpy as np
from PIL import Image, ImageDraw
import logging
from pathlib import Path
from datetime import datetime
import json
import io
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
        if 'current_image' not in st.session_state:
            st.session_state.current_image = None

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
            self.logger.error(f"Error processing file: {str(e)}")
            st.error(f"Error processing file: {str(e)}")
            return None

    def create_section_preview(self, image, coords):
        """Create a preview of selected section"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Calculate pixel coordinates
        x1 = int(coords["x"] * image.width)
        y1 = int(coords["y"] * image.height)
        x2 = int((coords["x"] + coords["width"]) * image.width)
        y2 = int((coords["y"] + coords["height"]) * image.height)
        
        # Crop section
        section = image.crop((x1, y1, x2, y2))
        
        # Resize for preview if too large
        max_preview_size = (300, 300)
        section.thumbnail(max_preview_size)
        
        return section

    def draw_existing_sections(self, image):
        """Draw existing sections on image"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        img_draw = ImageDraw.Draw(image)
        
        # Draw all sections for current page
        for section in st.session_state.current_sections:
            if section['page'] == st.session_state.current_page:
                coords = section['coordinates']
                x1 = int(coords['x'] * image.width)
                y1 = int(coords['y'] * image.height)
                x2 = int((coords['x'] + coords['width']) * image.width)
                y2 = int((coords['y'] + coords['height']) * image.height)
                
                # Draw rectangle with section name
                img_draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
                img_draw.text((x1, y1-20), section['name'], fill='red')

        # Convert to bytes for cropperjs
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def render_section_selection(self, image):
        """Render section selection using cropperjs"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Draw existing sections
        img_with_sections = self.draw_existing_sections(image)
        
        st.markdown("### Select Section")
        st.caption("Drag to select the section area, then click 'Mark Section'")

        # Use cropperjs for selection
        cropped_area = st_cropperjs(
            pic=img_with_sections,
            btn_text="Mark Section",
            key=f"cropper_{st.session_state.current_page}"
        )

        # Show section properties form when area is selected
        if cropped_area:
            # Get the cropped image
            try:
                cropped_img = Image.open(io.BytesIO(cropped_area))
                
                # Get crop data from image info
                x = int(cropped_img.info.get('cropX', 0))
                y = int(cropped_img.info.get('cropY', 0))
                width = int(cropped_img.info.get('cropWidth', 0))
                height = int(cropped_img.info.get('cropHeight', 0))
                
                # Calculate relative coordinates
                coords = {
                    "x": x / image.width if image.width else 0,
                    "y": y / image.height if image.height else 0,
                    "width": width / image.width if image.width else 0,
                    "height": height / image.height if image.height else 0
                }

                # Create preview
                preview_img = image.crop((x, y, x + width, y + height))
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.form("section_properties"):
                        st.markdown("### Section Details")
                        section_name = st.text_input("Section Name")
                        section_type = st.selectbox(
                            "Section Type",
                            ["SIP Details", "OTM Section", "Transaction Type", "Other"]
                        )

                        # Show coordinate information
                        st.write("Selected Area:")
                        st.write(f"- Location: ({coords['x']:.2%}, {coords['y']:.2%})")
                        st.write(f"- Size: {coords['width']:.2%} × {coords['height']:.2%}")

                        # Debug information
                        with st.expander("Debug Info"):
                            st.write("Image Size:", (image.width, image.height))
                            st.write("Crop Coordinates:", (x, y, width, height))
                            st.write("Relative Coordinates:", coords)

                        if st.form_submit_button("Add Section"):
                            if not section_name:
                                st.error("Please enter a section name")
                            else:
                                new_section = {
                                    "name": section_name,
                                    "type": section_type,
                                    "coordinates": coords,
                                    "page": st.session_state.current_page
                                }
                                st.session_state.current_sections.append(new_section)
                                st.success(f"Added section: {section_name}")
                                st.rerun()

                with col2:
                    if preview_img:
                        st.markdown("### Selection Preview")
                        # Resize preview if too large
                        max_size = (300, 300)
                        preview_img.thumbnail(max_size)
                        st.image(preview_img, caption="Selected Area")

            except Exception as e:
                st.error(f"Error processing selection: {str(e)}")
                st.write("Debug info:")
                st.write("Cropped area type:", type(cropped_area))
                        
    def render_sections_list(self):
        if st.session_state.current_sections:
            st.markdown("### Marked Sections")
            
            # Group sections by page
            sections_by_page = {}
            for section in st.session_state.current_sections:
                page = section['page']
                if page not in sections_by_page:
                    sections_by_page[page] = []
                sections_by_page[page].append(section)
            
            # Display sections grouped by page
            for page in sorted(sections_by_page.keys()):
                with st.expander(f"Page {page + 1}", expanded=(page == st.session_state.current_page)):
                    for i, section in enumerate(sections_by_page[page]):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"• {section['name']} ({section['type']})")
                                coords = section['coordinates']
                                st.write(f"Location: ({coords['x']:.2%}, {coords['y']:.2%})")
                                st.write(f"Size: {coords['width']:.2%} × {coords['height']:.2%}")
                            with col2:
                                if st.button("Remove", key=f"remove_{page}_{i}"):
                                    st.session_state.current_sections.remove(section)
                                    st.rerun()

    def render(self):
        st.title("Form Template Teaching")

        # Instructions
        with st.expander("How to Create Template", expanded=False):
            st.markdown("""
            ### Instructions:
            1. Upload your form (PDF or image)
            2. Select sections by dragging on the form
            3. Click 'Mark Section' when selection is ready
            4. Name and categorize each section
            5. Save the template when done
            """)

        # Main layout
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

                    # Page navigation for PDFs
                    if len(images) > 1:
                        st.markdown("### Page Navigation")
                        current_page = st.slider(
                            "Select Page",
                            0,
                            len(images) - 1,
                            st.session_state.current_page
                        )
                        st.session_state.current_page = current_page
                        st.write(f"Page {current_page + 1} of {len(images)}")

                    # Get current image
                    current_image = images[st.session_state.current_page]
                    
                    # Show section selection interface
                    self.render_section_selection(current_image)

        with col2:
            # Template properties
            with st.form("template_properties"):
                st.markdown("### Template Details")
                template_name = st.text_input("Template Name")
                form_type = st.selectbox(
                    "Form Type",
                    ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
                )
                
                if st.form_submit_button("Save Template"):
                    if not template_name:
                        st.error("Please enter a template name")
                    elif not st.session_state.current_sections:
                        st.error("Please mark at least one section")
                    else:
                        try:
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
                            
                            st.success("Template saved successfully!")
                            st.session_state.current_sections = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving template: {str(e)}")

            # Show marked sections
            self.render_sections_list()
            
            # Show saved templates
            st.markdown("---")
            self.view_saved_templates()

    def view_saved_templates(self):
        """View all saved templates"""
        template_dir = Path("templates")
        if not template_dir.exists() or not list(template_dir.glob("*.json")):
            st.info("No templates saved yet")
            return

        st.markdown("## Saved Templates")
        
        template_files = list(template_dir.glob("*.json"))
        
        for template_file in template_files:
            with st.expander(f"📄 {template_file.stem}", expanded=False):
                try:
                    with open(template_file, "r") as f:
                        template_data = json.load(f)
                    
                    st.markdown(f"### {template_data['name']}")
                    st.write(f"Form Type: {template_data['form_type']}")
                    st.write(f"Created: {template_data['created_at']}")
                    
                    if template_data['sections']:
                        st.markdown("#### Sections:")
                        for section in template_data['sections']:
                            st.markdown(f"""
                            - **{section['name']}** ({section['type']})
                            - Page: {section['page'] + 1}
                            - Coordinates: 
                                - x: {section['coordinates']['x']:.2%}
                                - y: {section['coordinates']['y']:.2%}
                                - width: {section['coordinates']['width']:.2%}
                                - height: {section['coordinates']['height']:.2%}
                            """)
                    
                    if st.button("Delete Template", key=f"delete_{template_file.stem}"):
                        template_file.unlink()
                        st.success("Template deleted!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error reading template {template_file.name}: {str(e)}")