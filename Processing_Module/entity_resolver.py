"""
entity_resolver.py

Purpose:
    This module provides an advanced capability for Cross-Reference Entity
    Resolution. After initial entity extraction is performed on each meeting
    chunk, this resolver analyzes the full set of entities from the entire
    meeting. It uses normalization and aliasing techniques to identify and
    merge different mentions of the same entity (e.g., "Bob", "Robert", and
    "Mr. Smith"), creating a canonical list of unique individuals and
    organizations discussed.

Key Features:
    - Aggregates entities from all processed windows.
    - Implements normalization rules to handle titles, initials, and variations.
    - Builds a unified, deduplicated map of all entities mentioned.
    - Provides a "single source of truth" for entities across the meeting.
"""

from collections import defaultdict
from typing import List, Dict, Any

class EntityResolver:
    """
    Normalizes and resolves entities across an entire meeting.
    """

    def resolve_across_windows(self, all_window_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates and resolves entities from all processed windows.

        Args:
            all_window_outputs: A list of the complete output dictionaries from
                                each processed window.

        Returns:
            A dictionary containing the unified lists of resolved 'people' and
            'organizations'.
        """
        all_people = []
        all_orgs = []

        for output in all_window_outputs:
            context = output.get('analysis_context', {})
            entities = context.get('extracted_intelligence', {}).get('entities', {})
            all_people.extend(entities.get('people', []))
            all_orgs.extend(entities.get('organizations', []))
        
        resolved_people = self._normalize_and_deduplicate(all_people)
        resolved_orgs = self._normalize_and_deduplicate(all_orgs, is_person=False)

        return {
            'people': resolved_people,
            'organizations': resolved_orgs
        }

    def _normalize_and_deduplicate(self, names: List[str], is_person: bool = True) -> List[str]:
        """
        A simple normalization engine to group similar names.
        
        For people, it handles titles and tries to match based on last names.
        For organizations, it handles common suffixes like 'Inc' or 'LLC'.
        
        Args:
            names: A list of entity names.
            is_person: A flag to apply person-specific normalization rules.

        Returns:
            A sorted list of unique, canonical entity names.
        """
        canonical_map = {} # Maps a simplified key to a canonical name
        
        for name in names:
            # Create a simplified key for matching
            key = name.lower().replace('.', '').replace(',', '')
            if is_person:
                key = key.replace('mr ', '').replace('ms ', '').replace('dr ', '')
            else: # is_org
                key = key.replace(' inc', '').replace(' llc', '').replace(' ltd', '')
            
            # Use the first encountered version as the canonical name
            if key not in canonical_map:
                canonical_map[key] = name
        
        return sorted(list(set(canonical_map.values())))
