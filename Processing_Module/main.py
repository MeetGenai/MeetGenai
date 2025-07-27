#!/usr/bin/env python3
"""
Main script for the end-to-end transcript processing pipeline.

This script orchestrates the aggregation and windowed analysis of transcripts.
It intelligently decides whether to merge multiple files or process a single
file directly based on the contents of the input directory.
"""
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.append(r"C:\Users\puspak\Desktop\Data Science and AI IITM\hackathon25thJuly\gitRepoNew\Processing_Module")

# --- Suppress Warnings ---
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='sklearn')

# --- Load Configuration and Factory ---
try:
    import config
    from pipeline_factory import create_transcript_aggregator, create_windowed_processor
    print(" Pipeline factory loaded successfully.")
except ImportError as e:
    print(f" Error: A required module is missing: {e}")
    sys.exit(1)

def run_full_pipeline(app_config):
    """
    Executes the complete aggregation and processing pipeline using a config object.
    """
    print("=" * 60)
    print(" STARTING END-TO-END TRANSCRIPT PIPELINE")
    print("=" * 60)
    
    start_time = datetime.now()

    try:
        # === STAGE 1: PREPARE TRANSCRIPT DATA ===
        print("\n--- STAGE 1: PREPARING TRANSCRIPT DATA ---")

        try:
            files_to_process = [f for f in os.listdir(app_config.input_dir) if f.endswith(".json")]
        except FileNotFoundError:
            print(f" Error: Input directory not found at '{app_config.input_dir}'")
            return {'success': False, 'error': 'Input directory not found.'}

        transcript_to_process = []
        
        # Decide action based on the number of files found.
        if len(files_to_process) == 0:
            print(" Critical Error: No JSON files found in the input directory. Cannot proceed.")
            return {'success': False, 'error': 'No JSON files found.'}
        
        elif len(files_to_process) == 1:
            print(" Found a single transcript file. Skipping aggregation/merge step.")
            aggregator = create_transcript_aggregator()
            single_file_path = os.path.join(app_config.input_dir, files_to_process[0])
            transcript_to_process = aggregator.load_and_process_single_transcript(single_file_path)
        
        else: # More than one file, requires aggregation.
            print(f" Found {len(files_to_process)} files. Proceeding with full aggregation.")
            aggregator = create_transcript_aggregator()
            transcript_to_process = aggregator.aggregate_from_directory(app_config.input_dir)
            
            # Save the intermediate merged transcript for auditing purposes.
            if transcript_to_process:
                merged_filename = os.path.join(app_config.output_dir, "00_merged_transcript.json")
                aggregator.save_transcript(transcript_to_process, merged_filename)

        # Final check if we have any data to process after Stage 1.
        if not transcript_to_process:
            print(" Critical Error: No valid transcript data available after initial loading. Cannot proceed.")
            return {'success': False, 'error': 'No data to process after Stage 1.'}

        # === STAGE 2: WINDOWED PROCESSING ===
        print("\n--- STAGE 2: ANALYZING TRANSCRIPT ---")
        processor = create_windowed_processor(
            window_size=app_config.window_size,
            output_dir=os.path.join(app_config.output_dir, "processed_windows"),
            base_filename=app_config.base_filename
        )
        
        processed_windows = processor.process_transcript(
            transcript_data=transcript_to_process,
            meeting_date=app_config.meeting_date
        )
        
        summary_stats = processor.get_summary_statistics(processed_windows)

        # --- FINAL REPORT ---
        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 60)
        print(f" PIPELINE COMPLETED SUCCESSFULLY in {duration:.2f}s")
        print("=" * 60)
        for key, value in summary_stats.items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")
        
        return {'success': True, 'summary': summary_stats}

    except Exception as e:
        print(f"\n A critical error occurred during the pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def setup_argument_parser():
    """Sets up the parser for optional command-line overrides."""
    parser = argparse.ArgumentParser(
        description="End-to-end transcript pipeline. Loads settings from .env, which can be overridden by these arguments.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--input-dir', default=config.INPUT_DIR,
                       help=f'Override the input directory. (Default from .env: {config.INPUT_DIR})')
    parser.add_argument('--output-dir', default=config.OUTPUT_DIR,
                       help=f'Override the output directory. (Default from .env: {config.OUTPUT_DIR})')
    parser.add_argument('--window-size', type=int, default=config.WINDOW_SIZE_SECONDS,
                       help=f'Override analysis window size in seconds. (Default from .env: {config.WINDOW_SIZE_SECONDS})')
    parser.add_argument('--filename', default=config.BASE_FILENAME,
                       help=f'Override the base filename for outputs. (Default from .env: {config.BASE_FILENAME})')
    parser.add_argument('--date', default=config.MEETING_DATE,
                       help=f'Override the meeting date (YYYY-MM-DD). (Default from .env: {config.MEETING_DATE})')
    return parser

def main():
    """Main execution function."""
    if not config.is_config_valid:
        sys.exit(1)

    parser = setup_argument_parser()
    args = parser.parse_args()
    
    final_config = argparse.Namespace(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        window_size=args.window_size,
        base_filename=args.filename,
        meeting_date=args.date
    )

    os.makedirs(final_config.output_dir, exist_ok=True)
    
    try:
        results = run_full_pipeline(final_config)
        
        if results.get('success'):
            print("\n Success! All stages complete.")
        else:
            print("\n Failure. The pipeline ended with an error.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n Processing interrupted by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"\n An unexpected top-level error occurred: {e}")
        sys.exit(1)

# if __name__ == "__main__":
#     main()
