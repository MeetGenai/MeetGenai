import os
import requests

from AudioTranscription.main import run as audio_transcription_run
# from Processing_Module.main import main as processing_module_main
from RAGSummarizer.main import run as rag_summarizer_run

from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

common_env = os.getenv("common_env")

load_dotenv(common_env)

audio_dir = os.getenv("audio_dir")
# metadata_dir = os.getenv("metadata_dir")
audio_transcription_output_base = os.getenv("audio_transcription_output_base")

API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
API_ADD_UPDATE_STATUS = os.getenv("API_ADD_UPDATE_STATUS")

cur_pipeline_stage = ""


def update_pipeline_status(status):
    API_URL = API_HOST + ":" +str(API_PORT) + API_ADD_UPDATE_STATUS
    response = requests.post(
        API_URL,
        json={
            "status": status
        }
    )
    return response


try:

    audio_files = [f for f in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, f))]

    # metadata_files = [f for f in os.listdir(metadata_dir) if os.path.isfile(os.path.join(metadata_dir, f))]

    # print(audio_files, metadata_files)
    print(audio_files)
    
    cur_pipeline_stage = "transcription"
    # update_pipeline_status(cur_pipeline_stage)
    
    for index, audio_file in enumerate(audio_files):
        audio_transcription_run(audio_dir + "/" + audio_file, audio_transcription_output_base + str(index) + ".json")

    cur_pipeline_stage = "pre-processing"
    # update_pipeline_status(cur_pipeline_stage)
    from Processing_Module.main import main as processing_module_main
    processing_module_main()
    
    cur_pipeline_stage = "summary generation"
    # update_pipeline_status(cur_pipeline_stage)
    print("cur pipeline stage", cur_pipeline_stage)
    rag_summarizer_run(meeting_series="testing context")

    print("pipeline completed")
    cur_pipeline_stage = "completed"
    # update_pipeline_status(cur_pipeline_stage)


except Exception as e:
    # update_pipeline_status("error in pipeline stage " + cur_pipeline_stage)
    print(e)



