"""
Faker utilities for generating realistic fake PII data
"""

from typing import Optional


class FakePIIGenerator:
    """
    Generator for creating realistic fake PII data.

    This class uses the Faker library to generate contextually appropriate
    fake data for different PII categories.
    """

    def __init__(self, locale: str = "en_US"):
        """
        Initialize the fake PII generator.

        Args:
            locale: Locale for generating fake data (e.g., 'en_US', 'fr_FR')
        """
        try:
            from faker import Faker
        except ImportError:
            raise ImportError(
                "The 'faker' package is required for generating fake PII. "
                "Install it with: pip install 'sentinel-pii-sdk[faker]'"
            )

        self.fake = Faker(locale=locale)
        self.locale = locale

    def get_fake_value(self, pii_type: str, original_text: Optional[str] = None) -> str:
        """
        Generate a fake value for a given PII type.

        Args:
            pii_type: Type of PII (e.g., 'person_name', 'email_address')
            original_text: Original PII text (optional, used for context)

        Returns:
            Fake PII value appropriate for the type
        """
        pii_type = pii_type.lower()

        # Map PII types to Faker methods
        mapping = {
            'person_name': lambda: self.fake.name(),
            'email_address': lambda: self.fake.email(),
            'phone_number': lambda: self.fake.phone_number(),
            'street_address': lambda: self.fake.address().replace('\n', ', '),
            'date_of_birth': lambda: self.fake.date_of_birth().strftime('%Y-%m-%d'),
            'date': lambda: self.fake.date(),
            'credit_card_info': lambda: self.fake.credit_card_number(),
            'personal_id': lambda: str(self.fake.random_number(digits=9)),
            'organization_name': lambda: self.fake.company(),
            'password': lambda: self.fake.password(),
            'age': lambda: str(self.fake.random_int(min=18, max=90)),
            'gender': lambda: self.fake.random_element(['male', 'female', 'non-binary']),
            'nationality': lambda: self.fake.country(),
            'domain_name': lambda: self.fake.domain_name(),
            'banking_number': lambda: self.fake.iban(),
            'username': lambda: self.fake.user_name(),
            'city': lambda: self.fake.city(),
            'state': lambda: self.fake.state(),
            'postcode': lambda: self.fake.postcode(),
            'country': lambda: self.fake.country(),
            'medical_condition': lambda: self.fake.random_element([
                'hypertension', 'diabetes', 'asthma', 'arthritis'
            ]),
            'secure_credential': lambda: self.fake.sha256(),
            'demographic_group': lambda: '[DEMOGRAPHIC_GROUP]',
            'religious_affiliation': lambda: '[RELIGIOUS_AFFILIATION]',
            'other_id': lambda: self.fake.uuid4(),
        }

        # Get the generator function
        generator = mapping.get(pii_type)

        if generator:
            return generator()
        else:
            # Default fallback for unknown types
            return f'[{pii_type.upper()}]'
