# app/models/form.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class FormType(Enum):
    CAF = "CA Form"
    SIP = "SIP Form"
    MULTIPLE_SIP = "Multiple SIP Form"
    OTHER = "Other"

class ValidationStatus(Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    WARNING = "Warning"
    NOT_APPLICABLE = "N/A"

@dataclass
class SectionValidation:
    section_name: str
    status: ValidationStatus
    details: Dict[str, any]
    confidence: float

@dataclass
class FormValidation:
    form_type: FormType
    total_pages: int
    sections: List[SectionValidation]
    sip_details_filled: bool = False
    otm_details_filled: bool = False
    validation_timestamp: str = None