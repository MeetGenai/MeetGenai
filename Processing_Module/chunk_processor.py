"""
chunk_processor.py

Purpose:
    This module defines the processor responsible for the deep analysis of a
    single, isolated chunk of a transcript. It orchestrates an enhanced sequence
    of analytical steps—including sanitization, sentiment analysis, participant
    assessment, and context preparation—to transform raw segments into a rich,
    multi-modal data object.

Key Features:
    - Acts as a sophisticated sub-pipeline for a single transcript window.
    - Integrates the new SentimentAnalyzer to add emotional context.
    - Produces a comprehensive data packet for each chunk, including the
      final context and an advanced, engineered LLM prompt.
    - Includes functionality to save its detailed output to a JSON file.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import components for type hinting and dependency injection
from dialogue_sanitizer import DialogueSanitizer
from sentiment_analyzer import SentimentAnalyzer
from participant_analyzer import ParticipantAnalyzer
from llm_payload_creator import LLMPayloadCreator

class TranscriptChunkProcessor:
    """
    Orchestrates the end-to-end multi-modal analysis of a single transcript chunk.
    """

    def __init__(self,
                 sanitizer: DialogueSanitizer,
                 sentiment_analyzer: SentimentAnalyzer,
                 participant_analyzer: ParticipantAnalyzer,
                 payload_creator: LLMPayloadCreator):
        """
        Initializes the processor with its required analytical components.

        Args:
            sanitizer: An instance of the DialogueSanitizer.
            sentiment_analyzer: An instance of the SentimentAnalyzer.
            participant_analyzer: An instance of the ParticipantAnalyzer.
            payload_creator: An instance of the LLMPayloadCreator.
        """
        self.sanitizer = sanitizer
        self.sentiment_analyzer = sentiment_analyzer
        self.participant_analyzer = participant_analyzer
        self.payload_creator = payload_creator

    def process_chunk(self,
                      transcript_segments: List[Dict[str, Any]],
                      meeting_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Runs the full, enhanced processing pipeline on a given list of segments.

        Args:
            transcript_segments: A list of raw segment dictionaries from a transcript chunk.
            meeting_date: An optional string for the meeting date (YYYY-MM-DD).

        Returns:
            A dictionary containing the final processed context, the LLM prompt,
            and associated metadata for the chunk, or None if the chunk is empty.
        """
        # Step 1: Sanitize text content in all segments.
        cleaned_segments = self.sanitizer.sanitize_segments(transcript_segments)
        if not cleaned_segments:
            print("   |> Warning: Chunk contained no meaningful content after sanitization. Skipping.")
            return None

        # Step 2: NEW - Analyze and attach sentiment to each segment.
        sentiment_enriched_segments = self.sentiment_analyzer.analyze_segments(cleaned_segments)

        # Step 3: Analyze participant contributions to get roles and stats.
        participant_roles, participant_stats = self.participant_analyzer.assess_contributions(sentiment_enriched_segments)

        # Apply the generated role mapping for clearer output.
        final_segments = self._apply_role_mapping(sentiment_enriched_segments, participant_roles)

        # Step 4: Build the comprehensive context and generate the advanced LLM prompt.
        payload = self.payload_creator.build_context_and_prompt(
            segments=final_segments,
            participant_stats=participant_stats,
            participant_roles=participant_roles
        )

        # Step 5: Assemble the final output package for this chunk.
        return {
            'llm_prompt': payload.get('llm_prompt'),
            'analysis_context': payload.get('final_context'),
            'processed_transcript_chunk': final_segments,
            'processing_metadata': {
                'source_segment_count': len(transcript_segments),
                'processed_segment_count': len(final_segments),
                'participant_role_map': participant_roles,
                'meeting_date': meeting_date or datetime.now().strftime("%Y-%m-%d"),
                'processing_timestamp_utc': datetime.utcnow().isoformat()
            }
        }

    def _apply_role_mapping(self,
                            segments: List[Dict[str, Any]],
                            role_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Applies the generated speaker role mapping to a list of segments."""
        if not role_map:
            return segments
        
        return [
            {**s, 'speaker': role_map.get(s.get('speaker', 'Unknown'), 'Unknown')}
            for s in segments
        ]

    def save_chunk_output(self, processed_data: Dict[str, Any], output_path: Path) -> bool:
        """
        Saves the processed data for a single chunk to a structured JSON file.

        Args:
            processed_data: The output dictionary from the process_chunk method.
            output_path: The file path where the JSON output will be saved.

        Returns:
            True if saving was successful, False otherwise.
        """
        if not processed_data:
            return False
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open('w', encoding='utf-8') as f:
                # Exclude the raw prompt from the file to save space
                data_to_save = {
                    key: value for key, value in processed_data.items()
                    if key != 'llm_prompt'
                }
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError) as e:
            print(f"   |>   Error saving chunk data to {output_path.name}: {e}")
            return False
