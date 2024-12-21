# app/models/template.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

class SectionType(Enum):
    SIP_DETAILS = "SIP Details"
    OTM_SECTION = "OTM Section"
    TRANSACTION_TYPE = "Transaction Type"
    SECTION_8 = "Section 8"
    SCHEME_DETAILS = "Scheme Details"
    OTHER = "Other"

class ValidationRule(Enum):
    CHECKBOX = "Checkbox Present"
    TEXT_FIELD = "Text Field Filled"
    TABLE_ENTRIES = "Table Has Entries"
    BANK_DETAILS = "Bank Details Present"
    SIGNATURE = "Signature Present"

@dataclass
class BoundingBox:
    x: float  # Relative coordinates (0-1)
    y: float
    width: float
    height: float
    page: int

@dataclass
class Section:
    name: str
    type: SectionType
    bounding_box: BoundingBox
    validation_rules: List[ValidationRule]
    required: bool = True
    additional_rules: Dict = None

@dataclass
class Template:
    name: str
    form_type: str
    sections: List[Section]
    identifier_marks: Dict[str, any]
    version: str = "1.0"
    total_pages: int = 1

