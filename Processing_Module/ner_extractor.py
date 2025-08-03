"""
ner_extractor.py

Purpose:
    This module provides a dedicated service for performing Named Entity
    Recognition (NER) on text content. It utilizes the spaCy NLP library to
    identify and categorize entities such as people, organizations, dates,
    and locations from the meeting transcript. This structured information is
    a critical input for context preparation and final summary generation.

Key Features:
    - Wraps the spaCy library for a clean, task-focused interface.
    - Handles the loading of a specified pre-trained spaCy model.
    - Provides graceful error handling if a required model is not installed.
    - Extracts and categorizes entities, with deduplication and sorting.
    - Filters out trivial or noisy entities for cleaner output.
"""

import spacy
from collections import defaultdict
from typing import List, Dict, Any, Set

class NamedEntityExtractor:
    """
    Extracts structured named entities from text using a spaCy model.
    """

    # Define the spaCy entity labels we are interested in capturing.
    _TARGET_ENTITY_LABELS = {
        'PERSON', 'ORG', 'DATE', 'GPE', 'LOC', 'MONEY', 'PRODUCT', 'EVENT'
    }

    # Map the raw spaCy labels to more descriptive, user-friendly keys.
    _LABEL_CATEGORY_MAP = {
        'PERSON': 'people',
        'ORG': 'organizations',
        'DATE': 'dates_mentioned',
        'GPE': 'geopolitical_entities', # e.g., countries, cities
        'LOC': 'locations',
        'MONEY': 'monetary_values',
        'PRODUCT': 'products_mentioned',
        'EVENT': 'events_mentioned'
    }

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initializes the extractor and loads the specified spaCy NLP model.

        Args:
            model_name: The name of the pre-trained spaCy model to use.
                        (e.g., "en_core_web_sm", "en_core_web_trf")
        """
        self.nlp = self._load_spacy_model(model_name)
        self.model_name = model_name

    def _load_spacy_model(self, model: str):
        """
        Safely loads the spaCy model, providing clear instructions on failure.
        """
        try:
            print(f"...Loading NER model: {model}...")
            return spacy.load(model)
        except OSError:
            print(f"\n  SpaCy Model Not Found: '{model}'")
            print("   This model is required for Named Entity Recognition.")
            print(f"   To install it, run the following command in your terminal:")
            print(f"   python -m spacy download {model}")
            return None

    def extract_from_corpus(self, text: str) -> Dict[str, List[str]]:
        """
        Processes a body of text to identify and categorize named entities.

        Args:
            text: The input string (corpus) to analyze.

        Returns:
            A dictionary where keys are entity categories (e.g., 'people') and
            values are sorted lists of unique entities found in that category.
        """
        if not self.nlp:
            print(f"  NER model '{self.model_name}' not loaded. Skipping entity extraction.")
            return {cat: [] for cat in self._LABEL_CATEGORY_MAP.values()}

        doc = self.nlp(text)
        
        # Use a dictionary of sets for automatic deduplication of entities.
        extracted_entities: Dict[str, Set[str]] = defaultdict(set)

        for entity in doc.ents:
            if entity.label_ in self._TARGET_ENTITY_LABELS:
                # Sanitize the entity text and filter out noise
                entity_text = entity.text.strip()
                if self._is_entity_valid(entity_text):
                    category = self._LABEL_CATEGORY_MAP[entity.label_]
                    extracted_entities[category].add(entity_text)
        
        # Convert sets to sorted lists for consistent and clean output.
        return {
            category: sorted(list(entities))
            for category, entities in extracted_entities.items()
        }

    def _is_entity_valid(self, entity_text: str) -> bool:
        """
        A simple filter to exclude trivial or likely incorrect entities.
        """
        # Exclude very short entities or those that are just numbers/punctuation
        if len(entity_text) < 3:
            return False
        if entity_text.isnumeric():
            return False
        return True
