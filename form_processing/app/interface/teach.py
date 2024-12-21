import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import cv2
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import base64

@dataclass
class Section:
    name: str
    type: str
    coordinates: Dict[str, float]
    validation_rules: Dict[str, any]
    page_number: int

@dataclass
class FormTemplate:
    name: str
    form_type: str
    sections: List[Section]
    identifier_marks: Dict[str, any]
    version: str = "1.0"

class TemplateTeachingInterface:
    def __init__(self):
        self.section_types = [
            "SIP Details",
            "OTM Section",
            "Transaction Type",
            "Section 8",
            "Scheme Details",
            "Other"
        ]
        
        self.validation_types = [
            "Checkbox Present",
            "Text Field Filled",
            "Table Has Entries",
            "Bank Details Present",
            "Signature Present"
        ]
        
    def initialize_session_state(self):
        """Initialize session state variables for template teaching"""
        if 'current_sections' not in st.session_state:
            st.session_state.current_sections = []
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        if 'pages' not in st.session_state:
            st.session_state.pages = []
            
    def convert_image_to_base64(self, image):
        """Convert image to base64 string"""
        if isinstance(image, np.ndarray):
            # Convert numpy array to PIL Image
            image = Image.fromarray(image)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def process_uploaded_file(self, uploaded_file):
        """Process uploaded file and convert to images"""
        if uploaded_file.type == "application/pdf":
            # Handle PDF conversion
            images = convert_pdf_to_images(uploaded_file)
        else:
            # Handle image files
            image = Image.open(uploaded_file)
            images = [np.array(image)]
        
        st.session_state.pages = images
        return images

    def render_annotation_interface(self, image):
        """Render the annotation interface with drawable canvas"""
        # Convert numpy array to PIL Image if necessary
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
            
        # Create canvas for annotation
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Orange with transparency
            stroke_width=2,
            stroke_color="#e00",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="rect",
            key=f"canvas_{st.session_state.current_page}"
        )
        
        return canvas_result

    def render_section_properties(self, canvas_result):
        """Render interface for setting section properties"""
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
            # Get the last drawn object
            last_object = canvas_result.json_data["objects"][-1]
            
            with st.form("section_properties"):
                st.subheader("Section Properties")
                
                # Basic properties
                section_name = st.text_input("Section Name")
                section_type = st.selectbox("Section Type", self.section_types)
                
                # Validation rules
                st.subheader("Validation Rules")
                validation_type = st.multiselect("Validation Types", self.validation_types)
                
                # Additional rules based on section type
                if section_type == "OTM Section":
                    st.checkbox("Check for Bank Account Number")
                    st.checkbox("Check for IFSC Code")
                elif section_type == "SIP Details":
                    st.checkbox("Check for Frequency")
                    st.checkbox("Check for Amount")
                
                if st.form_submit_button("Add Section"):
                    # Calculate relative coordinates
                    coords = {
                        "x": last_object["left"] / canvas_result.width,
                        "y": last_object["top"] / canvas_result.height,
                        "width": last_object["width"] / canvas_result.width,
                        "height": last_object["height"] / canvas_result.height
                    }
                    
                    # Create new section
                    new_section = Section(
                        name=section_name,
                        type=section_type,
                        coordinates=coords,
                        validation_rules={"types": validation_type},
                        page_number=st.session_state.current_page
                    )
                    
                    st.session_state.current_sections.append(new_section)
                    st.success(f"Added section: {section_name}")

    def render_template_creation(self):
        """Main interface for template creation"""
        st.title("Create Form Template")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a sample form",
            type=['pdf', 'png', 'jpg', 'jpeg']
        )
        
        if uploaded_file:
            # Process uploaded file
            images = self.process_uploaded_file(uploaded_file)
            
            # Page navigation
            if len(images) > 1:
                st.session_state.current_page = st.slider(
                    "Page",
                    0,
                    len(images) - 1,
                    st.session_state.current_page
                )
            
            # Display current page with annotation interface
            current_image = images[st.session_state.current_page]
            canvas_result = self.render_annotation_interface(current_image)
            
            # Section properties interface
            col1, col2 = st.columns([2, 1])
            with col1:
                self.render_section_properties(canvas_result)
            
            with col2:
                # Display current sections
                st.subheader("Current Sections")
                for i, section in enumerate(st.session_state.current_sections):
                    st.write(f"{i+1}. {section.name} ({section.type})")
                    if st.button(f"Remove {section.name}"):
                        st.session_state.current_sections.pop(i)
                        st.experimental_rerun()
            
            # Template saving interface
            with st.expander("Save Template"):
                template_name = st.text_input("Template Name")
                form_type = st.selectbox(
                    "Form Type",
                    ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
                )
                
                if st.button("Save Template"):
                    template = FormTemplate(
                        name=template_name,
                        form_type=form_type,
                        sections=st.session_state.current_sections,
                        identifier_marks={
                            "form_image": self.convert_image_to_base64(images[0])
                        }
                    )
                    
                    # Save template logic
                    self.save_template(template)
                    st.success("Template saved successfully!")

    def save_template(self, template: FormTemplate):
        """Save template to file"""
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)
        
        template_path = template_dir / f"{template.name.lower().replace(' ', '_')}.json"
        with open(template_path, "w") as f:
            json.dump(asdict(template), f, indent=4)

def convert_pdf_to_images(pdf_file):
    """Convert PDF to list of images"""
    # Add PDF conversion logic here
    # You can use pdf2image library
    return []