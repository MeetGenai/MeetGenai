"""
component_factory.py

Purpose:
    This module implements the Factory design pattern to construct and configure
    all components of the advanced transcript analysis pipeline. It acts as a
    centralized assembly line, instantiating each class—from basic tools to
    advanced analyzers—and injecting its dependencies. This approach creates a
    highly modular, maintainable, and easily extensible system.

Key Features:
    - Centralizes the instantiation of all standard and advanced components.
    - Implements dependency injection to wire the entire pipeline together.
    - Uses a configuration object to parameterize the created components.
    - Provides simple factory methods to build the application's main objects.
"""

from app_config import PipelineConfig

# Import all the building blocks of the advanced pipeline
from transcript_ingestor import TranscriptIngestor
from dialogue_sanitizer import DialogueSanitizer
from sentiment_analyzer import SentimentAnalyzer
from participant_analyzer import ParticipantAnalyzer
from conversation_chunker import ConversationChunker
from ner_extractor import NamedEntityExtractor
from outcome_detector import OutcomeDetector
from thematic_analyzer import ThematicAnalyzer
from entity_resolver import EntityResolver
from temporal_tracker import TemporalTracker
from llm_payload_creator import LLMPayloadCreator
from chunk_processor import TranscriptChunkProcessor
from pipeline_orchestrator import PipelineOrchestrator

class PipelineFactory:
    """
    Constructs and wires together all advanced pipeline components.
    """

    def __init__(self, config: PipelineConfig):
        """
        Initializes the factory with the application's configuration.

        Args:
            config: The validated PipelineConfig object.
        """
        self.config = config
        print("\n...Initializing advanced component factory...")

    def create_ingestor(self) -> TranscriptIngestor:
        """Builds and returns a TranscriptIngestor instance."""
        print("   |> Building: TranscriptIngestor")
        return TranscriptIngestor()

    def create_orchestrator(self) -> PipelineOrchestrator:
        """
        Builds the entire advanced processing pipeline and returns the top-level orchestrator.
        """
        print("   |> Assembling full multi-modal analysis pipeline...")

        # --- 1. Instantiate low-level, self-contained analysis tools ---
        sanitizer = DialogueSanitizer()
        sentiment_analyzer = SentimentAnalyzer() # New
        participant_analyzer = ParticipantAnalyzer()
        entity_extractor = NamedEntityExtractor()
        outcome_detector = OutcomeDetector()
        thematic_analyzer = ThematicAnalyzer()
        print("      - Core analytical tools created.")

        # --- 2. Instantiate high-level, meeting-wide analysis tools ---
        entity_resolver = EntityResolver() # New
        temporal_tracker = TemporalTracker() # New
        print("      - Holistic analysis tools created.")

        # --- 3. Instantiate composite components that depend on the tools ---
        llm_payload_creator = LLMPayloadCreator(
            entity_extractor=entity_extractor,
            outcome_detector=outcome_detector,
            thematic_analyzer=thematic_analyzer
        )
        print("      - LLM payload creator configured.")

        # --- 4. Instantiate the processor for a single chunk ---
        chunk_processor = TranscriptChunkProcessor(
            sanitizer=sanitizer,
            sentiment_analyzer=sentiment_analyzer, # Injected
            participant_analyzer=participant_analyzer,
            payload_creator=llm_payload_creator
        )
        print("      - Transcript chunk processor assembled.")

        # --- 5. Instantiate the chunker for splitting the transcript ---
        conversation_chunker = ConversationChunker(
            window_duration_sec=self.config.window_seconds
        )
        print("      - Conversation chunker configured.")

        # --- 6. Assemble the final, top-level orchestrator ---
        orchestrator = PipelineOrchestrator(
            chunker=conversation_chunker,
            processor=chunk_processor,
            entity_resolver=entity_resolver, # Injected
            temporal_tracker=temporal_tracker, # Injected
            output_dir=self.config.output_dir,
            filename_prefix=self.config.output_file_prefix
        )
        print("  Advanced pipeline assembly complete. Orchestrator is ready.")
        return orchestrator
