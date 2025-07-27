import json
from datetime import datetime, timedelta

def parse_time(time_str):
    """Parses a time string in HH:MM:SS format into a timedelta object."""
    try:
        t = datetime.strptime(time_str, "%H:%M:%S")
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    except ValueError:
        # Handle cases where the time format might be incorrect
        print(f"Error: Invalid time format '{time_str}'. Please use HH:MM:SS.")
        return timedelta()

def process_transcript_file(file_path):
    """
    Reads a transcript JSON file, extracts the recording time and speaker,
    updates the start and end times for each entry, and adds the speaker info.

    Args:
        file_path (str): The path to the input JSON file.

    Returns:
        list: A list of transcript entries with updated timestamps and speaker info.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Check for both "time of recording" and "speaker" in the first object
    if not data or "time of recording" not in data[0] or "speaker" not in data[0]:
        print(f"Warning: 'time of recording' or 'speaker' not found in the first entry of {file_path}. Skipping.")
        return []

    recording_start_time = parse_time(data[0]["time of recording"])
    speaker = data[0]["speaker"]  # Extract the speaker's name
    transcript_entries = data[1:]  # The rest of the list contains the transcript

    updated_entries = []
    for entry in transcript_entries:
        start_delta = timedelta(seconds=entry.get('start', 0))
        end_delta = timedelta(seconds=entry.get('end', 0))

        # Create a new dictionary to avoid modifying the original
        updated_entry = entry.copy()
        updated_entry['start'] = (recording_start_time + start_delta).total_seconds()
        updated_entry['end'] = (recording_start_time + end_delta).total_seconds()
        updated_entry['speaker'] = speaker  # Add the speaker to each entry
        updated_entries.append(updated_entry)

    return updated_entries

def merge_and_sort_transcripts(all_entries):
    """
    Merges multiple lists of transcript entries and sorts them by start time.

    Args:
        all_entries (list): A list of lists, where each inner list contains
                           transcript entries from a single file.

    Returns:
        list: A single, sorted list of all transcript entries.
    """
    merged_list = [entry for sublist in all_entries for entry in sublist]
    # Sort the merged list based on the 'start' time of each entry
    return sorted(merged_list, key=lambda x: x['start'])

def save_transcript(transcript_data, output_path):
    """
    Saves the final merged transcript to a JSON file.

    Args:
        transcript_data (list): The final list of transcript entries.
        output_path (str): The path to save the output JSON file.
    """
    with open(output_path, 'w') as f:
        json.dump(transcript_data, f, indent=2)
    print(f"Successfully saved the merged transcript to {output_path}")