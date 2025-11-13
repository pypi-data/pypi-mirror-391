"""
AI Data Validator - Report Models

This file defines the data models used for the validation and
PII scan report. This is the "return value" from the main
library function, providing crucial observability for logging.
"""
from pydantic import BaseModel
from typing import List, Any

class ValidationReport(BaseModel):
    """
    A detailed report of the validation and PII scan.
    
    This is the main object returned by the library.
    It contains the clean, validated data model plus metadata
    about the PII that was found and redacted.
    """
    
    # The final, Pydantic-validated, PII-cleaned model.
    # We use 'Any' because it could be any Pydantic model
    # passed by the user (e.g., UserProfile, ProductReview).
    clean_model: Any 

    # A list of unique PII entity types found in the data.
    # Example: ['PERSON', 'EMAIL_ADDRESS', 'PHONE_NUMBER']
    pii_types_found: List[str]

    # The total count of all PII entities that were redacted.
    # Example: 4
    pii_redaction_count: int

    class Config:
        # Allows us to use arbitrary types like the user's Pydantic model
        arbitrary_types_allowed = True