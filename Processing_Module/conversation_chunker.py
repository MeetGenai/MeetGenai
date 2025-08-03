"""
conversation_chunker.py

Purpose:
    This module provides a mechanism to partition a continuous transcript into
    discrete, fixed-length time windows or "chunks." This is a critical
    preprocessing step for analyzing long meetings, as it allows the pipeline
    to process the conversation in manageable segments, preventing memory
    overload and enabling more focused analysis of specific time periods.

Key Features:
    - Uses the high-performance `pandas` library for efficient time-based filtering.
    - Creates non-overlapping windows of a configurable duration.
    - Aggregates text, speakers, and raw segments within each window.
    - Handles empty or invalid input gracefully.
"""

from typing import List, Dict, Any
import pandas as pd

class ConversationChunker:
    """
    Splits a list of transcript segments into discrete, non-overlapping time windows.
    """

    def __init__(self, window_duration_sec: int = 300):
        """
        Initializes the chunker with a specified window duration.

        Args:
            window_duration_sec: The desired length of each time window in seconds.
                                 Must be a positive integer.
        """
        if not isinstance(window_duration_sec, int) or window_duration_sec <= 0:
            raise ValueError("Window duration must be a positive integer of seconds.")
        self.window_duration = window_duration_sec

    def chunk_by_time(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Partitions the transcript segments into a series of time-based windows.

        Args:
            segments: A list of transcript segment dictionaries. Each segment must
                      contain 'start', 'end', 'text', and 'speaker' keys.

        Returns:
            A list of window dictionaries. Each dictionary represents a time chunk
            and contains metadata, aggregated text, and the original segments
            that fall within its boundaries. Returns an empty list if no
            valid segments are provided.
        """
        if not segments:
            return []

        try:
            # Using a DataFrame is highly efficient for this type of slicing
            df = pd.DataFrame(segments)
            required_cols = {'start', 'end', 'text', 'speaker'}
            if not required_cols.issubset(df.columns):
                 raise KeyError("Input segments are missing required keys.")
        except (ValueError, KeyError):
            print("  Error: Could not create a valid DataFrame from segments.")
            print("   Please ensure segments is a list of dicts with 'start', 'end', 'text', 'speaker'.")
            return []

        total_meeting_duration = df['end'].max()
        time_windows = []

        # Iterate through the meeting duration in steps of the window size
        for start_time in range(0, int(total_meeting_duration) + 1, self.window_duration):
            end_time = start_time + self.window_duration

            # Efficiently filter segments whose start time is within the current window
            window_df = df[(df['start'] >= start_time) & (df['start'] < end_time)]

            if not window_df.empty:
                aggregated_text = " ".join(window_df['text'].astype(str).tolist())

                time_windows.append({
                    'window_id': len(time_windows) + 1,
                    'start_seconds': start_time,
                    'end_seconds': end_time,
                    'duration': self.window_duration,
                    'aggregated_text': aggregated_text,
                    'participants': window_df['speaker'].unique().tolist(),
                    'segment_count': len(window_df),
                    'source_segments': window_df.to_dict('records')
                })

        return time_windows

    @staticmethod
    def get_total_duration(segments: List[Dict[str, Any]]) -> float:
        """
        Calculates the total duration of a meeting from its first to last segment.

        Args:
            segments: A list of transcript segment dictionaries.

        Returns:
            The total duration in seconds, or 0.0 if input is empty.
        """
        if not segments:
            return 0.0

        try:
            min_start = min(s.get('start', 0.0) for s in segments)
            max_end = max(s.get('end', 0.0) for s in segments)
            return max_end - min_start
        except (TypeError, ValueError):
            # Handle cases with malformed segment data
            return 0.0
