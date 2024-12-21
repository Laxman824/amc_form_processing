
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

    # def render(self):
    #     st.title("Template Teaching Interface")

    #     col1, col2 = st.columns([3, 1])

    #     with col1:
    #         uploaded_file = st.file_uploader(
    #             "Upload a form template",
    #             type=['pdf', 'png', 'jpg', 'jpeg']
    #         )

    #         if uploaded_file:
    #             images = self.process_uploaded_file(uploaded_file)
    #             if images:
    #                 st.session_state.pages = images

    #                 # Page selection if PDF has multiple pages
    #                 if len(images) > 1:
    #                     page_col1, page_col2 = st.columns([3, 1])
    #                     with page_col1:
    #                         st.session_state.current_page = st.slider(
    #                             "Select Page",
    #                             0,
    #                             len(images) - 1,
    #                             st.session_state.current_page
    #                         )
    #                     with page_col2:
    #                         st.write(f"Page {st.session_state.current_page + 1} of {len(images)}")

    #                 # Display current page
    #                 current_image = st.session_state.pages[st.session_state.current_page]
    #                 if isinstance(current_image, np.ndarray):
    #                     current_image = Image.fromarray(current_image)

    #                 # First display the image normally
    #                 st.image(current_image, caption=f"Page {st.session_state.current_page + 1}", use_column_width=True)

    #                 # Then create the annotation canvas
    #                 canvas_result = st_canvas(
    #                     fill_color="rgba(255, 165, 0, 0.3)",
    #                     stroke_width=2,
    #                     stroke_color="#e00",
    #                     background_image=current_image,
    #                     drawing_mode="rect",
    #                     key=f"canvas_{st.session_state.current_page}",
    #                     update_streamlit=True,
    #                     width=current_image.width,
    #                     height=current_image.height
    #                 )

    #                 if canvas_result.json_data and canvas_result.json_data.get("objects"):
    #                     self.handle_annotations(canvas_result)

    #     with col2:
    #         st.subheader("Template Details")
            
    #         # Form for template properties
    #         with st.form("template_properties"):
    #             template_name = st.text_input("Template Name")
    #             form_type = st.selectbox(
    #                 "Form Type",
    #                 ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
    #             )
    #             submit_button = st.form_submit_button("Save Template")
                
    #             if submit_button:
    #                 if not template_name:
    #                     st.error("Please enter a template name")
    #                 elif not st.session_state.current_sections:
    #                     st.error("Please mark at least one section")
    #                 else:
    #                     self.save_template(template_name, form_type)
    #                     st.success("Template saved successfully!")

    #         # Display marked sections
    #         if st.session_state.current_sections:
    #             st.subheader("Marked Sections")
    #             for i, section in enumerate(st.session_state.current_sections):
    #                 with st.container():
    #                     col1, col2 = st.columns([3, 1])
    #                     with col1:
    #                         st.write(f"{section['name']} (Page {section['page'] + 1})")
    #                     with col2:
    #                         if st.button("Remove", key=f"remove_{i}"):
    #                             st.session_state.current_sections.pop(i)
    #                             st.experimental_rerun()

    def render_canvas(self, current_image):
            """Render the annotation canvas with point selection mode"""
            try:
                # Convert numpy array to PIL Image if needed
                if isinstance(current_image, np.ndarray):
                    current_image = Image.fromarray(current_image)
                
                # Get image dimensions
                img_width = current_image.width
                img_height = current_image.height
                
                # Scale down if image is too large
                max_width = 1000
                if img_width > max_width:
                    scale_factor = max_width / img_width
                    img_width = max_width
                    img_height = int(img_height * scale_factor)
                    current_image = current_image.resize((img_width, img_height))

                # Display the image
                st.image(current_image, use_column_width=True)

                # Selection mode
                selection_mode = st.radio(
                    "Selection Mode",
                    ["Draw Rectangle", "Click Points (4-point)"],
                    horizontal=True
                )

                if selection_mode == "Draw Rectangle":
                    # Regular rectangle drawing canvas
                    canvas_result = st_canvas(
                        background_color="rgba(255, 255, 255, 0)",
                        fill_color="rgba(255, 165, 0, 0.3)",
                        stroke_width=2,
                        stroke_color="#e00",
                        background_image=current_image,
                        drawing_mode="rect",
                        key=f"canvas_rect_{st.session_state.current_page}",
                        width=img_width,
                        height=img_height,
                        display_toolbar=True,
                    )
                    
                    return {"mode": "rectangle", "result": canvas_result}
                
                else:
                    # Point selection canvas
                    if 'points' not in st.session_state:
                        st.session_state.points = []

                    # Clear points button
                    if st.button("Clear Points"):
                        st.session_state.points = []
                        st.experimental_rerun()

                    # Point selection canvas
                    point_canvas = st_canvas(
                        background_color="rgba(255, 255, 255, 0)",
                        fill_color="#ff0000",
                        stroke_width=3,
                        stroke_color="#ff0000",
                        background_image=current_image,
                        drawing_mode="point",
                        point_display_radius=3,
                        key=f"canvas_point_{st.session_state.current_page}",
                        width=img_width,
                        height=img_height,
                    )

                    # Handle point selection
                    if point_canvas.json_data and point_canvas.json_data.get("objects"):
                        latest_point = point_canvas.json_data["objects"][-1]
                        if latest_point not in st.session_state.points:
                            st.session_state.points.append(latest_point)

                    # Show selected points
                    if st.session_state.points:
                        st.write(f"Selected {len(st.session_state.points)}/4 points")
                        
                        # Create section button appears when 4 points are selected
                        if len(st.session_state.points) == 4:
                            if st.button("Create Section from Points"):
                                # Convert points to rectangle
                                x_coords = [p['left'] for p in st.session_state.points]
                                y_coords = [p['top'] for p in st.session_state.points]
                                
                                # Create rectangle from points
                                rect = {
                                    "left": min(x_coords),
                                    "top": min(y_coords),
                                    "width": max(x_coords) - min(x_coords),
                                    "height": max(y_coords) - min(y_coords)
                                }
                                
                                # Clear points for next selection
                                st.session_state.points = []
                                
                                return {"mode": "points", "result": {"json_data": {"objects": [rect]}}}
                    
                    return {"mode": "points", "result": None}

            except Exception as e:
                st.error(f"Error setting up annotation canvas: {str(e)}")
                return None

        def handle_annotations(self, canvas_data):
            """Handle annotations from both rectangle and point selection modes"""
            if not canvas_data:
                return

            mode = canvas_data["mode"]
            canvas_result = canvas_data["result"]

            if canvas_result and canvas_result.json_data:
                objects = canvas_result.json_data.get("objects", [])
                if objects:
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

                            rect = objects[-1]
                            new_section = {
                                "name": section_name,
                                "type": section_type,
                                "coordinates": {
                                    "x": rect["left"] / canvas_result.width,
                                    "y": rect["top"] / canvas_result.height,
                                    "width": rect["width"] / canvas_result.width,
                                    "height": rect["height"] / canvas_result.height
                                },
                                "page": st.session_state.current_page
                            }
                            st.session_state.current_sections.append(new_section)
                            st.success(f"Added section: {section_name}")
                            
    # def render_canvas(self, current_image):
    #     """Render the annotation canvas with proper error handling"""
    #     try:
    #         # Convert numpy array to PIL Image if needed
    #         if isinstance(current_image, np.ndarray):
    #             current_image = Image.fromarray(current_image)
                
    #         # Get image dimensions
    #         img_width = current_image.width
    #         img_height = current_image.height
            
    #         # Scale down if image is too large
    #         max_width = 1000
    #         if img_width > max_width:
    #             scale_factor = max_width / img_width
    #             img_width = max_width
    #             img_height = int(img_height * scale_factor)
    #             current_image = current_image.resize((img_width, img_height))

    #         # First display the image
    #         st.image(current_image, use_column_width=True)
            
    #         # Then create canvas with the same dimensions
    #         canvas_result = st_canvas(
    #             background_color="rgba(255, 255, 255, 0)",  # Transparent background
    #             fill_color="rgba(255, 165, 0, 0.3)",      # Semi-transparent orange
    #             stroke_width=2,
    #             stroke_color="#e00",
    #             background_image=current_image,
    #             drawing_mode="rect",
    #             key=f"canvas_{st.session_state.current_page}_{datetime.now().timestamp()}",  # Unique key
    #             width=img_width,
    #             height=img_height,
    #             display_toolbar=True,
    #         )
            
    #         return canvas_result
            
    #     except Exception as e:
    #         st.error(f"Error setting up annotation canvas: {str(e)}")
    #         st.error("Please try uploading the file again or contact support.")
    #         return None

    # def render(self):
    #         st.title("Template Teaching Interface")

    #         # Add instructions
    #         with st.expander("How to Mark Sections", expanded=True):
    #             st.markdown("""
    #             ### Instructions for Marking Sections:
    #             1. **Navigate Pages**: Use the slider to move between pages
    #             2. **Mark Sections**: 
    #             - Draw a rectangle around the section
    #             - Enter section name and type
    #             - Click 'Add Section'
    #             3. **Review Sections**: Check marked sections list on the right
    #             4. **Save Template**: Enter template name and save when done
    #             """)

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

    #                     # Enhanced page navigation
    #                     if len(images) > 1:
    #                         st.markdown("### Page Navigation")
    #                         page_col1, page_col2, page_col3 = st.columns([2, 1, 1])
                            
    #                         with page_col1:
    #                             st.session_state.current_page = st.slider(
    #                                 "Select Page",
    #                                 0,
    #                                 len(images) - 1,
    #                                 st.session_state.current_page
    #                             )
    #                         with page_col2:
    #                             st.write(f"Page {st.session_state.current_page + 1} of {len(images)}")
    #                         with page_col3:
    #                             # Count sections on current page
    #                             current_page_sections = len([
    #                                 s for s in st.session_state.current_sections 
    #                                 if s['page'] == st.session_state.current_page
    #                             ])
    #                             st.write(f"Sections on page: {current_page_sections}")

    #                     # Display current page
    #                     current_image = st.session_state.pages[st.session_state.current_page]
    #                     if isinstance(current_image, np.ndarray):
    #                         current_image = Image.fromarray(current_image)

    #                     st.markdown("### Current Page View")
    #                     st.image(current_image, caption=f"Page {st.session_state.current_page + 1}", use_column_width=True)

    #                     st.markdown("### Draw Sections")
    #                     st.caption("Click and drag to draw a rectangle around a section")
                        
    #                     # Annotation canvas
    #                     canvas_result = st_canvas(
    #                         fill_color="rgba(255, 165, 0, 0.3)",
    #                         stroke_width=2,
    #                         stroke_color="#e00",
    #                         background_image=current_image,
    #                         drawing_mode="rect",
    #                         key=f"canvas_{st.session_state.current_page}",
    #                         update_streamlit=True,
    #                         width=current_image.width,
    #                         height=current_image.height
    #                     )

    #                     if canvas_result.json_data and canvas_result.json_data.get("objects"):
    #                         self.handle_annotations(canvas_result)

    #         with col2:
    #             st.subheader("Template Details")
                
    #             # Display sections grouped by page
    #             if st.session_state.current_sections:
    #                 st.markdown("### Marked Sections by Page")
                    
    #                 # Group sections by page
    #                 sections_by_page = {}
    #                 for section in st.session_state.current_sections:
    #                     page = section['page']
    #                     if page not in sections_by_page:
    #                         sections_by_page[page] = []
    #                     sections_by_page[page].append(section)
                    
    #                 # Display sections grouped by page
    #                 for page in sorted(sections_by_page.keys()):
    #                     with st.expander(f"Page {page + 1}", expanded=True):
    #                         for section in sections_by_page[page]:
    #                             cols = st.columns([3, 1])
    #                             with cols[0]:
    #                                 st.write(f"• {section['name']} ({section['type']})")
    #                             with cols[1]:
    #                                 if st.button("Remove", key=f"remove_{page}_{section['name']}"):
    #                                     st.session_state.current_sections.remove(section)
    #                                     st.experimental_rerun()
                
    #             st.markdown("---")
                
    #             # Template saving form
    #             with st.form("template_properties"):
    #                 st.markdown("### Save Template")
    #                 template_name = st.text_input("Template Name")
    #                 form_type = st.selectbox(
    #                     "Form Type",
    #                     ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
    #                 )
    #                 submit_button = st.form_submit_button("Save Template")
                    
    #                 if submit_button:
    #                     if not template_name:
    #                         st.error("Please enter a template name")
    #                     elif not st.session_state.current_sections:
    #                         st.error("Please mark at least one section")
    #                     else:
    #                         self.save_template(template_name, form_type)
    #                         st.success("Template saved successfully!")
    def render(self):
            """Main render method for template teaching interface"""
            st.title("Form Template Teaching Interface")

            # Instructions
            with st.expander("Instructions", expanded=False):
                st.markdown("""
                ### How to Create a Template:
                1. **Upload Form**: Upload a PDF or image file
                2. **Navigate Pages**: Use slider to move between pages (for PDFs)
                3. **Mark Sections**: Draw rectangles around important sections
                4. **Name Sections**: Name and categorize each marked section
                5. **Save Template**: Give your template a name and save it
                
                ### Available Section Types:
                - SIP Details
                - OTM Section
                - Transaction Type
                - Other
                """)

            # Main layout
            col1, col2 = st.columns([3, 1])

            with col1:
                # File Upload
                uploaded_file = st.file_uploader(
                    "Upload a form template",
                    type=['pdf', 'png', 'jpg', 'jpeg'],
                    help="Upload a PDF or image file of the form template"
                )

                if uploaded_file:
                    # Process uploaded file
                    images = self.process_uploaded_file(uploaded_file)
                    
                    if images:
                        st.session_state.pages = images

                        # Page Navigation (for PDFs)
                        if len(images) > 1:
                            st.markdown("### Page Navigation")
                            cols = st.columns([3, 1])
                            with cols[0]:
                                page_num = st.slider(
                                    "Select Page",
                                    0,
                                    len(images) - 1,
                                    st.session_state.current_page
                                )
                                st.session_state.current_page = page_num
                            with cols[1]:
                                st.markdown(f"**Page {page_num + 1} of {len(images)}**")

                        # Display current page and canvas
                        current_image = st.session_state.pages[st.session_state.current_page]
                        
                        # Section marking interface
                        st.markdown("### Mark Sections")
                        st.caption("Click and drag to draw rectangles around form sections")
                        
                        canvas_result = self.render_canvas(current_image)
                        
                        if canvas_result and canvas_result.json_data and canvas_result.json_data.get("objects"):
                            self.handle_annotations(canvas_result)

            # Right sidebar for template management
            with col2:
                st.markdown("### Template Details")
                
                # Template properties form
                with st.form("template_properties"):
                    template_name = st.text_input("Template Name")
                    form_type = st.selectbox(
                        "Form Type",
                        ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
                    )
                    
                    # Display counts
                    if st.session_state.current_sections:
                        total_sections = len(st.session_state.current_sections)
                        current_page_sections = len([
                            s for s in st.session_state.current_sections 
                            if s['page'] == st.session_state.current_page
                        ])
                        st.markdown(f"""
                        - Total sections marked: {total_sections}
                        - Sections on current page: {current_page_sections}
                        """)
                    
                    if st.form_submit_button("Save Template"):
                        if not template_name:
                            st.error("Please enter a template name")
                        elif not st.session_state.current_sections:
                            st.error("Please mark at least one section")
                        else:
                            try:
                                self.save_template(template_name, form_type)
                                st.success(f"Template '{template_name}' saved successfully!")
                            except Exception as e:
                                st.error(f"Error saving template: {str(e)}")

                # Display marked sections
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
                        with st.expander(f"Page {page + 1}", 
                                    expanded=(page == st.session_state.current_page)):
                            for idx, section in enumerate(sections_by_page[page]):
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.markdown(f"""
                                    **{section['name']}**  
                                    Type: {section['type']}
                                    """)
                                with cols[1]:
                                    if st.button("🗑️", key=f"delete_{page}_{idx}"):
                                        st.session_state.current_sections.remove(section)
                                        st.experimental_rerun()

                # Template statistics and validation
                if st.session_state.get('pages'):
                    st.markdown("### Template Statistics")
                    total_pages = len(st.session_state.pages)
                    total_sections = len(st.session_state.current_sections)
                    pages_with_sections = len(sections_by_page) if 'sections_by_page' in locals() else 0
                    
                    st.markdown(f"""
                    - Total Pages: {total_pages}
                    - Total Sections: {total_sections}
                    - Pages with sections: {pages_with_sections}/{total_pages}
                    """)
                    
                    # Validation warnings
                    if total_pages > pages_with_sections:
                        st.warning(f"{total_pages - pages_with_sections} pages have no sections marked")

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