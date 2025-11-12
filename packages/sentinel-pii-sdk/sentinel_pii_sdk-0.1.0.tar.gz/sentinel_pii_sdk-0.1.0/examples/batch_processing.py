"""
Batch processing example for Sentinel PII SDK
"""

from sentinel_pii import detect_pii_batch, PIIHandlingMode

# Multiple documents to process
documents = [
    "My email is john@email.com and phone is (555) 123-4567",
    "Patient ID: 12345, DOB: 1990-05-15, Diagnosed with diabetes",
    "Contact Dr. Sarah Johnson at sjohnson@hospital.org",
    "Credit card: 4532-1234-5678-9010, expires 12/25",
]

print("=== Batch Processing ===\n")

# Process all documents at once
results = detect_pii_batch(documents, mode=PIIHandlingMode.TAG)

# Display results
for i, (original, processed) in enumerate(zip(documents, results), 1):
    print(f"Document {i}:")
    print(f"  Original:  {original}")
    print(f"  Processed: {processed}")
    print()
