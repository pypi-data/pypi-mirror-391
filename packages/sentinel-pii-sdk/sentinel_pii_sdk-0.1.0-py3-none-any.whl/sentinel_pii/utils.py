"""
Utility functions for batch processing and dataset cleaning
"""

import json
from typing import List, Optional
from tqdm import tqdm

from .redactor import SentinelPIIRedactor, PIIHandlingMode


def detect_pii_batch(
    documents: List[str],
    mode: PIIHandlingMode = PIIHandlingMode.TAG,
    locale: str = "en_US",
) -> List[str]:
    """
    Convenience function to detect PII in multiple documents.

    Args:
        documents: List of text documents to process
        mode: How to handle identified PII (TAG, REDACT, or REPLACE)
        locale: Locale for generating fake data (only used if mode=REPLACE)

    Returns:
        List of documents with PII handled according to mode

    Examples:
        >>> from sentinel_pii import detect_pii_batch, PIIHandlingMode
        >>>
        >>> docs = ["My email is john@example.com"]
        >>> result = detect_pii_batch(docs, mode=PIIHandlingMode.TAG)
        >>> print(result[0])
        'My email is [EMAIL_ADDRESS]'
    """
    redactor = SentinelPIIRedactor()
    return redactor.detect_pii(documents, mode=mode, locale=locale)


def clean_dataset(
    input_filename: str,
    output_filename: str,
    mode: PIIHandlingMode = PIIHandlingMode.TAG,
    locale: str = "en_US",
):
    """
    Process a JSONL dataset file with PII detection.

    This function reads a JSONL file where each line is a JSON object
    containing a 'messages' field (list of message objects with 'content').
    It processes all message content through PII detection and writes
    the results to an output file.

    Args:
        input_filename: Path to input JSONL file
        output_filename: Path to output JSONL file
        mode: How to handle identified PII (TAG, REDACT, or REPLACE)
        locale: Locale for generating fake data (only used if mode=REPLACE)

    Examples:
        >>> from sentinel_pii import clean_dataset, PIIHandlingMode
        >>>
        >>> clean_dataset(
        ...     "input_data.jsonl",
        ...     "output_data.jsonl",
        ...     mode=PIIHandlingMode.REDACT
        ... )
    """
    redactor = SentinelPIIRedactor()

    # Count lines for progress bar
    with open(input_filename, "r") as f:
        num_lines = sum(1 for line in f)

    with open(input_filename, "r") as fin, open(output_filename, "w") as fout:
        for line in tqdm(fin, total=num_lines, desc="Processing dataset"):
            json_obj = json.loads(line.strip())

            # Process messages in the JSON object
            if "messages" in json_obj:
                messages_to_process = []
                for message in json_obj["messages"]:
                    if message.get("content"):
                        messages_to_process.append(message["content"])

                # Process all messages
                if messages_to_process:
                    processed_messages = redactor.detect_pii(
                        messages_to_process, mode=mode, locale=locale, show_progress=False
                    )

                    # Update the JSON object
                    msg_idx = 0
                    for message in json_obj["messages"]:
                        if message.get("content"):
                            message["content"] = processed_messages[msg_idx]
                            msg_idx += 1

            # Write to output
            fout.write(json.dumps(json_obj) + "\n")
            fout.flush()

    print(f"\n✓ Processed {num_lines} records from {input_filename}")
    print(f"✓ Saved results to {output_filename}")
