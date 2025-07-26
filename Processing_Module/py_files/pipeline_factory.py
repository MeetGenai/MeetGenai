"""
Factory for creating the transcript processing pipeline.

This module centralizes the instantiation and wiring of all pipeline components,
promoting Inversion of Control and loose coupling.
"""

from pipeline_config import PIPELINE_COMPONENTS

def create_transcript_aggregator():
    """Builds and returns a TranscriptAggregator instance."""
    print("...Assembling Stage 1: Transcript Aggregator...")
    aggregator_class = PIPELINE_COMPONENTS["transcript_aggregator"]
    print(" Aggregator assembly complete.")
    return aggregator_class()

def create_windowed_processor(window_size: int, output_dir: str, base_filename: str):
    """
    Builds and returns a fully configured WindowedTranscriptProcessor.
    """
    print("\n...Assembling Stage 2: Windowed Analysis Pipeline...")

    # --- Instantiate individual analysis components ---
    text_cleaner = PIPELINE_COMPONENTS["text_cleaner"]()
    speaker_analyzer = PIPELINE_COMPONENTS["speaker_analyzer"]()
    temporal_segmenter = PIPELINE_COMPONENTS["temporal_segmenter"]()
    entity_extractor = PIPELINE_COMPONENTS["entity_extractor"]()
    action_detector = PIPELINE_COMPONENTS["action_item_detector"]()
    topic_analyzer = PIPELINE_COMPONENTS["topic_analyzer"]()

    # --- Wire up dependencies for composite components ---
    llm_context_preparer = PIPELINE_COMPONENTS["llm_context_preparer"](
        entity_extractor=entity_extractor,
        action_detector=action_detector,
        topic_analyzer=topic_analyzer
    )

    meeting_processor = PIPELINE_COMPONENTS["meeting_transcript_processor"](
        text_cleaner=text_cleaner,
        speaker_analyzer=speaker_analyzer,
        temporal_segmenter=temporal_segmenter,
        context_preparer=llm_context_preparer
    )

    windowed_processor = PIPELINE_COMPONENTS["windowed_transcript_processor"](
        base_processor=meeting_processor,
        window_size=window_size,
        output_dir=output_dir,
        base_filename=base_filename
    )

    print(" Windowed analysis pipeline assembly complete.")
    return windowed_processor
