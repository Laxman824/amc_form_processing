import streamlit as st
from PIL import Image
import numpy as np
import cv2
import json
import os
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="Form Processing System",
    page_icon="📄",
    layout="wide"
)

class FormProcessor:
    def __init__(self):
        self.template_dir = Path("templates")
        self.template_dir.mkdir(exist_ok=True)
        
    def load_templates(self):
        """Load existing templates from directory"""
        templates = {}
        if self.template_dir.exists():
            for file in self.template_dir.glob("*.json"):
                with open(file, "r") as f:
                    templates[file.stem] = json.load(f)
        return templates

class App:
    def __init__(self):
        self.processor = FormProcessor()
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'mode' not in st.session_state:
            st.session_state.mode = 'process'  # or 'teach'
        if 'templates' not in st.session_state:
            st.session_state.templates = self.processor.load_templates()
            
    def render_sidebar(self):
        """Render the sidebar"""
        with st.sidebar:
            st.title("Form Processing System")
            mode = st.radio(
                "Mode",
                ["Process Forms", "Teach Templates"],
                key="mode_radio"
            )
            st.session_state.mode = 'process' if mode == "Process Forms" else 'teach'
            
            st.markdown("---")
            st.markdown("""
            ### Instructions
            1. Select mode (Process or Teach)
            2. Upload form
            3. View results or create template
            """)
    
    def render_teaching_interface(self):
        """Render the template teaching interface"""
        st.header("Template Teaching Interface")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader(
                "Upload a sample form",
                type=['pdf', 'png', 'jpg', 'jpeg']
            )
            
            if uploaded_file:
                # Handle form template creation
                template_name = st.text_input("Template Name")
                form_type = st.selectbox(
                    "Form Type",
                    ["CA Form", "SIP Form", "Multiple SIP Form", "Other"]
                )
                
                if st.button("Save Template"):
                    # Save template logic here
                    st.success("Template saved successfully!")
        
        with col2:
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Form")
                # Add annotation tools here
    
    def render_processing_interface(self):
        """Render the form processing interface"""
        st.header("Form Processing Interface")
        
        uploaded_files = st.file_uploader(
            "Upload form(s) for processing",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for file in uploaded_files:
                st.subheader(f"Processing: {file.name}")
                # Add processing logic here
                st.info("Processing results will appear here")
    
    def run(self):
        """Run the application"""
        self.render_sidebar()
        
        if st.session_state.mode == 'teach':
            self.render_teaching_interface()
        else:
            self.render_processing_interface()

if __name__ == "__main__":
    app = App()
    app.run()