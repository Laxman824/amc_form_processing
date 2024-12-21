#!/bin/bash

# Create folders
mkdir -p form_processing/app/{interface,core,models,utils} templates data

# Create files
touch form_processing/app/main.py
touch form_processing/app/interface/teach.py form_processing/app/interface/process.py
touch form_processing/app/core/{processor.py,detector.py,validator.py}
touch form_processing/app/models/{template.py,form.py}
touch form_processing/app/utils/{image.py,storage.py}
touch form_processing/requirements.txt

echo "Structure created successfully for now !"
