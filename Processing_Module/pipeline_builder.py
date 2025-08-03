"""
pipeline_builder.py

This module implements the Factory design pattern. It is responsible for
instantiating and wiring together all the necessary components to construct
the complete, ready-to-use transcript processing pipeline.
"""

from component_registry import COMPONENT_REGISTRY
from settings import PipelineSettings

def build_processing_pipeline(settings: PipelineSettings):
    """
    Builds and returns a fully configured WindowedTranscriptProcessor.

    This function follows the dependency injection principle, creating instances
    of each component and passing them as arguments to the components that
    depend on them.

    Args:
        settings: The application's configuration settings.

    Returns:
        A fully assembled WindowedTranscriptProcessor instance.
    """
    print("\n...Assembling the analysis pipeline...")

    # --- Instantiate individual, low-level analysis components ---
    text_cleaner = COMPONENT_REGISTRY["text_cleaner"]()
    speaker_analyzer = COMPONENT_REGISTRY["speaker_analyzer"]()
    entity_extractor = COMPONENT_REGISTRY["entity_extractor"]()
    action_detector = COMPONENT_REGISTRY["action_item_detector"]()
    topic_analyzer = COMPONENT_REGISTRY["topic_analyzer"]()
    
    print("   - Core analysis modules instantiated.")

    # --- Wire up dependencies for composite components ---
    llm_context_preparer = COMPONENT_REGISTRY["llm_context_preparer"](
        entity_extractor=entity_extractor,
        action_detector=action_detector,
        topic_analyzer=topic_analyzer
    )
    
    meeting_processor = COMPONENT_REGISTRY["meeting_processor"](
        text_cleaner=text_cleaner,
        speaker_analyzer=speaker_analyzer,
        context_preparer=llm_context_preparer
    )
    
    print("   - High-level processors configured.")

    # --- Assemble the final, top-level windowed processor ---
    windowed_processor = COMPONENT_REGISTRY["windowed_processor"](
        base_processor=meeting_processor,
        window_duration=settings.window_duration_seconds,
        output_directory=str(settings.output_directory / "processed_windows"),
        output_filename_base=settings.output_filename_base
    )
    
    print("  Windowed analysis pipeline assembly complete.")
    return windowed_processor

def build_data_loader():
    """Builds and returns a TranscriptLoader instance."""
    loader_class = COMPONENT_REGISTRY["transcript_loader"]
    return loader_class()

