import hashlib
import re
from typing import Dict
import torch
from transformers import pipeline
from .Anonymizer import Anonymizer

ANONYMIZED_NAMES = [
    "Max Mustermann",
    "Maria Musterfrau",
    "Erika Mustermann",
    "John Doe",
]

ANONYMIZED_CITIES = [
    "Musterstadt",
    "Beispielstadt",
    "Demostadt"
]

ANONYMIZED_STREETS = [
    "Musterstraße 1",
    "Beispielweg 2",
    "Demoweg 3"
]

ASSISTANT_NAME = "RunYourDinner Team"
SUPPORT_PERSON_NAMES_LOWERCASE = ["clemens stich", "clemens"]


MULTILINGUAL_NER_MODEL = "Babelscape/wikineural-multilingual-ner"
# MULTILINGUAL_NER_MODEL = "stefan-it/gelectra-large-germanquad-ner"

class AnonymizerBabelfish(Anonymizer):

    def __init__(self, skip_anonymization: bool = False):
        self.skip_anonymization = skip_anonymization
        self._ner_pipeline = None
        # Mapping dictionaries for consistent anonymization
        self._name_mapping: Dict[str, str] = {}
        self._city_mapping: Dict[str, str] = {}
        self._street_mapping: Dict[str, str] = {}

    @property
    def ner_pipeline(self):
        if self._ner_pipeline is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._ner_pipeline = pipeline(
                "ner",
                model=MULTILINGUAL_NER_MODEL,
                aggregation_strategy="simple",  # Aggregate subword tokens into full entities
                device=device
            )
        return self._ner_pipeline


    def _get_deterministic_replacement(self, entity: str, entity_type: str) -> str:
        """
        Get a consistent anonymized replacement for an entity using hash-based mapping.
        Same entity always maps to the same replacement.
        
        Args:
            entity: The original entity text
            entity_type: Type of entity (PER, LOC, etc.)
            
        Returns:
            Anonymized replacement string
        """
        # Normalize entity (lowercase, strip whitespace)
        normalized = entity.strip().lower()
        
        # Select appropriate mapping and replacement pool
        if entity_type == "PER":
            mapping = self._name_mapping
            pool = ANONYMIZED_NAMES
        elif entity_type == "LOC":
            # Check if it looks like a street address (contains numbers)
            if any(char.isdigit() for char in entity):
                mapping = self._street_mapping
                pool = ANONYMIZED_STREETS
            else:
                mapping = self._city_mapping
                pool = ANONYMIZED_CITIES
        else:
            # For other entity types (ORG, MISC), use city pool
            mapping = self._city_mapping
            pool = ANONYMIZED_CITIES
        
        # Check if we already have a mapping
        if normalized in mapping:
            return mapping[normalized]
        
        # Create deterministic hash-based index
        hash_value = int(hashlib.md5(normalized.encode()).hexdigest(), 16)
        index = hash_value % len(pool)
        replacement = pool[index]
        
        # Store mapping for consistency
        mapping[normalized] = replacement
        
        return replacement

    def anonymize_personal_data(self, text: str, language: str) -> str:
        if self.skip_anonymization:
            return text
        
        if not text or not text.strip():
            return text
        

        anonymized_text = self._replace_support_person_name(text)
        
        # Get NER predictions
        entities = self.ner_pipeline(anonymized_text)
        
        # Sort entities by start position in reverse order to replace from end to start
        # This preserves indices when making replacements
        entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        # Replace entities with anonymized versions
        for entity in entities_sorted:
            entity_type = entity['entity_group']
            entity_text = entity['word']
            start = entity['start']
            end = entity['end']
            
            # Only anonymize PER (persons) and LOC (locations)
            if entity_type in ['PER', 'LOC']:
                replacement = self._get_deterministic_replacement(entity_text, entity_type)
                anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
        
        # Replace any occurrence of assistant name if present
        # This is a safety measure to ensure the assistant name is never anonymized
        anonymized_text = anonymized_text.replace(ASSISTANT_NAME, ASSISTANT_NAME)
        
        return anonymized_text
    

    def _replace_support_person_name(self, text: str) -> str:
        """
        Replace occurrences of support person names with the assistant name.
        Checks for case-insensitive matches, preserving the rest of the text's capitalization.
        
        Args:
            text: The input text
            
        Returns:
            Text with support person names replaced
        """
        result = text
        for name in SUPPORT_PERSON_NAMES_LOWERCASE:
            # Use re.escape to safely handle special characters in names
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            result = pattern.sub(ASSISTANT_NAME, result)
        return result