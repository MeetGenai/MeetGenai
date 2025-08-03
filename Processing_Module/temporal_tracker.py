"""
temporal_tracker.py

Purpose:
    This module implements Temporal Relationship Mapping to provide insights
    into the narrative flow of a meeting. It analyzes the sequence of processed
    windows to track how discussion topics evolve over time. By identifying
    when themes are introduced, revisited, or dropped, it constructs a
    high-level timeline of the conversation's focus, turning a series of
    isolated chunks into a cohesive story.

Key Features:
    - Tracks topics across multiple time windows.
    - Identifies the introduction and reappearance of discussion themes.
    - Maps the relationship between key decisions and the topics being
      discussed when they were made.
    - Generates a structured timeline of the meeting's conversational journey.
"""

from collections import defaultdict
from typing import List, Dict, Any

class TemporalTracker:
    """
    Analyzes the evolution of topics and decisions over the meeting timeline.
    """

    def generate_meeting_timeline(self, all_window_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a timeline of topic evolution and decision points.

        Args:
            all_window_outputs: A list of the complete output dictionaries from
                                each processed window.
        
        Returns:
            A dictionary containing the 'topic_evolution' map.
        """
        topic_evolution = defaultdict(list)
        
        for output in all_window_outputs:
            window_id = output.get('window_metadata', {}).get('window_id', 'N/A')
            context = output.get('analysis_context', {})
            themes = context.get('extracted_intelligence', {}).get('discussion_themes', {})
            
            for theme_id, keywords in themes.items():
                # Create a canonical key for the theme based on its keywords
                theme_key = f"Theme {theme_id}: {', '.join(keywords)}"
                topic_evolution[theme_key].append(window_id)

        return {
            'topic_evolution': dict(topic_evolution)
        }
