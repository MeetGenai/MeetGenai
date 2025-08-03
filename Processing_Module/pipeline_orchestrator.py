"""
pipeline_orchestrator.py

Purpose:
    This module serves as the master conductor for the entire advanced transcript
    analysis pipeline. It manages the high-level workflow of chunking the
    transcript, orchestrating the multi-modal analysis of each chunk, and then
    performing a final, meeting-wide synthesis that includes entity resolution
    and temporal tracking.

Key Features:
    - Manages the end-to-end, windowed analysis process.
    - Delegates chunk analysis to a `TranscriptChunkProcessor`.
    - After window processing, it invokes the `EntityResolver` and `TemporalTracker`
      for holistic, meeting-wide analysis.
    - Generates and saves both individual chunk outputs and a final,
      comprehensive master report for the entire meeting.
"""

import json
from copy import deepcopy
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import pipeline components for dependency injection
from conversation_chunker import ConversationChunker
from chunk_processor import TranscriptChunkProcessor
from entity_resolver import EntityResolver
from temporal_tracker import TemporalTracker

class PipelineOrchestrator:
    """
    Manages the full, multi-stage analysis of a meeting transcript.
    """

    def __init__(self,
                 chunker: ConversationChunker,
                 processor: TranscriptChunkProcessor,
                 entity_resolver: EntityResolver,
                 temporal_tracker: TemporalTracker,
                 output_dir: Path,
                 filename_prefix: str):
        """
        Initializes the orchestrator.

        Args:
            chunker: An instance of the ConversationChunker.
            processor: An instance of the TranscriptChunkProcessor.
            entity_resolver: An instance of the EntityResolver.
            temporal_tracker: An instance of the TemporalTracker.
            output_dir: The root directory where all output will be saved.
            filename_prefix: The base name for the chunk output files.
        """
        self.chunker = chunker
        self.processor = processor
        self.entity_resolver = entity_resolver
        self.temporal_tracker = temporal_tracker
        self.output_dir = output_dir
        self.filename_prefix = filename_prefix
        self.chunk_output_dir = output_dir / "processed_chunks"

    def execute(self,
                full_transcript: List[Dict[str, Any]],
                meeting_date: Optional[str] = None) -> None:
        """
        Runs the entire pipeline: chunking, chunk processing, and final synthesis.
        """
        if not full_transcript:
            print("  No transcript data provided to orchestrator. Aborting.")
            return

        print(f"  Starting advanced windowed processing...")
        self.chunk_output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Split the full transcript into time-based chunks
        windows = self.chunker.chunk_by_time(full_transcript)
        if not windows:
            print("  Could not create any time windows from the transcript data.")
            return

        print(f"   |> Transcript split into {len(windows)} time windows.")

        # Step 2: Process each window individually
        all_window_outputs = []
        for window in windows:
            window_id = window['window_id']
            print(f"\n   [ Analyzing window {window_id}/{len(windows)} ({window['start_seconds']}s - {window['end_seconds']}s) ]")
            try:
                segments_in_window = deepcopy(window.get('source_segments', []))
                processed_analysis = self.processor.process_chunk(
                    transcript_segments=segments_in_window,
                    meeting_date=meeting_date
                )
                if processed_analysis:
                    # Assemble the final output with metadata at the top for readability
                    final_window_output = {
                        'window_metadata': {
                            'window_id': window_id,
                            'start_seconds': window['start_seconds'],
                            'end_seconds': window['end_seconds'],
                        },
                        **processed_analysis  # Unpack the rest of the analysis data
                    }
                    output_path = self.chunk_output_dir / f"{self.filename_prefix}_{window_id:03d}.json"
                    if self.processor.save_chunk_output(final_window_output, output_path):
                        print(f"   |>   Saved window {window_id} analysis to {output_path.name}")
                    all_window_outputs.append(final_window_output)
            except Exception as e:
                print(f"   |>   A critical error occurred while processing window {window_id}: {e}")
                continue
        
        print(f"\n  Window processing complete. Processed {len(all_window_outputs)} of {len(windows)} windows.")

        # Step 3: Perform final, meeting-wide analysis
        if all_window_outputs:
            print("\n  Performing final meeting-wide synthesis...")
            self.finalize_analysis(all_window_outputs)
        else:
            print("\n  No windows were successfully processed. Skipping final synthesis.")

    def finalize_analysis(self, all_window_outputs: List[Dict[str, Any]]) -> None:
        """
        Runs post-processing analyses across all windows and saves a master report.
        """
        # Run entity resolution across all found entities
        resolved_entities = self.entity_resolver.resolve_across_windows(all_window_outputs)
        print("   |> Unified and resolved entities across the meeting.")

        # Generate the temporal topic timeline
        timeline = self.temporal_tracker.generate_meeting_timeline(all_window_outputs)
        print("   |> Generated temporal topic timeline.")

        # Assemble the final master report
        master_report = {
            'meeting_summary': self.generate_final_summary(all_window_outputs),
            'holistic_analysis': {
                'resolved_entities': resolved_entities,
                'topic_evolution_timeline': timeline
            },
            'window_by_window_data': all_window_outputs
        }

        # Save the master report
        report_path = self.output_dir / "meeting_master_report.json"
        try:
            with report_path.open('w', encoding='utf-8') as f:
                # Exclude bulky data from the top-level report for readability
                for window_data in master_report['window_by_window_data']:
                    window_data.pop('llm_prompt', None)
                    window_data.pop('processed_transcript_chunk', None)
                
                json.dump(master_report, f, indent=2, ensure_ascii=False)
            print(f"   |>   Saved final master report to: {report_path.name}")
        except (IOError, TypeError) as e:
            print(f"   |>   Error saving master report: {e}")

    def generate_final_summary(self, all_window_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates aggregated statistics across all successfully processed windows."""
        if not all_window_outputs:
            return {'status': 'No windows were processed successfully.'}

        total_tasks = sum(len(out['analysis_context']['extracted_intelligence']['outcomes']['tasks']) for out in all_window_outputs)
        total_decisions = sum(len(out['analysis_context']['extracted_intelligence']['outcomes']['decisions']) for out in all_window_outputs)
        
        return {
            'total_windows_processed': len(all_window_outputs),
            'total_action_items_found': total_tasks,
            'total_decisions_found': total_decisions,
            'output_location': str(self.output_dir.resolve()),
        }
