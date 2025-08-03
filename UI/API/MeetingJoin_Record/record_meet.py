import webbrowser
import pyautogui
import soundcard as sc
import soundfile as sf
import time
import os
import numpy as np
from threading import Thread
import psycopg2 
from io import BytesIO 
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DEFAULT_MEETING_URL = os.getenv('MEET_LINK')
DEFAULT_RECORDING_DURATION_SECONDS = 60
DEFAULT_OUTPUT_FILENAME = "meeting_recording.wav"

# --- PostgreSQL Database Configuration ---
# Replace with your local PostgreSQL credentials.
DB_CONFIG = {
    "dbname": "meeting_recordings",
    "user": os.getenv('Username'),
    "password": os.getenv('Password'), 
    "host": "localhost",
    "port": "5432"
}

def select_loopback_device():
    """
    Tries to automatically select the main speaker/headphone loopback device.
    If the choice is not clear, it falls back to a manual user prompt.
    """
    all_devices = sc.all_microphones(include_loopback=True)
    # Filter for devices that ARE loopback devices
    loopback_devices = [d for d in all_devices if d.isloopback]

    if not loopback_devices:
        print("\n❌ CRITICAL ERROR: No loopback audio device found.")
        print("On Windows, ensure 'Stereo Mix' is enabled. On Linux, ensure a monitor device is available.")
        return None

    # --- NEW: Automatic Selection Logic ---
    # Keywords that usually indicate the main system speakers/headphones
    preferred_keywords = ['Speaker', 'Headphones', 'Built-in', 'Analog']
    
    preferred_devices = []
    for device in loopback_devices:
        # Check if any of the preferred keywords are in the device name, but exclude HDMI/DisplayPort
        if any(keyword.lower() in device.name.lower() for keyword in preferred_keywords):
            if 'hdmi' not in device.name.lower() and 'displayport' not in device.name.lower():
                preferred_devices.append(device)

    # If we found exactly one preferred device, use it automatically.
    if len(preferred_devices) == 1:
        selected_device = preferred_devices[0]
        print(f"\n✅ Automatically selected audio device: {selected_device.name}")
        return selected_device

    # --- Fallback to Manual Selection ---
    # This part runs if zero or multiple preferred devices were found.
    print("\n--- Please Select the SYSTEM AUDIO Device to Record ---")
    print("Could not automatically determine the best device. Please choose from the list:")
    for i, device in enumerate(loopback_devices):
        print(f"  [{i}]: {device.name}")

    while True:
        try:
            selection = int(input("Enter the number for the device: "))
            if 0 <= selection < len(loopback_devices):
                return loopback_devices[selection]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def save_audio_to_db(filename, audio_data, samplerate):
    """
    Saves the recorded audio data to the PostgreSQL database.
    """
    conn = None
    try:
        # Convert numpy audio data to an in-memory WAV file
        print("\nConverting audio to WAV format for database...")
        in_memory_wav = BytesIO()
        sf.write(in_memory_wav, audio_data, samplerate, format='WAV')
        in_memory_wav.seek(0) # Rewind the buffer to the beginning
        wav_binary_data = in_memory_wav.read()
        print(f"Audio data is {len(wav_binary_data)} bytes.")

        # Connect to the database
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Database connection successful.")

        # Insert the data into the 'recordings' table
        print(f"Uploading '{filename}' to the database...")
        cur.execute(
            "INSERT INTO recordings (filename, audio_data) VALUES (%s, %s)",
            (filename, psycopg2.Binary(wav_binary_data))
        )
        
        # Commit the transaction
        conn.commit()
        
        # Verify the insert
        if cur.rowcount == 1:
            print("✅ Success! Audio recording saved to the database.")
        else:
            print("⚠️ WARNING: Database command executed, but no rows were inserted.")

    except psycopg2.OperationalError as e:
        print(f"\n❌ DATABASE ERROR: Could not connect to PostgreSQL.")
        print(f"   Please ensure the server is running and the credentials in DB_CONFIG are correct.")
        print(f"   Error details: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred while saving to the database: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def record_system_audio(loopback_device, filename, duration, samplerate):
    """
    Records audio from the selected loopback device and saves it to the database.
    """
    print("\n--- Starting System Audio Recording ---")
    
    try:
        print(f"Starting recording for '{loopback_device.name}' ({duration} seconds)...")
        with loopback_device.recorder(samplerate=samplerate) as rec:
            audio_data = rec.record(numframes=samplerate * duration)
        print("Finished recording.")

        if audio_data is None or audio_data.size == 0:
            print("No audio was recorded. Nothing to save.")
            return

        # Directly save the recorded data
        save_audio_to_db(filename, audio_data, samplerate)

    except Exception as e:
        print(f"\n❌ An error occurred during recording: {e}")

def main():
    """
    Main function to orchestrate the entire process.
    """
    print("--- Meeting Recorder Bot (PostgreSQL - Loopback Only) ---")
    
    # Only select the loopback device
    loopback_device = select_loopback_device()
    if not loopback_device: return
    
    # Get user input for meeting details
    meeting_url = input(f"\nEnter meeting URL (or press Enter for default): ")
    duration_str = input(f"Enter recording duration in seconds (or press Enter for {DEFAULT_RECORDING_DURATION_SECONDS}s): ")
    output_filename = input(f"Enter a filename for the DB record (or press Enter for {DEFAULT_OUTPUT_FILENAME}): ")

    meeting_url = meeting_url or DEFAULT_MEETING_URL
    duration = int(duration_str) if duration_str else DEFAULT_RECORDING_DURATION_SECONDS
    output_filename = output_filename or DEFAULT_OUTPUT_FILENAME
    if not output_filename.lower().endswith('.wav'):
        output_filename += '.wav'

    print(f"\nOpening meeting URL: {meeting_url}")
    webbrowser.open(meeting_url)
    print("Waiting for the meeting page to load...")
    time.sleep(10)

    print("\n--- Trying to automatically join the meeting ---")
    try:
        join_button_location = pyautogui.locateCenterOnScreen('join_button.png', confidence=0.8)
        if join_button_location:
            pyautogui.click(join_button_location)
            print("Clicked the 'Join' button!")
        else:
            raise pyautogui.ImageNotFoundException
    except Exception:
        print("\n⚠️ Could not find 'join_button.png'. Please position mouse over join button.")
        print("I will click in 5 seconds...")
        time.sleep(5)
        pyautogui.click()
        print("Clicked at the current mouse position.")
    
    samplerate = 48000
    time.sleep(5)

    # Call the simplified recording function
    record_system_audio(loopback_device, output_filename, duration, samplerate)
    
    print("\n--- Script finished ---")

if __name__ == "__main__":
    print("="*50)
    print("DISCLAIMER: Please ensure you have consent from all participants before recording.")
    print("="*50)
    
    try:
        import psycopg2
    except ImportError:
        print("❌ Missing dependency: psycopg2. Please run: pip install psycopg2-binary")
        exit()

    main()
