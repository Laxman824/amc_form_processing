from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TestCase:
    name: str
    form_type: str
    file_path: str
    expected_results: Dict
    sections: List[Dict]

# Test cases for different form types
TEST_CASES = [
    TestCase(
        name="CAF_Complete",
        form_type="CA Form",
        file_path="tests/data/caf_complete.pdf",
        expected_results={
            'sip_details_filled': True,
            'otm_details_filled': True
        },
        sections=[
            {
                'name': 'section8',
                'page': 1,
                'expected': {
                    'sip_checkbox_checked': True,
                    'sip_details_filled': True
                }
            },
            {
                'name': 'otm',
                'page': 2,
                'expected': {
                    'account_number_found': True,
                    'ifsc_found': True
                }
            }
        ]
    ),
    TestCase(
        name="SIP_Complete",
        form_type="SIP Form",
        file_path="tests/data/sip_complete.pdf",
        expected_results={
            'sip_details_filled': True,
            'otm_details_filled': True
        },
        sections=[
            {
                'name': 'transaction_type',
                'page': 0,
                'expected': {
                    'type_detected': 'registration',
                    'checkbox_checked': True
                }
            },
            {
                'name': 'otm',
                'page': 1,
                'expected': {
                    'account_number_found': True,
                    'ifsc_found': True
                }
            }
        ]
    )
]

# Validation test patterns
VALIDATION_PATTERNS = {
    'bank_account': r'\d{9,18}',
    'ifsc': r'[A-Z]{4}0[A-Z0-9]{6}',
    'pan': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
    'amount': r'(?:rs|inr|₹)?\s*\d+(?:,\d+)*(?:\.\d{2})?',
    'date': r'\d{2}[-/]\d{2}[-/]\d{2,4}'
}

# Test section coordinates
TEST_SECTIONS = {
    'CA Form': {
        'section8': {'x': 0.1, 'y': 0.2, 'width': 0.8, 'height': 0.3},
        'otm': {'x': 0.1, 'y': 0.6, 'width': 0.8, 'height': 0.3}
    },
    'SIP Form': {
        'transaction_type': {'x': 0.1, 'y': 0.1, 'width': 0.8, 'height': 0.2},
        'sip_details': {'x': 0.1, 'y': 0.3, 'width': 0.8, 'height': 0.3},
        'otm': {'x': 0.1, 'y': 0.6, 'width': 0.8, 'height': 0.3}
    }
}