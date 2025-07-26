"""
Component responsible for aggregating multiple raw transcript files or
processing a single file into a standardized, time-sorted format.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class TranscriptAggregator:
    """
    Reads, adjusts timestamps, and merges transcript files from a directory,
    or processes a single transcript file.
    """
    def __init__(self):
        """Initializes the TranscriptAggregator."""
        pass

    def _parse_time(self, time_str: str) -> Optional[timedelta]:
        """Parses a time string in HH:MM:SS format into a timedelta object."""
        try:
            t = datetime.strptime(time_str, "%H:%M:%S")
            return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        except (ValueError, TypeError):
            print(f" Warning: Invalid time format '{time_str}'. Skipping time adjustment.")
            return None

    def _process_single_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Processes a single transcript file, adjusting its timestamps based on
        the 'time of recording' header.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data or "time of recording" not in data[0] or "speaker" not in data[0]:
                print(f" Warning: 'time of recording' or 'speaker' missing in {os.path.basename(file_path)}. Assuming it's a pre-processed file.")
                # If headers are missing, assume it's a list of segments already
                return data if isinstance(data, list) else []

            recording_start_time = self._parse_time(data[0]["time of recording"])
            speaker = data[0]["speaker"]
            transcript_entries = data[1:]

            if recording_start_time is None:
                return [] # Cannot process if time is invalid

            updated_entries = []
            for entry in transcript_entries:
                start_delta = timedelta(seconds=entry.get('start', 0))
                end_delta = timedelta(seconds=entry.get('end', 0))

                updated_entry = entry.copy()
                updated_entry['start'] = (recording_start_time + start_delta).total_seconds()
                updated_entry['end'] = (recording_start_time + end_delta).total_seconds()
                updated_entry['speaker'] = speaker
                updated_entries.append(updated_entry)

            return updated_entries

        except (json.JSONDecodeError, IndexError) as e:
            print(f" Error reading or parsing {os.path.basename(file_path)}: {e}")
            return []

    def load_and_process_single_transcript(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Public method to load and process a single transcript file.
        Used when the input directory contains only one file.
        """
        print(f"📂 Processing single transcript file: '{os.path.basename(file_path)}'")
        if not os.path.exists(file_path):
            print(f" Error: Input file not found at '{file_path}'")
            raise FileNotFoundError
        
        return self._process_single_file(file_path)

    def aggregate_from_directory(self, input_dir: str) -> List[Dict[str, Any]]:
        """
        Finds all JSON transcripts in a directory, processes, merges, and sorts them.
        """
        all_entries = []
        print(f" Reading and merging multiple transcripts from: '{input_dir}'")

        files_to_process = [f for f in os.listdir(input_dir) if f.endswith(".json")]
        
        for filename in files_to_process:
            file_path = os.path.join(input_dir, filename)
            processed = self._process_single_file(file_path)
            if processed:
                all_entries.extend(processed)

        if not all_entries:
            print(" Warning: No valid transcript entries could be aggregated.")
            return []

        # Sort the final merged list by the new absolute start times
        sorted_transcript = sorted(all_entries, key=lambda x: x['start'])
        print(f" Aggregated {len(sorted_transcript)} segments from {len(files_to_process)} files.")
        return sorted_transcript

    def save_transcript(self, transcript_data: List[Dict], output_path: str):
        """Saves the final merged transcript to a JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            print(f"    Merged transcript saved for review at: {output_path}")
        except Exception as e:
            print(f" Error saving merged transcript: {e}")
