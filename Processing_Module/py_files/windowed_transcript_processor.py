import os
import warnings
from copy import deepcopy
from typing import List, Dict, Any, Optional
from datetime import datetime

# Suppress sklearn warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='sklearn')

from temporal_segmenter import TemporalSegmenter

class WindowedTranscriptProcessor:
    """
    Breaks a long transcript into fixed-length time windows and runs the
    processing pipeline on each window independently.
    """

    def __init__(self,
                 base_processor,
                 window_size: int = 300,
                 output_dir: str = "processed_windows",
                 base_filename: str = "meeting_window"):
        """
        Initializes the windowed processor with injected dependencies.
        
        Args:
            base_processor: A fully configured instance of MeetingTranscriptProcessor.
            window_size (int): The window size in seconds.
            output_dir (str): Directory to save processed files.
            base_filename (str): Base name for the output files.
        """
        self.window_size = window_size
        self.output_dir = output_dir
        self.base_filename = base_filename
        self.base_processor = base_processor
        
        # This segmenter is specific to the windowing logic itself.
        self.segmenter = TemporalSegmenter(window_size=self.window_size)
        
        # Ensure the output directory exists.
        os.makedirs(self.output_dir, exist_ok=True)

    def _split_segments(self, segments: List[Dict[str, Any]]) -> List[List[Dict]]:
        """Return a list of segment lists – one list per time window."""
        if not segments:
            return []
        
        windows = self.segmenter.create_time_windows(segments)
        return [w["segments"] for w in windows if w["segments"]]

    def process_transcript(self,
                          transcript_data: List[Dict[str, Any]],
                          meeting_date: Optional[str] = None) -> List[Dict]:
        """
        Splits transcript into time windows and processes each chunk.
        """
        
        print(f" Starting windowed processing with {self.window_size}s windows...")
        
        if not transcript_data:
            print(" No transcript data provided. Aborting.")
            return []

        # Pre-process the full transcript once to get a clean speaker map
        print("...Performing initial cleaning and speaker analysis...")
        pre_cleaned = self.base_processor.text_cleaner.clean_transcript_segments(transcript_data)
        if not pre_cleaned:
            print(" No segments remained after initial cleaning. Aborting.")
            return []

        speaker_map, _ = self.base_processor.speaker_analyzer.analyze_speakers(pre_cleaned)
        mapped_segments = self.base_processor.speaker_analyzer.apply_speaker_mapping(
            pre_cleaned, speaker_map
        )
        
        # Split the cleaned, speaker-mapped transcript into windows
        windows_of_segments = self._split_segments(mapped_segments)
        if not windows_of_segments:
            print(" Could not create any time windows from the transcript data.")
            return []

        print(f"...Transcript split into {len(windows_of_segments)} time windows.")

        processed_outputs = []
        for idx, segments_in_window in enumerate(windows_of_segments, start=1):
            if not segments_in_window:
                continue

            start_time = segments_in_window[0]['start']
            end_time = segments_in_window[-1]['end']
            print(f"\n Processing window {idx}/{len(windows_of_segments)} ({len(segments_in_window)} segments)...")

            try:
                # Deep-copy to prevent mutations across windows
                window_segments = deepcopy(segments_in_window)

                # Run the full pipeline on this window's data
                output = self.base_processor.process_transcript(
                    window_segments,
                    meeting_date=meeting_date
                )

                # Add window-specific metadata to the output
                output['window_metadata'] = {
                    'window_number': idx,
                    'window_start_s': start_time,
                    'window_end_s': end_time,
                }

                # Save the output for this window to its own file
                outfile = os.path.join(
                    self.output_dir,
                    f"{self.base_filename}_{idx:03d}.json" # Padded for better sorting
                )
                
                if self.base_processor.save_processed_data(output, outfile):
                    print(f" Saved window {idx} to {os.path.basename(outfile)}")
                    processed_outputs.append(output)
                else:
                    print(f" Failed to save window {idx}.")

            except Exception as e:
                print(f" An error occurred while processing window {idx}: {e}")
                continue

        print(f"\n Successfully processed and saved {len(processed_outputs)} windows.")
        return processed_outputs

    def get_summary_statistics(self, all_window_outputs: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics across all processed windows."""
        if not all_window_outputs:
            return { 'error': 'No windows were successfully processed' }

        total_duration = sum(
            output.get('metadata', {}).get('total_duration_minutes', 0)
            for output in all_window_outputs
        )
        total_actions = sum(
            len(output.get('context', {}).get('identified_actions', []))
            for output in all_window_outputs
        )
        total_decisions = sum(
            len(output.get('context', {}).get('identified_decisions', []))
            for output in all_window_outputs
        )
        all_participants = set()
        for output in all_window_outputs:
            participants = output.get('context', {}).get('meeting_info', {}).get('participants', [])
            all_participants.update(participants)

        return {
            'total_windows_processed': len(all_window_outputs),
            'total_duration_minutes': round(total_duration, 2),
            'total_participants': len(all_participants),
            'participants': sorted(list(all_participants)),
            'total_action_items': total_actions,
            'total_decisions': total_decisions,
            'output_directory': os.path.abspath(self.output_dir),
        }
