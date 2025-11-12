"""
Core PII redaction functionality using Sentinel model
"""

import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from enum import Enum
from typing import List, Optional, Union


class PIIHandlingMode(Enum):
    """Enum for different PII handling modes"""
    TAG = "tag"  # Keep PII content between tags: [PII:type]
    REDACT = "redact"  # Replace PII with just category: [PII:type]
    REPLACE = "replace"  # Replace PII with fake data (requires faker extra)


class PIIType(Enum):
    """Enum for different PII types supported by Sentinel"""
    AGE = "age"
    CREDIT_CARD_INFO = "credit_card_info"
    NATIONALITY = "nationality"
    DATE = "date"
    DATE_OF_BIRTH = "date_of_birth"
    DOMAIN_NAME = "domain_name"
    EMAIL_ADDRESS = "email_address"
    DEMOGRAPHIC_GROUP = "demographic_group"
    GENDER = "gender"
    PERSONAL_ID = "personal_id"
    OTHER_ID = "other_id"
    BANKING_NUMBER = "banking_number"
    MEDICAL_CONDITION = "medical_condition"
    ORGANIZATION_NAME = "organization_name"
    PERSON_NAME = "person_name"
    PHONE_NUMBER = "phone_number"
    STREET_ADDRESS = "street_address"
    PASSWORD = "password"
    SECURE_CREDENTIAL = "secure_credential"
    RELIGIOUS_AFFILIATION = "religious_affiliation"


class SentinelPIIRedactor:
    """
    Sentinel PII Redactor using fine-tuned Granite model from HuggingFace.

    This class provides PII detection and redaction capabilities using the
    cernis-intelligence/sentinel model hosted on HuggingFace.

    Examples:
        >>> from sentinel_pii import SentinelPIIRedactor, PIIHandlingMode
        >>>
        >>> # Initialize the redactor
        >>> redactor = SentinelPIIRedactor()
        >>>
        >>> # Detect PII in text
        >>> text = "My name is John Smith and my email is john@email.com"
        >>> result = redactor.detect_pii([text])
        >>> print(result[0])
        'My name is [PERSON_NAME] and my email is [EMAIL_ADDRESS]'
    """

    # Default PII categories to look for
    DEFAULT_PII_CATEGORIES = """PII Categories to identify:
- PERSON_NAME: Names of people
- EMAIL_ADDRESS: Email addresses
- PHONE_NUMBER: Phone numbers
- STREET_ADDRESS: Physical addresses
- DATE_OF_BIRTH: Birth dates
- DATE: Any dates
- PERSONAL_ID: SSN, passport, driver's license, national ID, etc.
- CREDIT_CARD_INFO: Credit card numbers
- PASSWORD: Passwords or credentials
- USERNAME: Usernames
- MEDICAL_CONDITION: Diagnoses, treatments, health information
- ORGANIZATION_NAME: Company/organization names
- AGE: Person's age
- GENDER: Gender identifiers
- NATIONALITY: Country references
- BANKING_NUMBER: Bank account numbers
- SECURE_CREDENTIAL: API keys, tokens, private keys
- RELIGIOUS_AFFILIATION: Religious identifiers
- DEMOGRAPHIC_GROUP: Race, ethnicity identifiers"""

    def __init__(self, pii_categories: Optional[str] = None):
        """
        Initialize the Sentinel PII Redactor.

        The model is loaded from HuggingFace (cernis-intelligence/sentinel) on first use.

        Args:
            pii_categories: Optional custom PII categories string (uses defaults if None)
        """
        self.model = None
        self.tokenizer = None
        self.pii_categories = pii_categories or self.DEFAULT_PII_CATEGORIES

    def _initialize_model(self):
        """Load the Sentinel model from HuggingFace on first use."""
        if self.model is None:
            print("Loading Sentinel model from HuggingFace...")

            # Determine device
            device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

            # Load model without device_map to avoid meta device issues
            self.model = AutoModelForCausalLM.from_pretrained(
                "cernis-intelligence/sentinel",
                dtype=torch.float16 if device != "cpu" else torch.float32,
                low_cpu_mem_usage=True
            )

            # Move to device
            self.model = self.model.to(device)

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                "cernis-intelligence/sentinel"
            )

            print("✓ Model loaded successfully")

    def _model_call(self, text: str) -> str:
        """
        Process text through the model to identify PII entities.

        Args:
            text: The text to process

        Returns:
            The processed text with PII tags
        """
        self._initialize_model()

        messages = [
            {
                "role": "user",
                "content": f"{self.pii_categories}\n\nIdentify and tag all PII in the following text using the format [CATEGORY]:\n\n{text}"
            }
        ]

        # Apply chat template
        encoded_input = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )

        input_ids = encoded_input["input_ids"].to(self.model.device)
        attention_mask = encoded_input["attention_mask"].to(self.model.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=1024,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=False,  # Deterministic for PII detection
                temperature=0.7,
                top_p=0.9,
            )

        # Decode only the generated part
        input_length = encoded_input["input_ids"].size(1)
        generated_ids = outputs[0][input_length:]
        output_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        return output_text

    def detect_pii(
        self,
        documents: List[str],
        mode: PIIHandlingMode = PIIHandlingMode.TAG,
        locale: str = "en_US",
        show_progress: bool = True,
    ) -> List[str]:
        """
        Detect and handle PII in a list of documents.

        Args:
            documents: List of text documents to process
            mode: How to handle identified PII (TAG, REDACT, or REPLACE)
            locale: Locale for generating fake data (only used if mode=REPLACE)
            show_progress: Whether to show progress bar

        Returns:
            List of documents with PII handled according to the specified mode

        Raises:
            ImportError: If mode=REPLACE but faker is not installed
        """
        if mode == PIIHandlingMode.REPLACE:
            try:
                from .faker_utils import FakePIIGenerator
            except ImportError:
                raise ImportError(
                    "The 'faker' package is required for REPLACE mode. "
                    "Install it with: pip install 'sentinel-pii-sdk[faker]'"
                )

        processed_documents = []
        iterator = tqdm(documents, desc="Processing documents") if show_progress else documents

        for doc in iterator:
            # Get model output with PII tags
            tagged_output = self._model_call(doc)

            # Handle different modes
            if mode == PIIHandlingMode.TAG:
                # Keep as-is with tags
                processed_doc = tagged_output

            elif mode == PIIHandlingMode.REDACT:
                # The model already outputs in tagged format like [PERSON_NAME]
                # This is effectively the same as TAG mode
                processed_doc = tagged_output

            elif mode == PIIHandlingMode.REPLACE:
                # Replace with fake data
                from .faker_utils import FakePIIGenerator
                fake_generator = FakePIIGenerator(locale=locale)

                def replace_with_fake(match):
                    pii_type = match.group(1).lower()
                    # Extract original text if available (between tags)
                    return fake_generator.get_fake_value(pii_type, "")

                # Replace [CATEGORY] tags with fake data
                processed_doc = re.sub(
                    r'\[([A-Z_]+)\]',
                    replace_with_fake,
                    tagged_output
                )

            processed_documents.append(processed_doc)

        return processed_documents

    def redact_text(
        self,
        text: str,
        mode: PIIHandlingMode = PIIHandlingMode.TAG,
        locale: str = "en_US",
    ) -> str:
        """
        Detect and handle PII in a single text.

        Args:
            text: Text to process
            mode: How to handle identified PII (TAG, REDACT, or REPLACE)
            locale: Locale for generating fake data (only used if mode=REPLACE)

        Returns:
            Text with PII handled according to the specified mode
        """
        return self.detect_pii([text], mode=mode, locale=locale, show_progress=False)[0]
