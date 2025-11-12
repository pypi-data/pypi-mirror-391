"""
Dataset cleaning example for Sentinel PII SDK
"""

import json
from sentinel_pii import clean_dataset, PIIHandlingMode

# First, create a sample input JSONL file
sample_data = [
    {
        "messages": [
            {"role": "user", "content": "My name is John Smith and email is john@email.com"},
            {"role": "assistant", "content": "Hello John! I can help you with that."}
        ]
    },
    {
        "messages": [
            {"role": "user", "content": "Patient DOB: 1990-05-15, diagnosis: diabetes"},
            {"role": "assistant", "content": "I've recorded that information."}
        ]
    }
]

# Write sample data
print("Creating sample input file...")
with open("sample_input.jsonl", "w") as f:
    for item in sample_data:
        f.write(json.dumps(item) + "\n")

# Clean the dataset
print("Processing dataset...")
clean_dataset(
    input_filename="sample_input.jsonl",
    output_filename="sample_output.jsonl",
    mode=PIIHandlingMode.TAG
)

# Display results
print("\n=== Results ===\n")
print("Input:")
with open("sample_input.jsonl") as f:
    for line in f:
        print(json.dumps(json.loads(line), indent=2))

print("\nOutput:")
with open("sample_output.jsonl") as f:
    for line in f:
        print(json.dumps(json.loads(line), indent=2))
