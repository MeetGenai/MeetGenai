import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json

import os

import sys
from pathlib import Path


from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

COMMON_ENV_PATH = Path(os.getenv("COMMON_ENV_PATH")).resolve()

load_dotenv(dotenv_path=COMMON_ENV_PATH)

audio_dir = os.getenv("audio_dir")
metadata_dir = os.getenv("metadata_dir")
audio_transcription_output_base = os.getenv("audio_transcription_output_base")


DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
API_ADD_MEETING_ENDPOINT = os.getenv("API_ADD_MEETING_ENDPOINT")

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
n_results = int(os.getenv("n_results"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

SUMMARY_GEN_LLM_URL = os.getenv("SUMMARY_GEN_LLM_URL")
SUMMARY_GEN_LLM_MODEL_INTERMEDIATE = os.getenv("SUMMARY_GEN_LLM_MODEL_INTERMEDIATE")
SUMMARY_GEN_LLM_MODEL_FINAL = os.getenv("SUMMARY_GEN_LLM_MODEL_FINAL")
SUMMARY_GEN_LLM_CONTEXT_SIZE = int(os.getenv("SUMMARY_GEN_LLM_CONTEXT_SIZE"))

FILE_DIR_NAME = os.getenv("raw_transcripts")
input_directory = os.getenv("input_directory")
output_directory = os.getenv("output_directory")
output_file_name = os.getenv("output_file_name")


# HOST = "localhost"
# PORT = 8000
# COLLECTION_NAME = "meeting_tldrs"
# EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# n_results = 3



class ChromaDBClass:
    def __init__(self):
        self.client = None
        self.colleciton = None
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        

    def init_db(self):
        if (self.client == None):
            self.client = chromadb.HttpClient(host=DB_HOST, port=DB_PORT)
        if (self.colleciton == None):
            self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)


    def store_meeting_summary(self, meeting_id, summary_text, meeting_series, is_latest=False):
        embedding = self.embedding_model.encode([summary_text])
        self.collection.add(
            embeddings=embedding.tolist(),
            documents=[summary_text],
            metadatas=[{
                "meeting_series": meeting_series,
                "latest": is_latest     # Store the latest status
            }],
            ids=[meeting_id]
        )

    
    def get_relevant_docs(self, cur_meeting_summary, cur_meeting_series):
        query_embedding = self.embedding_model.encode([cur_meeting_summary])
    
        # Search for similar meetings
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where={"meeting_series": cur_meeting_series}  # Filter
        )

        return (",".join([v[0] for v in results["documents"] if len(v) > 0])).strip(",")
    

    def get_next_meeting_id(self):
        # Fetch all existing meeting IDs
        docs = self.collection.get(include=["ids"])
        existing_ids = docs.get("ids", [])
        max_id = 0
        for meeting_id in existing_ids:
            if meeting_id.startswith("meeting_"):
                try:
                    id_num = int(meeting_id.split("_")[1])
                    max_id = max(max_id, id_num)
                except Exception:
                    pass
        return f"meeting_{max_id + 1}"



class MeetingSummaryGeneratorWithContext:
    def __init__(self):
        self.final_summary = None
        
    
    
    def generate_summary(self, prompt, model):
        # prompt = f"""
        # Based on the current meeting transcript and previous meeting context, 
        # generate an enhanced summary that builds upon previous discussions.
        
        # Previous meetings context:
        # {previous_context}
        
        # Current meeting transcript:
        # {current_transcript}
        
        # Please provide:
        # 1. Key points from current meeting
        # 2. Connections to previous discussions
        # 3. Progress updates on ongoing topics
        # 4. Action items and follow-ups
        # """
        
        # Ollama API call
        response = requests.post(
            # 'http://localhost:11434/api/generate',
            SUMMARY_GEN_LLM_URL,
            json={
                # 'model': 'llama2:13b',  # or mistral:7b
                # 'model': 'mistral:7b',
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_ctx': SUMMARY_GEN_LLM_CONTEXT_SIZE  # Set context length
                }
            }
        )
        # print(response)
        return response.json()['response']
    

    
    def get_contextual_prompt(self, current_transcript, context_string):
        prompt = f"""
            Analyze previous meeting context and current meeting transcript and provide a structured summary. Use EXACTLY this format:

            **Action Items:**
            - [Action description] | [Deadline: YYYY-MM-DD if mentioned] | [Responsible: Speaker name]
            - ...

            **Key Notes:**
            - [Important decision or fact 1]
            - [Important decision or fact 2]
            - ...

            **Detailed Summary:**
            [Concise 6-7 sentence overview covering main topics]

            **Meeting Metadata:**
            - Date: Unknown
            - Duration: Unknown

            
            previous meeting context:
            {context_string}
            
            current meeting transcript:
            {current_transcript}
        """
        return prompt

    def get_non_contextual_prompt(self, current_transcript):
        prompt = f"""
            Analyze current meeting transcript and provide a structured summary. Use EXACTLY this format:

            **Action Items:**
            - [Action description] | [Deadline: YYYY-MM-DD if mentioned] | [Responsible: Speaker name]
            - ...

            **Key Notes:**
            - [Important decision or fact 1]
            - [Important decision or fact 2]
            - ...

            **Detailed Summary:**
            [Concise 6-7 sentence overview covering main topics]

            **Meeting Metadata:**
            - Date: Unknown
            - Duration: Unknown

            
            current meeting transcript:
            {current_transcript}
        """
        return prompt
    
    def get_summary(self, transcript, db_object: ChromaDBClass, model, meeting_series=None):
        cur_meeting_summary = transcript
        prompt = ""


        if (meeting_series is not None):
            context_string = db_object.get_relevant_docs(cur_meeting_summary, meeting_series)

            print("Context fetched successfully", context_string)

            prompt = self.get_contextual_prompt(transcript, context_string)
        else:
            prompt = self.get_non_contextual_prompt(transcript)

        if (prompt != ""):
            print("prompt to be executed", prompt)
            self.final_summary = self.generate_summary(prompt, model)
            return self.final_summary
        else:
            return "Error in creating prompt"

def create_summary_for_raw_transcript(transcript: str, meeting_summary_gen_obj: MeetingSummaryGeneratorWithContext, db_obj: ChromaDBClass, model, meeting_series=None):
    # prompt = False
    # if (contextual == False or context is None):
    #     prompt = meeting_summary_gen_obj.get_non_contextual_prompt(transcript)
    # else:
    #     prompt = meeting_summary_gen_obj.get_contextual_prompt(transcript, context)
    summary = meeting_summary_gen_obj.get_summary(transcript, db_obj, model, meeting_series)
    return summary


def get_file_data():
    files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
    str_file_arr = []

    for file in files:
        tmp_str = ""
        file_path = input_directory + "/" + file
        with open(file_path, "r") as f:
            tmp_json = json.load(f)
            tmp_json["context"].pop("conversation_summary")
            str_file_arr.append(json.dumps(tmp_json))
    return str_file_arr


def get_detailed_summary(transcript):
    start = "**Detailed Summary:**"
    end = "**Meeting Metadata:**"

    start_index = transcript.find(start)
    if (start_index == -1):
        return transcript
    end_index = transcript.find(end)
    return transcript[start_index + len(start): end_index].strip().strip("\n").strip()

def save_meeting_summary(summary, meeting_series):
    API_URL = API_HOST + ":" +str(API_PORT) + API_ADD_MEETING_ENDPOINT
    response = requests.post(
        API_URL,
        json={
            'summary': summary,
            'meetingSeries': meeting_series,
        }
    )
    return response

def run(meeting_series = None):
    # meeting_series = None
    # if (len(sys.argv) >= 2):
    #     meeting_series = sys.argv[1]


    db_object = ChromaDBClass()
    db_object.init_db()

    
    files = get_file_data()

    meeting_summary_gen_obj = MeetingSummaryGeneratorWithContext()
    summary_str = ""

    for index, file_text in enumerate(files):

        cur_summary = create_summary_for_raw_transcript(file_text, meeting_summary_gen_obj, db_object, SUMMARY_GEN_LLM_MODEL_INTERMEDIATE, meeting_series)
        with open("str_"+str(index)+".txt", "w") as f:
            f.write(cur_summary)
        summary_str += cur_summary

    final_summary = create_summary_for_raw_transcript(summary_str, meeting_summary_gen_obj, db_object,SUMMARY_GEN_LLM_MODEL_INTERMEDIATE, meeting_series)
    
    # save_summary_to_db(final_summary)
    

    with open(output_directory + "/" + output_file_name, "w") as f:
        f.write(final_summary)

    if (meeting_series is not None):
        meeting_summary = get_detailed_summary(final_summary)
        ## TODO:save back meeting summary with meeting series
        response = save_meeting_summary(meeting_summary, meeting_series)
        print(response)
        




# if __name__ == "__main__":
#     run()