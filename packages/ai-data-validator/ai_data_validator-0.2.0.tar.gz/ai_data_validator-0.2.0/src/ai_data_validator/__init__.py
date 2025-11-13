"""
AI Data Validator Library
Core module for data validation and PII redaction.

Version 0.2.0:
- Now returns a detailed 'ValidationReport' for observability.
- Supports custom redaction strategies via 'custom_operators'.
- Fully recursive PII scanning for nested objects and lists.
"""

from pydantic import BaseModel, ValidationError
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from typing import Type, Any, Dict, List, Tuple, Optional

# Import our new report model from the other file
from .report import ValidationReport

# --- 1. Initialize Engines Globally (Performance) ---
# This is a critical performance optimization. We initialize these
# engines ONCE when the library is imported. This prevents the
# large spaCy NER model from being reloaded on every API call.
print("Initializing PII Analyzer Engine... (This may take a moment)")
try:
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    print("PII Analyzer Engine initialized successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not initialize Presidio engines: {e}")
    print("This is often due to a missing spaCy model. Please run:")
    print("python -m spacy download en_core_web_lg")
    analyzer = None
    anonymizer = None

# --- 2. Define Default Redaction Rules ---
# This is the default strategy if the user provides none.
# We replace PII with a clear, bracketed placeholder.
DEFAULT_OPERATORS = {
    "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[REDACTED_EMAIL]"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED_PHONE]"}),
    "CREDIT_CARD_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED_CC]"}),
    "LOCATION": OperatorConfig("replace", {"new_value": "[REDACTED_LOCATION]"}),
    "PERSON": OperatorConfig("replace", {"new_value": "[REDACTED_PERSON]"}),
}

# --- 3. Internal Recursive Cleaning Engine ---

def _scan_and_clean_string(
    text: str, 
    operators: Dict[str, OperatorConfig]
) -> Tuple[str, List[str]]:
    """
    Internal helper: Runs Presidio on a single string.
    
    Returns a tuple containing:
    1. The cleaned (anonymized) text.
    2. A list of PII types found (e.g., ['PERSON', 'PERSON']).
    """
    if not analyzer:
        return text, []  # Fail safe if engine didn't load
        
    try:
        # 1. Analyze (Detect)
        analyze_results = analyzer.analyze(text=text, language='en')
        if not analyze_results:
            return text, []

        # 2. Anonymize (Redact)
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=analyze_results,
            operators=operators
        )
        
        # 3. Report
        # We return a list of all entity types found, not unique.
        # This allows us to get a total count later.
        found_types = [res.entity_type for res in analyze_results]
        
        return anonymized_result.text, found_types
        
    except Exception:
        # If Presidio fails for any reason, return the original text
        return text, []

def _recursively_clean_object(
    data_obj: Any, 
    operators: Dict[str, OperatorConfig]
) -> Tuple[Any, List[str]]:
    """
    Recursively crawls a data structure (dict, list) and
    runs the PII cleaner on all string values.
    
    Returns a tuple containing:
    1. The fully cleaned object (dict, list, etc.).
    2. A flat list of all PII types found during recursion.
    """
    all_found_types = []

    if isinstance(data_obj, dict):
        # It's a dict, recurse on its values
        cleaned_dict = {}
        for key, value in data_obj.items():
            (cleaned_value, found_types) = _recursively_clean_object(value, operators)
            cleaned_dict[key] = cleaned_value
            all_found_types.extend(found_types)
        return cleaned_dict, all_found_types

    elif isinstance(data_obj, list):
        # It's a list, recurse on its items
        cleaned_list = []
        for item in data_obj:
            (cleaned_item, found_types) = _recursively_clean_object(item, operators)
            cleaned_list.append(cleaned_item)
            all_found_types.extend(found_types)
        return cleaned_list, all_found_types

    elif isinstance(data_obj, str):
        # It's a string! This is the base case. Clean it.
        return _scan_and_clean_string(data_obj, operators)

    else:
        # It's an int, bool, float, None... just return it as-is.
        return data_obj, []

# --- 4. The Public Function (Main Entrypoint) ---

def validate_and_clean(
    *,
    data: dict,
    model: Type[BaseModel],
    custom_operators: Optional[Dict[str, OperatorConfig]] = None
) -> ValidationReport:
    """
    Validates raw data against a Pydantic model and recursively
    redacts PII from all string fields, returning a detailed report.

    This is the main function of the library.

    Args:
        data: The raw, "dirty" dictionary of input data.
        model: The Pydantic BaseModel class to validate against.
        custom_operators: (Optional) A Presidio 'operators' dictionary
                          to define custom redaction strategies (e.g.,
                          masking, hashing). If None, uses default
                          '[REDACTED_...]' replacements.

    Raises:
        pydantic.ValidationError: If the data fails schema validation.
        Exception: If the Presidio engines failed to initialize.

    Returns:
        A ValidationReport object containing:
        - .clean_model: The Pydantic model with PII redacted.
        - .pii_types_found: A unique list of PII types found.
        - .pii_redaction_count: The total number of PII items redacted.
    """
    if not analyzer or not anonymizer:
        raise Exception(
            "Presidio engines are not initialized. "
            "Please check your spaCy model installation."
        )

    # --- Step 1: Schema Validation (The "Bouncer") ---
    # This line is the Pydantic validator. If the data is
    # the wrong shape (e.g., 'age' is a string), it will
    # raise a ValidationError and stop everything.
    try:
        validated_data = model(**data)
    except ValidationError as e:
        print(f"Data validation failed: {e}")
        raise e # Re-raise the error to be handled by the calling API

    # --- Step 2: PII Redaction (The "Security Team") ---
    
    # Use the user's custom strategy, or our default one
    operators_to_use = custom_operators or DEFAULT_OPERATORS
    
    # Get a dict copy to clean
    data_dict = validated_data.dict()
    
    # Run the recursive cleaner
    (cleaned_data_dict, all_found_types) = _recursively_clean_object(
        data_dict, 
        operators_to_use
    )

    # --- Step 3: Package and Return the Report ---
    
    # Create the final, clean Pydantic model
    final_clean_model = model(**cleaned_data_dict)
    
    # Get unique types for the report
    unique_found_types = sorted(list(set(all_found_types)))
    
    # Get the total count for the report
    redaction_count = len(all_found_types)

    # Return the final report object
    return ValidationReport(
        clean_model=final_clean_model,
        pii_types_found=unique_found_types,
        pii_redaction_count=redaction_count
    )