# amc_form_processing
# Form Processing System

A Streamlit-based application for processing and validating financial forms.

## Features

- Form type identification (CAF, SIP, Multiple SIP)
- Section detection and validation
- Template teaching interface
- Form processing interface
- Support for multiple pages and form types

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd form-processing
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# For Windows
# Install Tesseract-OCR and add to PATH
# Install Poppler and add to PATH
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app/main.py
```

2. Access the application at `http://localhost:8501`

## Project Structure

```
form_processing/
├── app/
│   ├── main.py            # Main Streamlit application
│   ├── interface/         # User interfaces
│   ├── core/             # Core processing logic
│   ├── models/           # Data models
│   └── utils/            # Utility functions
├── templates/            # Stored form templates
├── data/                # Sample forms and test data
└── requirements.txt
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Check types: `mypy .`

## License

[Add License Information]