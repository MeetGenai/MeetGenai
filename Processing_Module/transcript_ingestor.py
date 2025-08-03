"""
transcript_ingestor.py

Purpose:
    This module provides a dedicated class for loading and validating the
    raw meeting transcript from a JSON file. It serves as the primary entry
    point for data into the analysis pipeline, ensuring that the data
    conforms to the required structure before any processing begins.

Key Features:
    - Loads data from a specified JSON file path.
    - Performs rigorous validation on the file format and content structure.
    - Raises clear, informative errors for common issues like missing files,
      invalid JSON, or malformed segment data.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class TranscriptIngestor:
    """
    Handles the loading and structural validation of a meeting transcript file.
    """

    def load_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Reads a JSON transcript file, validates its structure, and returns its content.

        Args:
            file_path: The `pathlib.Path` object pointing to the input .json file.

        Returns:
            A list of transcript segment dictionaries, where each segment is a
            dictionary containing keys like 'start', 'end', 'speaker', and 'text'.

        Raises:
            FileNotFoundError: If the file does not exist at the specified path.
            ValueError: If the file is not valid JSON, is not a list of objects,
                        or if any segment is missing essential keys.
        """
        print(f"  Ingesting transcript from: '{file_path.name}'")

        if not file_path.is_file():
            raise FileNotFoundError(
                f"The transcript file was not found at the specified path: {file_path}"
            )

        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = json.load(f)

            if not isinstance(content, list):
                raise ValueError("Invalid format: The transcript file must contain a top-level JSON array (list).")

            # Perform a structural check on the first segment as a quick validation
            if content and not self._is_segment_valid(content[0]):
                 raise ValueError(
                    "Invalid segment structure. Each segment must be an object "
                    "containing 'start', 'end', 'speaker', and 'text' keys."
                )

            print(f"   |> Successfully loaded and validated {len(content)} segments.")
            return content

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parsing failed. The file may be corrupted. Details: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred during file ingestion: {e}")
            raise

    def _is_segment_valid(self, segment: Any) -> bool:
        """
        Checks if a single segment dictionary has the required structure.

        Args:
            segment: The segment object to validate.

        Returns:
            True if the segment is a dictionary with all required keys, False otherwise.
        """
        required_keys = {'start', 'end', 'speaker', 'text'}
        return isinstance(segment, dict) and required_keys.issubset(segment.keys())

