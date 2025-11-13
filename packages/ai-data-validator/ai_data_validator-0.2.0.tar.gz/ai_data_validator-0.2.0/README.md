# AI Data Validator

AI Data Validator is a production-ready Python library designed to be the first line of defense for any AI or data-intensive application.  
It provides a single, powerful function to solve two of the biggest problems in production systems:

1. **Data Validation:** Ensures all incoming data (e.g., from an API request) rigorously matches a required Pydantic schema.  
2. **Data Compliance:** Automatically finds and redacts sensitive Personally Identifiable Information (PII) before it can be logged, saved, or sent to an AI model, preventing data leaks and model poisoning.

This library bundles the power of **Pydantic** (for schema enforcement) and **Microsoft’s Presidio** (for hybrid Regex + NER PII detection) into a single, observable, and flexible function.

---

## 🔑 Key Features

- **Pydantic Schema Enforcement:** Validates data shape, types, and custom rules with clear `ValidationError`s.  
- **Recursive PII Redaction:** Crawls nested data structures (dicts, lists, etc.) and cleans every string value.  
- **Hybrid PII Detection:** Uses Presidio’s `AnalyzerEngine` to detect PII using both Regex and context-aware NER models.  
- **Detailed Observability Reports:** Returns a `ValidationReport` with PII types found and total redaction count.  
- **Customizable Redaction Strategies:** Define your own masking, hashing, or replacement logic via `custom_operators`.

---

## ⚙️ Installation

### 1. Install from PyPI (coming soon)
```bash
pip install ai-data-validator
````

### 2. Install for Local Development

Clone the repository:

```bash
git clone https://github.com/your-username/ai-data-validator.git
cd ai-data-validator
```

Install in editable mode (links the package to your Python environment):

```bash
pip install -e .
```

### 3. Download the NER Model (one-time setup)

Presidio uses a spaCy NER model for smart PII detection:

```bash
python -m spacy download en_core_web_lg
```

---

## 🚀 Quick Start: Default Validation

This example shows the default behavior — validating a schema and redacting PII with `[REDACTED_...]` placeholders.

```python
from pydantic import BaseModel, EmailStr
from pydantic.errors import ValidationError
from ai_data_validator import validate_and_clean

# 1. Define your expected data schema
class UserComment(BaseModel):
    username: str
    comment_text: str

# 2. Get your "dirty" data from an API request
dirty_data = {
    "username": "John Doe",
    "comment_text": "My email is john.doe@example.com."
}

# 3. Validate and clean the data in one line
try:
    report = validate_and_clean(
        data=dirty_data,
        model=UserComment
    )

    # The report gives you everything you need:
    print(f"PII Types Found: {report.pii_types_found}")
    print(f"Total Redactions: {report.pii_redaction_count}")

    # The .clean_model is the final, safe-to-use object
    print("\n--- Clean Model ---")
    print(report.clean_model.json(indent=2))

except ValidationError as e:
    print(f"Data is invalid and was rejected: {e}")
```

**Output:**

```text
PII Types Found: ['EMAIL_ADDRESS', 'PERSON']
Total Redactions: 2

--- Clean Model ---
{
  "username": "[REDACTED_PERSON]",
  "comment_text": "My email is [REDACTED_EMAIL]."
}
```

---

## 🧠 Advanced Usage: Custom Redaction Strategy (Masking)

This library gives you full control.
Here, we’ll replace `PERSON` with `[CUSTOMER]` but mask phone numbers.

```python
from pydantic import BaseModel
from ai_data_validator import validate_and_clean
from presidio_anonymizer.entities import OperatorConfig

# 1. Define your schema
class SupportTicket(BaseModel):
    customer_name: str
    issue_description: str

# 2. Define a custom redaction strategy
custom_strategy = {
    "PERSON": OperatorConfig("replace", {"new_value": "[CUSTOMER]"}),
    "PHONE_NUMBER": OperatorConfig(
        "mask",
        {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 7,
            "from_end": True
        }
    )
    # Any PII type not in this dict (like EMAIL_ADDRESS)
    # will use the DEFAULT operator: [REDACTED]
}

# 3. Define dirty data
dirty_data = {
    "customer_name": "Jane Smith",
    "issue_description": "Hi, my phone is (555) 123-4567. Please call me."
}

# 4. Run the validator with our custom strategy
report = validate_and_clean(
    data=dirty_data,
    model=SupportTicket,
    custom_operators=custom_strategy
)

print(report.clean_model.json(indent=2))
```

**Output:**

```text
{
  "customer_name": "[CUSTOMER]",
  "issue_description": "Hi, my phone is (***) ***-4567. Please call me."
}
```

---

## 📘 API Reference

### `validate_and_clean(data, model, custom_operators=None)`

**Parameters:**

* `data (dict)`: The raw, unvalidated input dictionary.
* `model (Type[BaseModel])`: The Pydantic model to validate against.
* `custom_operators (Optional[Dict[str, OperatorConfig]])`: Custom Presidio operator configs for entity types.

**Returns:**
A `ValidationReport` object.

**Raises:**

* `pydantic.ValidationError`: If input fails validation.
* `Exception`: If Presidio engines fail to initialize (e.g., spaCy model missing).

---

### `ValidationReport` (Return Object)

**Attributes:**

* `.clean_model (BaseModel)`: Validated and cleaned Pydantic model.
* `.pii_types_found (List[str])`: List of unique PII entities found.
* `.pii_redaction_count (int)`: Total number of redactions performed.

---

## 🧩 Architectural Notes

* **Global Engine Initialization:**
  The Presidio `AnalyzerEngine` and `AnonymizerEngine` are initialized globally when the library loads.
  This prevents the large (800MB+) spaCy NER model from being reloaded on every call — improving production performance.

---

## 🛠️ License & Credits

Built with ❤️ using:

* [Pydantic](https://docs.pydantic.dev/)
* [Microsoft Presidio](https://github.com/microsoft/presidio)
* [spaCy](https://spacy.io/)
`
