"""
Configuration loader for the transcript processing pipeline.

This module loads settings from a .env file and provides them as
typed, validated variables for the application. It also establishes
sensible defaults if variables are not set.
"""
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from a .env file if it exists
load_dotenv()

print("...Loading configuration from .env file...")

# --- Path Configuration ---
INPUT_DIR = os.getenv("INPUT_DIR", "./raw_transcripts")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

# --- Processing Parameters ---
try:
    WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 300))
except (ValueError, TypeError):
    print("⚠️ Warning: Invalid WINDOW_SIZE_SECONDS. Using default of 300.")
    WINDOW_SIZE_SECONDS = 300

BASE_FILENAME = os.getenv("BASE_FILENAME", "meeting_analysis")

# --- Metadata ---
# Use today's date if MEETING_DATE is not set in the .env file
MEETING_DATE = os.getenv("MEETING_DATE") or datetime.now().strftime("%Y-%m-%d")


def validate_config():
    """
    Validates the loaded configuration and prints it for verification.
    Returns True if the basic configuration is valid, False otherwise.
    """
    print("\n--- Pipeline Configuration ---")
    print(f"  Input Directory      : {INPUT_DIR}")
    print(f"  Output Directory     : {OUTPUT_DIR}")
    print(f"  Window Size          : {WINDOW_SIZE_SECONDS}s")
    print(f"  Base Filename        : {BASE_FILENAME}")
    print(f"  Meeting Date         : {MEETING_DATE}")
    print("----------------------------\n")
    
    # A simple validation check
    if not INPUT_DIR or not OUTPUT_DIR:
        print(" Error: INPUT_DIR and OUTPUT_DIR must be set in the .env file.")
        return False
    return True

# Run validation on import
is_config_valid = validate_config()
