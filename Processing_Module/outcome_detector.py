"""
outcome_detector.py

Purpose:
    This module is engineered to identify and extract concrete outcomes from
    meeting transcripts. Using rule-based pattern matching with regular
    expressions, it scans dialogue for phrases that signify commitments (tasks)
    and resolutions (decisions). This provides a structured list of actionable
    items and key takeaways from the conversation.

Key Features:
    - Uses pre-compiled regex for efficient pattern matching.
    - Separately identifies tasks and decisions.
    - Attempts to extract associated metadata like assignees and deadlines.
    - Implements an intelligent deduplication mechanism to avoid redundant results.
"""

import re
from typing import List, Dict, Any, Optional, Set

class OutcomeDetector:
    """
    Analyzes transcript text to extract structured tasks and key decisions.
    """

    def __init__(self):
        """
        Initializes the detector and compiles regex patterns for high performance.
        """
        # Patterns targeting forward-looking statements, commitments, and responsibilities.
        self.task_patterns = [
            re.compile(r'\b(i will|we will|i\'ll|we\'ll|we need to|i need to|let\'s|should|must)\s+([^.?!]{15,200})\b', re.IGNORECASE),
            re.compile(r'\b(action item|next step|the plan is|task for)\s*[:\-is]*\s*([^.?!]{15,200})\b', re.IGNORECASE),
            re.compile(r'\b(who can|can someone|assign to|responsible for)\s+([^.?!]{15,200})\b', re.IGNORECASE)
        ]

        # Patterns targeting conclusive statements, agreements, and resolutions.
        self.decision_patterns = [
            re.compile(r'\b(we decided|we agreed|the decision is|it\'s settled)\s+(that\s*)?([^.?!]{15,200})\b', re.IGNORECASE),
            re.compile(r'\b(so we\'ll move forward with|let\'s go with|the consensus is)\s+([^.?!]{15,200})\b', re.IGNORECASE)
        ]

        # Patterns for extracting potential assignees (Proper Nouns).
        self.assignee_pattern = re.compile(r'\b(for|to|assign to|assigned to|cc)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b')

        # Patterns for detecting common business deadlines.
        self.deadline_pattern = re.compile(r'\b(by|before|due on|deadline is)\s+((?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|week|EOW|EOD|end of day|end of week))', re.IGNORECASE)

    def detect_outcomes(self, segments: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Scans all transcript segments to identify and extract tasks and decisions.

        Args:
            segments: A list of transcript segment dictionaries.

        Returns:
            A dictionary containing two keys, 'tasks' and 'decisions', each with a
            deduplicated list of the corresponding outcomes found.
        """
        tasks = []
        decisions = []

        for segment in segments:
            text = segment.get('text', '')
            if not text:
                continue

            # Detect Tasks
            for pattern in self.task_patterns:
                for match in pattern.finditer(text):
                    task_desc = match.group(2).strip(" ,.")
                    tasks.append({
                        'description': task_desc,
                        'assignee': self._find_assignee(task_desc, text) or "Unassigned",
                        'deadline': self._find_deadline(task_desc) or "Not Specified",
                        'speaker': segment.get('speaker', 'N/A'),
                        'timestamp': segment.get('start', 0.0),
                    })

            # Detect Decisions
            for pattern in self.decision_patterns:
                for match in pattern.finditer(text):
                    decisions.append({
                        'description': match.group(2).strip(" ,."),
                        'speaker': segment.get('speaker', 'N/A'),
                        'timestamp': segment.get('start', 0.0)
                    })

        return {
            'tasks': self._deduplicate(tasks, 'description'),
            'decisions': self._deduplicate(decisions, 'description')
        }

    def _find_assignee(self, outcome_text: str, context: str) -> Optional[str]:
        """Attempts to identify an assignee from the text."""
        # Check both the matched outcome text and the full segment for context
        full_context = f"{outcome_text} {context}"
        match = self.assignee_pattern.search(full_context)
        return match.group(2).strip() if match else None

    def _find_deadline(self, outcome_text: str) -> Optional[str]:
        """Attempts to identify a deadline within the text."""
        match = self.deadline_pattern.search(outcome_text)
        return match.group(2).strip() if match else None

    def _deduplicate(self, items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        """
        Removes duplicate entries based on the normalized content of a specified key.
        """
        seen_keys: Set[str] = set()
        unique_items = []
        for item in items:
            # Normalize the text for more robust deduplication
            # (lowercase, remove whitespace, take first 80 chars)
            normalized_key = "".join(item[key].lower().split())[:80]
            if normalized_key not in seen_keys:
                seen_keys.add(normalized_key)
                unique_items.append(item)
        return unique_items
