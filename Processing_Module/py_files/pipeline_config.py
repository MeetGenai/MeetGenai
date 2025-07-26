"""
Configuration file for the transcript processing pipeline.

This file defines the concrete classes to be used for each component
of the pipeline. By modifying this file, you can swap out components
without changing the core application logic.
"""

# --- New Pre-processing Component ---
from transcript_aggregator import TranscriptAggregator

# --- Existing Analysis Components ---
from text_cleaner import TextCleaner
from speaker_analyzer import SpeakerAnalyzer
from temporal_segmenter import TemporalSegmenter
from entity_extractor import EntityExtractor
from action_item_detector import ActionItemDetector
from topic_analyzer import TopicAnalyzer
from llm_context_preparer import LLMContextPreparer
from meeting_transcript_processor import MeetingTranscriptProcessor
from windowed_transcript_processor import WindowedTranscriptProcessor

PIPELINE_COMPONENTS = {
    # Stage 1: Aggregation
    "transcript_aggregator": TranscriptAggregator,

    # Stage 2: Core Analysis Components
    "text_cleaner": TextCleaner,
    "speaker_analyzer": SpeakerAnalyzer,
    "temporal_segmenter": TemporalSegmenter,
    "entity_extractor": EntityExtractor,
    "action_item_detector": ActionItemDetector,
    "topic_analyzer": TopicAnalyzer,

    # Stage 2: High-Level Processors
    "llm_context_preparer": LLMContextPreparer,
    "meeting_transcript_processor": MeetingTranscriptProcessor,
    "windowed_transcript_processor": WindowedTranscriptProcessor,
}
