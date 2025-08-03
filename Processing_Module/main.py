#!/usr/bin/env python3
"""
main.py

This script serves as the main entry point for the Advanced Meeting Intelligence Pipeline.

It orchestrates the entire process by:
1. Loading the application configuration from `app_config.py`.
2. Using a `PipelineFactory` to construct the full suite of advanced components.
3. Identifying the input transcript file.
4. Executing the main `PipelineOrchestrator` to run the multi-stage analysis.
5. Displaying a final, comprehensive report showcasing the advanced analytics.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import os

current_dir = os.getcwd()

# sys.path.append(r"C:\Users\puspak\Desktop\Data Science and AI IITM\hackathon25thJuly\gitRepoNew\Processing_Module")
sys.path.append(current_dir + r"\Processing_Module")

# Suppress noisy warnings from third-party libraries for a cleaner output.
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
warnings.filterwarnings('ignore', category=FutureWarning, module='transformers')
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    from app_config import APP_CONFIG
    from component_factory import PipelineFactory
except ImportError as e:
    print(f"  Critical Error: A required module is missing: {e}", file=sys.stderr)
    print("   Please ensure all project files are present and dependencies are installed.", file=sys.stderr)
    sys.exit(1)

class Application:
    """
    Manages the setup and execution of the advanced transcript analysis pipeline.
    """
    def __init__(self):
        """Initializes the application by building the full pipeline."""
        self.config = APP_CONFIG
        factory = PipelineFactory(self.config)
        self.ingestor = factory.create_ingestor()
        self.orchestrator = factory.create_orchestrator()

    def run(self) -> None:
        """
        Executes the full pipeline from data ingestion to final reporting.
        """
        print("\n=================================================")
        print("     EXECUTING MEETING ANALYSIS PIPELINE  ")
        print("=================================================\n")

        try:
            # 1. Find and load the transcript data
            transcript_path = self._find_input_transcript()
            transcript_data = self.ingestor.load_from_file(transcript_path)

            # 2. Execute the main orchestrator, which now handles all processing
            # and saves the final master report internally.
            self.orchestrator.execute(
                full_transcript=transcript_data,
                meeting_date=self.config.meeting_date
            )

            # 3. Display a final confirmation message.
            self._display_completion_message()

        except (FileNotFoundError, ValueError) as e:
            print(f"  Data Loading or Validation Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"  An unexpected critical error occurred during pipeline execution:", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _find_input_transcript(self) -> Path:
        """Locates the single .json file in the configured input directory."""
        print(f"  Searching for transcript in: {self.config.input_dir}")
        json_files = list(self.config.input_dir.glob("*.json"))

        if not json_files:
            raise FileNotFoundError(f"No .json transcript files found in '{self.config.input_dir}'")
        if len(json_files) > 1:
            print(f"  Warning: Found {len(json_files)} .json files. Using the first one: {json_files[0].name}")

        return json_files[0]

    def _display_completion_message(self) -> None:
        """Prints a final message pointing the user to the output files."""
        report_path = self.config.output_dir / "meeting_master_report.json"
        chunk_dir = self.config.output_dir / "processed_chunks"
        
        print("\n=================================================")
        print("            PIPELINE EXECUTION COMPLETE ")
        print("-------------------------------------------------")
        print("All analyses have been successfully completed.")
        print(f"\n  A detailed master report has been saved to:")
        print(f"   {report_path}")
        print(f"\n  Individual chunk analyses are located in:")
        print(f"   {chunk_dir}")
        print("=================================================")

def main():
    """
    The main function that initializes and runs the application.
    """
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        print("\n\n  Pipeline execution interrupted by user. Exiting gracefully.")
        sys.exit(0)

# if __name__ == "__main__":
#     main()
