"""
participant_analyzer.py

Purpose:
    This module is dedicated to analyzing the conversational dynamics of a meeting.
    It quantifies the contribution of each participant by calculating metrics such
    as total talk time, word count, and overall engagement percentage. Based on
    these metrics, it assigns descriptive roles (e.g., "Primary Contributor")
    to each unique speaker, providing valuable insight into the meeting's flow.

Key Features:
    - Calculates detailed statistics for each speaker.
    - Implements a configurable threshold to identify the most active speaker.
    - Assigns clear, role-based labels to anonymous speaker IDs.
    - Produces a speaker map and detailed statistics for downstream use.
"""

from collections import defaultdict
from typing import List, Dict, Any, Tuple

class ParticipantAnalyzer:
    """
    Calculates speaker statistics and maps speaker IDs to descriptive roles.
    """

    def __init__(self, primary_threshold: float = 0.40, lead_margin: float = 0.10):
        """
        Initializes the analyzer with configurable thresholds.

        Args:
            primary_threshold: The percentage of total talk time a speaker must
                               exceed to be considered the primary contributor.
            lead_margin: The minimum percentage lead the top speaker must have
                         over the second to be assigned the primary role. This
                         avoids assigning a primary speaker in balanced discussions.
        """
        if not 0 < primary_threshold < 1:
            raise ValueError("primary_threshold must be between 0 and 1.")
        if not 0 < lead_margin < 1:
            raise ValueError("lead_margin must be between 0 and 1.")

        self.primary_threshold = primary_threshold
        self.lead_margin = lead_margin

    def assess_contributions(self, segments: List[Dict[str, Any]]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Analyzes speaker contributions to generate role mappings and statistics.

        This is the main public method that orchestrates the two-step process of
        first calculating metrics and then assigning roles based on them.

        Args:
            segments: A list of cleaned transcript segment dictionaries.

        Returns:
            A tuple containing:
            - A dictionary mapping original speaker IDs to new role-based labels.
            - A dictionary of detailed statistics for each original speaker.
        """
        if not segments:
            return {}, {}

        statistics = self._compute_metrics(segments)
        role_map = self._assign_roles(statistics)

        return role_map, statistics

    def _compute_metrics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates talk duration, word count, and other metrics for each speaker.
        """
        speaker_metrics = defaultdict(lambda: {'talk_duration': 0.0, 'word_count': 0, 'utterance_count': 0})
        total_duration = 0.0

        for segment in segments:
            speaker_id = segment.get('speaker', 'Unknown')
            duration = max(0.0, segment.get('end', 0.0) - segment.get('start', 0.0))
            words = len(segment.get('text', '').split())

            speaker_metrics[speaker_id]['talk_duration'] += duration
            speaker_metrics[speaker_id]['word_count'] += words
            speaker_metrics[speaker_id]['utterance_count'] += 1
            total_duration += duration

        # Post-process to add percentages and averages
        if total_duration > 0:
            for speaker, data in speaker_metrics.items():
                contribution_pct = (data['talk_duration'] / total_duration) * 100
                data['contribution_percentage'] = round(contribution_pct, 2)

        return dict(speaker_metrics)

    def _assign_roles(self, statistics: Dict[str, Any]) -> Dict[str, str]:
        """
        Creates descriptive labels for speakers based on their calculated metrics.
        """
        if not statistics:
            return {}

        # Sort speakers by talk duration in descending order
        sorted_speakers = sorted(
            statistics.items(),
            key=lambda item: item[1].get('talk_duration', 0),
            reverse=True
        )

        role_map = {}
        participant_num = 1
        is_primary_assigned = False

        # Check if a primary speaker should be assigned
        if len(sorted_speakers) >= 1:
            top_speaker_id, top_speaker_stats = sorted_speakers[0]
            top_contribution = top_speaker_stats.get('contribution_percentage', 0)

            # Condition 1: Must exceed the primary threshold
            exceeds_threshold = top_contribution >= (self.primary_threshold * 100)

            # Condition 2: Must have a significant lead over the next speaker
            has_clear_lead = True
            if len(sorted_speakers) > 1:
                second_speaker_stats = sorted_speakers[1][1]
                second_contribution = second_speaker_stats.get('contribution_percentage', 0)
                has_clear_lead = (top_contribution - second_contribution) >= (self.lead_margin * 100)

            if exceeds_threshold and has_clear_lead:
                role_map[top_speaker_id] = "Primary Contributor"
                is_primary_assigned = True

        # Assign roles to all other speakers
        for speaker_id, _ in sorted_speakers:
            if speaker_id in role_map:
                continue # Already assigned a role (e.g., Primary)

            if speaker_id.upper() == 'UNKNOWN':
                role_map[speaker_id] = "Unidentified Speaker"
            else:
                role_map[speaker_id] = f"Participant {participant_num}"
                participant_num += 1

        return role_map
