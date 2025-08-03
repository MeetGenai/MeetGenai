"""
app_config.py

Purpose:
    This module serves as the central hub for the application's configuration.
    It leverages `python-dotenv` to load settings from a `.env` file and
    employs a `dataclasses.dataclass` for type-safe, immutable access to
    configuration parameters throughout the pipeline. This approach promotes
    clean, decoupled code by centralizing all configuration management.

Key Features:
    - Loads environment variables from a `.env` file.
    - Validates the presence and integrity of critical settings.
    - Provides a frozen, read-only dataclass (`PipelineConfig`) to prevent
      runtime modifications to the configuration.
    - Gracefully handles configuration errors with user-friendly messages.
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

@dataclass(frozen=True)
class PipelineConfig:
    """
    A read-only container for all pipeline configuration settings.

    Using a frozen dataclass ensures that configuration values are set once
    at startup and cannot be accidentally altered during pipeline execution,
    enhancing predictability and stability.

    Attributes:
        input_dir (Path): The absolute path to the directory containing the input transcript.
        output_dir (Path): The absolute path to the root directory for all output files.
        window_seconds (int): The duration of each analysis window in seconds.
        output_file_prefix (str): The base name for processed window files.
        meeting_date (str): The date of the meeting in 'YYYY-MM-DD' format.
    """
    input_dir: Path
    output_dir: Path
    window_seconds: int
    output_file_prefix: str
    meeting_date: str

def initialize_configuration() -> PipelineConfig:
    """
    Loads, validates, and encapsulates application settings from the .env file.

    This function acts as the single source of truth for configuration. It reads
    the .env file, performs essential validation (e.g., checking if directories
    exist), and constructs the immutable PipelineConfig object.

    Returns:
        An initialized and validated PipelineConfig object.

    Raises:
        SystemExit: If the configuration is missing, invalid, or points to
                    non-existent paths, terminating the application.
    """
    # Load environment variables from the .env file in the project root
    load_dotenv()
    print("...Initializing pipeline configuration...")

    try:
        # --- Load Path Settings ---
        input_path = Path(os.getenv("INPUT_DATA_DIRECTORY", "input_transcripts"))
        output_path = Path(os.getenv("OUTPUT_RESULTS_DIRECTORY", "analysis_results"))

        # --- Load Processing Parameters ---
        window_duration = int(os.getenv("ANALYSIS_WINDOW_SECONDS", 300))
        filename_prefix = os.getenv("OUTPUT_FILENAME_PREFIX", "meeting_analysis")

        # --- Load Metadata ---
        # Use provided date or default to today's date
        date_override = os.getenv("MEETING_DATE_OVERRIDE")
        effective_date = date_override or datetime.now().strftime("%Y-%m-%d")

        config = PipelineConfig(
            input_dir=input_path.resolve(),
            output_dir=output_path.resolve(),
            window_seconds=window_duration,
            output_file_prefix=filename_prefix,
            meeting_date=effective_date
        )

        _perform_validation(config)
        return config

    except (ValueError, TypeError) as e:
        print(f"\n Configuration Error: An invalid value was found in your .env file.")
        print(f"   Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  A critical error occurred while loading settings: {e}")
        sys.exit(1)

def _perform_validation(config: PipelineConfig):
    """
    Conducts sanity checks on the loaded configuration.
    """
    print("\n--- Pipeline Configuration Summary ---")
    print(f"  Input Source  : {config.input_dir}")
    print(f"  Output Target : {config.output_dir}")
    print(f"  Window Size   : {config.window_seconds} seconds")
    print(f"  File Prefix   : {config.output_file_prefix}")
    print(f"  Meeting Date  : {config.meeting_date}")
    print("------------------------------------\n")

    if not config.input_dir.is_dir():
        print(f"  Validation Failed: The specified input directory does not exist.")
        print(f"   Please create this directory or correct the path in your .env file.")
        print(f"   Attempted Path: {config.input_dir}")
        sys.exit(1)

    # Ensure the output directory exists, creating it if necessary
    try:
        config.output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"  Validation Failed: Could not create the output directory.")
        print(f"   Please check permissions for the path.")
        print(f"   Attempted Path: {config.output_dir}")
        print(f"   Error: {e}")
        sys.exit(1)

    print(" Configuration loaded and validated successfully.")

# Create a single, globally accessible configuration instance
# This object will be imported and used by other modules in the application.
APP_CONFIG = initialize_configuration()
