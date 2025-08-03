"""
dialogue_sanitizer.py

Purpose:
    This module provides a robust utility for cleaning and normalizing raw
    conversational text from transcripts. Its primary goal is to prepare the
    text for more advanced Natural Language Processing (NLP) tasks by removing
    noise such as filler words, repetitions, and encoding artifacts.

Key Features:
    - Fixes common text encoding issues and artifacts using the `ftfy` library.
    - Removes a customizable list of conversational filler words (e.g., "um", "like").
    - Collapses repeated words (e.g., "I I think" becomes "I think").
    - Normalizes whitespace to ensure consistent formatting.
    - Processes text segment-by-segment, filtering out segments that become
      empty after sanitization.
"""

import re
from typing import List, Dict, Any, Set
from ftfy import fix_text

class DialogueSanitizer:
    """
    A text processing engine designed to clean and normalize conversational dialogue.
    """

    # A comprehensive set of common English filler words and discourse markers.
    # Using a set provides O(1) average time complexity for lookups.
    DEFAULT_FILLER_WORDS: Set[str] = {
        'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean', 'actually',
        'basically', 'literally', 'obviously', 'well', 'so', 'right',
        'okay', 'ok', 'yeah', 'yes', 'hmm', 'huh', 'gotcha'
    }

    def __init__(self, custom_fillers: Set[str] = None):
        """
        Initializes the DialogueSanitizer, pre-compiling regex patterns for efficiency.

        Args:
            custom_fillers: An optional set of strings to add to the default
                            list of filler words to be removed.
        """
        all_fillers = self.DEFAULT_FILLER_WORDS.union(custom_fillers or set())

        # This pattern finds filler words as whole words and consumes any trailing comma/space.
        self.filler_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(word) for word in all_fillers) + r')\b[,\s]*',
            re.IGNORECASE
        )
        # This pattern finds sequences of a repeated word (e.g., "the the") and captures the first.
        self.repetition_pattern = re.compile(r'\b(\w+)(\s+\1\b)+', re.IGNORECASE)
        # This pattern finds and collapses two or more whitespace characters into a single space.
        self.whitespace_pattern = re.compile(r'\s{2,}')

    def sanitize_utterance(self, utterance: str) -> str:
        """
        Applies a sequence of cleaning operations to a single text string.

        Args:
            utterance: The raw text string to be sanitized.

        Returns:
            A cleaned and normalized version of the input string.
        """
        if not isinstance(utterance, str) or not utterance.strip():
            return ""

        # Step 1: Fix potential encoding errors and mojibake (e.g., "â€™" -> "'").
        text = fix_text(utterance)

        # Step 2: Remove conversational filler words.
        text = self.filler_pattern.sub('', text)

        # Step 3: Collapse word repetitions to a single instance.
        # The replacement `r'\1'` refers to the first captured group (the word itself).
        text = self.repetition_pattern.sub(r'\1', text)

        # Step 4: Normalize all whitespace to single spaces and trim ends.
        text = self.whitespace_pattern.sub(' ', text).strip()

        return text

    def sanitize_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies the sanitization process to the 'text' field of each segment.

        This method iterates through a list of transcript segments, cleans the
        text of each one, and filters out any segments that become empty as a
        result. This ensures that only segments with meaningful content are
        passed to subsequent pipeline stages.

        Args:
            segments: A list of transcript segment dictionaries.

        Returns:
            A new list containing only the cleaned, non-empty segments.
        """
        if not isinstance(segments, list):
            print("  Warning: `sanitize_segments` received non-list input. Returning empty list.")
            return []

        sanitized_segments = []
        for segment in segments:
            # Create a copy to maintain immutability of the original data
            processed_segment = segment.copy()
            original_text = processed_segment.get('text', '')

            cleaned_text = self.sanitize_utterance(original_text)
            processed_segment['text'] = cleaned_text

            # Only retain segments that still have content after cleaning
            if cleaned_text:
                sanitized_segments.append(processed_segment)

        return sanitized_segments
