"""
Basic usage example for Sentinel PII SDK
"""

from sentinel_pii import SentinelPIIRedactor, PIIHandlingMode

# Initialize the redactor (model loads from HuggingFace on first use)
redactor = SentinelPIIRedactor()

# Example text with PII
text = "My name is John Smith and my email is john@email.com. I live at 123 Main St, New York, NY 10001."

# TAG mode - Show PII categories
print("=== TAG Mode ===")
result = redactor.redact_text(text, mode=PIIHandlingMode.TAG)
print(result)
print()

# REDACT mode - Same as TAG for this model
print("=== REDACT Mode ===")
result = redactor.redact_text(text, mode=PIIHandlingMode.REDACT)
print(result)
print()

# REPLACE mode - Replace with fake data (requires 'pip install sentinel-pii-sdk[faker]')
print("=== REPLACE Mode ===")
try:
    result = redactor.redact_text(text, mode=PIIHandlingMode.REPLACE)
    print(result)
except ImportError as e:
    print(f"Install faker to use REPLACE mode: pip install 'sentinel-pii-sdk[faker]'")
