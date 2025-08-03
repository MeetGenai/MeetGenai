import psycopg2
import os

# --- PostgreSQL Database Configuration ---
# This must match the configuration in your recorder bot script.
DB_CONFIG = {
    "dbname": "meeting_recordings",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

def fetch_and_save_latest_audio():
    """
    Connects to the database, fetches the most recent audio recording,
    and saves it as a .wav file.
    """
    conn = None
    try:
        # Connect to the database
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Database connection successful.")

        # SQL query to get the most recent recording based on the highest ID
        # The id column is a SERIAL PRIMARY KEY, so the highest ID is the latest entry.
        query = "SELECT filename, audio_data FROM recordings ORDER BY id DESC LIMIT 1"
        
        print("Fetching the latest audio recording...")
        cur.execute(query)
        
        # Fetch one result
        result = cur.fetchone()
        
        if result:
            filename, audio_binary_data = result
            
            # Ensure the filename is safe to use
            safe_filename = os.path.basename(filename)
            
            print(f"Found recording: '{safe_filename}'")
            
            # Write the binary data to a local .wav file
            # 'wb' mode means 'write binary'
            with open(safe_filename, 'wb') as f:
                f.write(audio_binary_data)
                
            print(f"✅ Success! Audio saved to: {os.path.abspath(safe_filename)}")
        else:
            print("⚠️ No recordings found in the database.")

    except psycopg2.OperationalError as e:
        print(f"\n❌ DATABASE ERROR: Could not connect to PostgreSQL.")
        print(f"   Please ensure the server is running and the credentials in DB_CONFIG are correct.")
        print(f"   Error details: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("--- Fetch Latest Audio from PostgreSQL ---")
    
    # Check for psycopg2 dependency before running
    try:
        import psycopg2
    except ImportError:
        print("❌ Missing dependency: psycopg2. Please run: pip install psycopg2-binary")
        exit()
        
    fetch_and_save_latest_audio()
