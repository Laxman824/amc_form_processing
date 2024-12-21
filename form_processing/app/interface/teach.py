# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# import numpy as np
# from PIL import Image
# import io
# import logging
# from pathlib import Path
# from datetime import datetime
# import json

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
#             st.error(f"Error processing file: {str(e)}")
#             return None

#     def render_canvas(self, current_image):
#             """Render the annotation canvas with point selection mode"""
#             try:
#                 # Convert numpy array to PIL Image if needed
#                 if isinstance(current_image, np.ndarray):
#                     current_image = Image.fromarray(current_image)
                
#                 # Get image dimensions
#                 img_width = current_image.width
#                 img_height = current_image.height
                
#                 # Scale down if image is too large
#                 max_width = 1000
#                 if img_width > max_width:
#                     scale_factor = max_width / img_width
#                     img_width = max_width
#                     img_height = int(img_height * scale_factor)
#                     current_image = current_image.resize((img_width, img_height))

#                 # Display the image
#                 st.image(current_image, use_column_width=True)

#                 # Selection mode
#                 selection_mode = st.radio(
#                     "Selection Mode",
#                     ["Draw Rectangle", "Click Points (4-point)"],
#                     horizontal=True
#                 )

#                 if selection_mode == "Draw Rectangle":
#                     # Regular rectangle drawing canvas
#                     canvas_result = st_canvas(
#                         background_color="rgba(255, 255, 255, 0)",
#                         fill_color="rgba(255, 165, 0, 0.3)",
#                         stroke_width=2,
#                         stroke_color="#e00",
#                         background_image=current_image,
#                         drawing_mode="rect",
#                         key=f"canvas_rect_{st.session_state.current_page}",
#                         width=img_width,
#                         height=img_height,
#                         display_toolbar=True,
#                     )
                    
#                     return {"mode": "rectangle", "result": canvas_result}
                
#                 else:
#                     # Point selection canvas
#                     if 'points' not in st.session_state:
#                         st.session_state.points = []

#                     # Clear points button
#                     if st.button("Clear Points"):
#                         st.session_state.points = []
#                         st.experimental_rerun()

#                     # Point selection canvas
#                     point_canvas = st_canvas(
#                         background_color="rgba(255, 255, 255, 0)",
#                         fill_color="#ff0000",
#                         stroke_width=3,
#                         stroke_color="#ff0000",
#                         background_image=current_image,
#                         drawing_mode="point",
#                         point_display_radius=3,
#                         key=f"canvas_point_{st.session_state.current_page}",
#                         width=img_width,
#                         height=img_height,
#                     )

#                     # Handle point selection
#                     if point_canvas.json_data and point_canvas.json_data.get("objects"):
#                         latest_point = point_canvas.json_data["objects"][-1]
#                         if latest_point not in st.session_state.points:
#                             st.session_state.points.append(latest_point)

#                     # Show selected points
#                     if st.session_state.points:
#                         st.write(f"Selected {len(st.session_state.points)}/4 points")
                        
#                         # Create section button appears when 4 points are selected
#                         if len(st.session_state.points) == 4:
#                             if st.button("Create Section from Points"):
#                                 # Convert points to rectangle
#                                 x_coords = [p['left'] for p in st.session_state.points]
#                                 y_coords = [p['top'] for p in st.session_state.points]
                                
#                                 # Create rectangle from points
#                                 rect = {
#                                     "left": min(x_coords),
#                                     "top": min(y_coords),
#                                     "width": max(x_coords) - min(x_coords),
#                                     "height": max(y_coords) - min(y_coords)
#                                 }
                                
#                                 # Clear points for next selection
#                                 st.session_state.points = []
                                
#                                 return {"mode": "points", "result": {"json_data": {"objects": [rect]}}}
                    
#                     return {"mode": "points", "result": None}

#             except Exception as e:
#                 st.error(f"Error setting up annotation canvas: {str(e)}")
#                 return None

#     def handle_annotations(self, canvas_data):
#         """Handle annotations from both rectangle and point selection modes"""
#         if not canvas_data:
#             return

#         mode = canvas_data["mode"]
#         canvas_result = canvas_data["result"]

#         if canvas_result and canvas_result.json_data:
#             objects = canvas_result.json_data.get("objects", [])
#             if objects:
#                 with st.form("section_properties"):
#                     st.subheader("Add Section")
#                     section_name = st.text_input("Section Name")
#                     section_type = st.selectbox(
#                         "Section Type",
#                         ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                     )
                    
#                     if st.form_submit_button("Add Section"):
#                         if not section_name:
#                             st.warning("Please enter a section name")
#                             return

#                         rect = objects[-1]
#                         new_section = {
#                             "name": section_name,
#                             "type": section_type,
#                             "coordinates": {
#                                 "x": rect["left"] / canvas_result.width,
#                                 "y": rect["top"] / canvas_result.height,
#                                 "width": rect["width"] / canvas_result.width,
#                                 "height": rect["height"] / canvas_result.height
#                             },
#                             "page": st.session_state.current_page
#                         }
#                         st.session_state.current_sections.append(new_section)
#                         st.success(f"Added section: {section_name}")

#     def render(self):
#             """Main render method for template teaching interface"""
#             st.title("Form Template Teaching Interface")

#             # Instructions
#             with st.expander("Instructions", expanded=False):
#                 st.markdown("""
#                 ### How to Create a Template:
#                 1. **Upload Form**: Upload a PDF or image file
#                 2. **Navigate Pages**: Use slider to move between pages (for PDFs)
#                 3. **Mark Sections**: Draw rectangles around important sections
#                 4. **Name Sections**: Name and categorize each marked section
#                 5. **Save Template**: Give your template a name and save it
                
#                 ### Available Section Types:
#                 - SIP Details
#                 - OTM Section
#                 - Transaction Type
#                 - Other
#                 """)

#             # Main layout
#             col1, col2 = st.columns([3, 1])

#             with col1:
#                 # File Upload
#                 uploaded_file = st.file_uploader(
#                     "Upload a form template",
#                     type=['pdf', 'png', 'jpg', 'jpeg'],
#                     help="Upload a PDF or image file of the form template"
#                 )

#                 if uploaded_file:
#                     # Process uploaded file
#                     images = self.process_uploaded_file(uploaded_file)
                    
#                     if images:
#                         st.session_state.pages = images

#                         # Page Navigation (for PDFs)
#                         if len(images) > 1:
#                             st.markdown("### Page Navigation")
#                             cols = st.columns([3, 1])
#                             with cols[0]:
#                                 page_num = st.slider(
#                                     "Select Page",
#                                     0,
#                                     len(images) - 1,
#                                     st.session_state.current_page
#                                 )
#                                 st.session_state.current_page = page_num
#                             with cols[1]:
#                                 st.markdown(f"**Page {page_num + 1} of {len(images)}**")

#                         # Display current page and canvas
#                         current_image = st.session_state.pages[st.session_state.current_page]
                        
#                         # Section marking interface
#                         st.markdown("### Mark Sections")
#                         st.caption("Click and drag to draw rectangles around form sections")
                        
#                         canvas_result = self.render_canvas(current_image)
                        
#                         if canvas_result and canvas_result.json_data and canvas_result.json_data.get("objects"):
#                             self.handle_annotations(canvas_result)

#             # Right sidebar for template management
#             with col2:
#                 st.markdown("### Template Details")
                
#                 # Template properties form
#                 with st.form("template_properties"):
#                     template_name = st.text_input("Template Name")
#                     form_type = st.selectbox(
#                         "Form Type",
#                         ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
#                     )
                    
#                     # Display counts
#                     if st.session_state.current_sections:
#                         total_sections = len(st.session_state.current_sections)
#                         current_page_sections = len([
#                             s for s in st.session_state.current_sections 
#                             if s['page'] == st.session_state.current_page
#                         ])
#                         st.markdown(f"""
#                         - Total sections marked: {total_sections}
#                         - Sections on current page: {current_page_sections}
#                         """)
                    
#                     if st.form_submit_button("Save Template"):
#                         if not template_name:
#                             st.error("Please enter a template name")
#                         elif not st.session_state.current_sections:
#                             st.error("Please mark at least one section")
#                         else:
#                             try:
#                                 self.save_template(template_name, form_type)
#                                 st.success(f"Template '{template_name}' saved successfully!")
#                             except Exception as e:
#                                 st.error(f"Error saving template: {str(e)}")

#                 # Display marked sections
#                 if st.session_state.current_sections:
#                     st.markdown("### Marked Sections")
                    
#                     # Group sections by page
#                     sections_by_page = {}
#                     for section in st.session_state.current_sections:
#                         page = section['page']
#                         if page not in sections_by_page:
#                             sections_by_page[page] = []
#                         sections_by_page[page].append(section)
                    
#                     # Display sections grouped by page
#                     for page in sorted(sections_by_page.keys()):
#                         with st.expander(f"Page {page + 1}", 
#                                     expanded=(page == st.session_state.current_page)):
#                             for idx, section in enumerate(sections_by_page[page]):
#                                 cols = st.columns([3, 1])
#                                 with cols[0]:
#                                     st.markdown(f"""
#                                     **{section['name']}**  
#                                     Type: {section['type']}
#                                     """)
#                                 with cols[1]:
#                                     if st.button("🗑️", key=f"delete_{page}_{idx}"):
#                                         st.session_state.current_sections.remove(section)
#                                         st.experimental_rerun()

#                 # Template statistics and validation
#                 if st.session_state.get('pages'):
#                     st.markdown("### Template Statistics")
#                     total_pages = len(st.session_state.pages)
#                     total_sections = len(st.session_state.current_sections)
#                     pages_with_sections = len(sections_by_page) if 'sections_by_page' in locals() else 0
                    
#                     st.markdown(f"""
#                     - Total Pages: {total_pages}
#                     - Total Sections: {total_sections}
#                     - Pages with sections: {pages_with_sections}/{total_pages}
#                     """)
                    
#                     # Validation warnings
#                     if total_pages > pages_with_sections:
#                         st.warning(f"{total_pages - pages_with_sections} pages have no sections marked")

#     def handle_annotations(self, canvas_result):
#         if len(canvas_result.json_data["objects"]) > 0:
#             last_object = canvas_result.json_data["objects"][-1]
            
#             with st.form("section_properties"):
#                 st.subheader("Add Section")
#                 section_name = st.text_input("Section Name")
#                 section_type = st.selectbox(
#                     "Section Type",
#                     ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                 )
                
#                 if st.form_submit_button("Add Section"):
#                     if not section_name:
#                         st.warning("Please enter a section name")
#                         return

#                     # Calculate relative coordinates
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
#above code is for rectangle section taking and draw 4 points but not working so 
# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# from PIL import Image, ImageDraw
# import numpy as np
# import io
# import logging
# from pathlib import Path
# from datetime import datetime
# import json
# from ..utils.pdf import pdf_to_images, is_valid_pdf
# class TemplateTeachingInterface:
#     def __init__(self):
#         self.setup_logging()
#         self.initialize_session_state()

#     def initialize_session_state(self):
#         """Initialize all session state variables"""
#         if 'current_page' not in st.session_state:
#             st.session_state.current_page = 0
#         if 'pages' not in st.session_state:
#             st.session_state.pages = []
#         if 'current_sections' not in st.session_state:
#             st.session_state.current_sections = []
#         if 'points' not in st.session_state:
#             st.session_state.points = []
#         if 'show_section_form' not in st.session_state:
#             st.session_state.show_section_form = False
#         if 'temp_section' not in st.session_state:
#             st.session_state.temp_section = None

#     def setup_logging(self):
#         self.logger = logging.getLogger(__name__)


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
#             st.error(f"Error processing file: {str(e)}")
#             return None

#     def draw_points_on_image(self, image, points):
#         """Draw points on image with numbers"""
#         draw = ImageDraw.Draw(image)
#         # Draw existing points in red with numbers
#         for i, (x, y) in enumerate(points):
#             # Draw red circle
#             draw.ellipse([x-5, y-5, x+5, y+5], fill='red')
#             # Draw point number
#             draw.text((x+10, y+10), str(i+1), fill='red')
            
#         return image

#     def handle_click(self, image):
#         """Handle click events on image"""
#         col1, col2 = st.columns([4, 1])
        
#         with col1:
#             # Calculate scaling factor
#             display_width = 800  # Fixed display width
#             scale_factor = display_width / image.width
#             display_height = int(image.height * scale_factor)
            
#             # Create copy of image for drawing
#             display_image = image.copy()
#             if st.session_state.points:
#                 display_image = self.draw_points_on_image(display_image, st.session_state.points)

#             # Display image and get click coordinates
#             clicked = st.image(display_image, width=display_width, use_column_width=False)
            
#         with col2:
#             st.write("Selected Points:", len(st.session_state.points))
#             if st.button("Clear Points"):
#                 st.session_state.points = []
#                 st.experimental_rerun()

#             if len(st.session_state.points) >= 4:
#                 if st.button("Create Section", type="primary"):
#                     # Convert points to section coordinates
#                     x_coords = [p[0] for p in st.session_state.points]
#                     y_coords = [p[1] for p in st.session_state.points]
                    
#                     # Calculate relative coordinates
#                     width = image.width
#                     height = image.height
#                     section = {
#                         "x": min(x_coords) / width,
#                         "y": min(y_coords) / height,
#                         "width": (max(x_coords) - min(x_coords)) / width,
#                         "height": (max(y_coords) - min(y_coords)) / height
#                     }
#                     return section
                    
#             elif len(st.session_state.points) < 4:
#                 st.info(f"Click {4 - len(st.session_state.points)} more points")

#         # Handle click event
#         if clicked:
#             # Get click coordinates and scale them to original image size
#             try:
#                 coordinates = st.experimental_get_query_params().get('click', [None])[0]
#                 if coordinates:
#                     x, y = map(int, coordinates.split(','))
#                     # Scale coordinates back to original image size
#                     original_x = int(x / scale_factor)
#                     original_y = int(y / scale_factor)
#                     if len(st.session_state.points) < 4:
#                         st.session_state.points.append((original_x, original_y))
#                         st.experimental_rerun()
#             except Exception as e:
#                 st.error(f"Error handling click: {str(e)}")

#         return None

#     def render_selection_interface(self, image):
#         """Render the section selection interface with reliable point selection"""
#         st.markdown("### Select Section Points")
        
#         # Create a grid of clickable points over the image
#         # First display the image
#         display_width = 800
#         scale_factor = display_width / image.width
#         display_height = int(image.height * scale_factor)
        
#         # Create copy of image for drawing
#         display_image = image.copy()
        
#         # Draw existing points
#         if st.session_state.points:
#             draw = ImageDraw.Draw(display_image)
#             for i, point in enumerate(st.session_state.points):
#                 x, y = point
#                 # Draw red circle
#                 draw.ellipse([x-5, y-5, x+5, y+5], fill='red', outline='white')
#                 # Draw number
#                 draw.text((x+7, y-7), str(i+1), fill='red', stroke_fill='white')
        
#         col1, col2 = st.columns([4, 1])
        
#         with col1:
#             # Display the image
#             st.image(display_image, width=display_width)
            
#             # Create a grid of invisible buttons over the image
#             num_rows = 10
#             num_cols = 10
            
#             # Calculate grid cell size
#             cell_width = image.width / num_cols
#             cell_height = image.height / num_rows
            
#             # Create grid of buttons
#             for row in range(num_rows):
#                 cols = st.columns(num_cols)
#                 for col in range(num_cols):
#                     with cols[col]:
#                         # Create an invisible button
#                         if st.button("", key=f"btn_{row}_{col}", help="Click to add point"):
#                             # Calculate actual coordinates
#                             x = int((col + 0.5) * cell_width)
#                             y = int((row + 0.5) * cell_height)
                            
#                             if len(st.session_state.points) < 4:
#                                 st.session_state.points.append((x, y))
#                                 st.experimental_rerun()
        
#         with col2:
#             st.write(f"Points: {len(st.session_state.points)}/4")
#             if st.button("Clear Points"):
#                 st.session_state.points = []
#                 st.experimental_rerun()
            
#             # Show create section button when 4 points are selected
#             if len(st.session_state.points) == 4:
#                 if st.button("Create Section", type="primary"):
#                     x_coords = [p[0] for p in st.session_state.points]
#                     y_coords = [p[1] for p in st.session_state.points]
                    
#                     section = {
#                         "x": min(x_coords) / image.width,
#                         "y": min(y_coords) / image.height,
#                         "width": (max(x_coords) - min(x_coords)) / image.width,
#                         "height": (max(y_coords) - min(y_coords)) / image.height
#                     }
                    
#                     # Show section properties form
#                     st.session_state.show_section_form = True
#                     st.session_state.temp_section = section
#                     st.experimental_rerun()
            
#             elif len(st.session_state.points) < 4:
#                 points_left = 4 - len(st.session_state.points)
#                 st.info(f"Select {points_left} more point{'s' if points_left > 1 else ''}")
        
#         # Show section properties form if needed
#         if st.session_state.get('show_section_form', False):
#             with st.form("section_properties"):
#                 st.subheader("Add Section")
#                 section_name = st.text_input("Section Name")
#                 section_type = st.selectbox(
#                     "Section Type",
#                     ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                 )
                
#                 if st.form_submit_button("Save Section"):
#                     if section_name:
#                         new_section = {
#                             "name": section_name,
#                             "type": section_type,
#                             "coordinates": st.session_state.temp_section,
#                             "page": st.session_state.current_page
#                         }
#                         st.session_state.current_sections.append(new_section)
#                         # Clear temporary data
#                         st.session_state.points = []
#                         st.session_state.show_section_form = False
#                         if 'temp_section' in st.session_state:
#                             del st.session_state.temp_section
#                         st.success(f"Added section: {section_name}")
#                         st.experimental_rerun()
#                     else:
#                         st.error("Please enter a section name")

#     def render(self):
#         """Main render method"""
#         st.title("Form Template Teaching")

#         uploaded_file = st.file_uploader(
#             "Upload a form template",
#             type=['pdf', 'png', 'jpg', 'jpeg']
#         )

#         if uploaded_file:
#             # Process file
#             images = self.process_uploaded_file(uploaded_file)
            
#             if images:
#                 st.session_state.pages = images

#                 # Page navigation for PDFs
#                 if len(images) > 1:
#                     current_page = st.slider(
#                         "Select Page",
#                         0,
#                         len(images) - 1,
#                         st.session_state.current_page
#                     )
#                     st.session_state.current_page = current_page

#                 # Get current image
#                 current_image = images[st.session_state.current_page]
#                 if isinstance(current_image, np.ndarray):
#                     current_image = Image.fromarray(current_image)

#                 # Show selection interface
#                 self.render_selection_interface(current_image)

#                 # Show marked sections
#                 self.render_sections_list()



#     def render_sections_list(self):
#         """Render the list of marked sections"""
#         if st.session_state.current_sections:
#             st.markdown("### Marked Sections")
#             for i, section in enumerate(st.session_state.current_sections):
#                 col1, col2 = st.columns([3, 1])
#                 with col1:
#                     st.write(f"{i+1}. {section['name']} (Page {section['page'] + 1})")
#                 with col2:
#                     if st.button("Remove", key=f"remove_{i}"):
#                         st.session_state.current_sections.pop(i)
#                         st.experimental_rerun()

# import streamlit as st
# # from streamlit_cropper import st_cropper
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
#         return image

#     def render_section_selection(self, image):
#         """Render section selection using streamlit-cropper"""
#         if isinstance(image, np.ndarray):
#             image = Image.fromarray(image)

#         # Draw existing sections on image
#         image_with_sections = self.draw_existing_sections(image.copy())
        
#         st.markdown("### Select Section")
#         st.caption("Drag to select the section area")

#         # Use streamlit-cropper for section selection
#         cropped_img = st_cropperjs(
#             image_with_sections,
#             realtime_update=True,
#             box_color='red',
#             aspect_ratio=None,
#             return_type='box',
#             key=f"cropper_{st.session_state.current_page}"
#         )

#         # Show section properties form when area is selected
#         if cropped_img and isinstance(cropped_img, dict):
#             with st.form("section_properties"):
#                 st.markdown("### Section Details")
                
#                 # Calculate relative coordinates
#                 coords = {
#                     "x": cropped_img['left'] / image.width,
#                     "y": cropped_img['top'] / image.height,
#                     "width": cropped_img['width'] / image.width,
#                     "height": cropped_img['height'] / image.height
#                 }

#                 # Section properties
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     section_name = st.text_input("Section Name")
#                 with col2:
#                     section_type = st.selectbox(
#                         "Section Type",
#                         ["SIP Details", "OTM Section", "Transaction Type", "Other"]
#                     )

#                 # Add section button
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
#         """Render list of marked sections"""
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
#             2. Drag to select sections on the form
#             3. Name and categorize each section
#             4. Save the template when done
            
#             **Tip**: Click and drag on the form to select sections
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
                
                # Draw rectangle for section
                img_draw.rectangle([x1, y1, x2, y2], 
                                outline='red', 
                                width=2)
                # Draw section name
                img_draw.text((x1, y1-20), 
                            section['name'], 
                            fill='red')

        # Convert back to bytes for cropperjs
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr

    def render_section_selection(self, image):
        """Render section selection using cropperjs"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

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
            cropped_img = Image.open(io.BytesIO(cropped_area))
            
            # Calculate relative coordinates based on cropped area
            coords = {
                "x": cropped_img.info.get('cropX', 0) / image.width,
                "y": cropped_img.info.get('cropY', 0) / image.height,
                "width": cropped_img.info.get('cropWidth', 0) / image.width,
                "height": cropped_img.info.get('cropHeight', 0) / image.height
            }

            with st.form("section_properties"):
                st.markdown("### Section Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    section_name = st.text_input("Section Name")
                with col2:
                    section_type = st.selectbox(
                        "Section Type",
                        ["SIP Details", "OTM Section", "Transaction Type", "Other"]
                    )

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
                        st.experimental_rerun()

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
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.write(f"• {section['name']} ({section['type']})")
                        with cols[1]:
                            if st.button("Remove", key=f"remove_{page}_{i}"):
                                st.session_state.current_sections.remove(section)
                                st.experimental_rerun()

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
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error saving template: {str(e)}")

            # Show marked sections
            self.render_sections_list()