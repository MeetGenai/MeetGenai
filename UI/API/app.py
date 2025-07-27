from fastapi import FastAPI, HTTPException
import chromadb
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import uvicorn

import uuid
import os

from pathlib import Path


from dotenv import load_dotenv

load_dotenv()


COMMON_ENV_PATH = Path(os.getenv("COMMON_ENV_PATH")).resolve()


load_dotenv()


API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
n_results = int(os.getenv("n_results"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")






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


    def store_meeting_summary(self, meeting_id, summary_text, meeting_series):
        
        # Generate embedding
        embedding = self.embedding_model.encode([summary_text])
        
        # Store in vector database
        self.collection.add(
            embeddings=embedding.tolist(),
            documents=[summary_text],
            metadatas=[{
                "meeting_series": meeting_series,
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




app = FastAPI()

db = ChromaDBClass()
db.init_db()

class MeetingInput(BaseModel):
    # emailId: str
    # password: str
    summary: str
    meetingSeries: str = None
    # type: str  # 'new' or 'existing'

class JoinMeetingInput(BaseModel):
    link: str
    email: str
    password: str

class StatusInput(BaseModel):
    status: str  # The new status text, e.g., "in progress", "done"

@app.post("/api/join_meeting")
def join_meeting(meeting_input: JoinMeetingInput):
    dotenv_path = Path("../MeetingJoin_Record/.env")
    with open(dotenv_path, "w") as f:
        f.write(f"EMAIL_ID={meeting_input.email}\n")
        f.write(f"EMAIL_PASSWORD={meeting_input.password}\n")
        f.write(f"MEET_LINK={meeting_input.link}\n")

    # Run the test_firefox.py script
    script_path = Path("../MeetingJoin_Record/test_firefox.py").resolve()
    os.system(f"python {script_path} &")
    
    return {"message": "Meeting join process started."}

@app.get("/api/get_meeting_series")
def get_meeting_series():
    # Example: fetch all unique meeting_series from db.collection metadata
    print("in get meeting series")
    results = db.collection.get(where={"meeting_series": "testing context"})
    print(results)

    docs = db.collection.get(include=["metadatas"])
    # all_records = db.collection.get()
    # print(all_records)
    # db.collection.delete(where={"meeting_series": "existing meeting series"})  # Empty dict usually means 'all'

    series_set = set()
    for meta in docs["metadatas"]:
        if "meeting_series" in meta and meta["meeting_series"]:
            series_set.add(meta["meeting_series"])
    return {"series": list(series_set)}

@app.post("/api/add_meeting")
def add_meeting(meeting: MeetingInput):
    # Validate meeting series uniqueness
    # existing_series = {
    #     ms["meeting_series"]
    #     for ms in db.collection.get(include=["metadatas"])["metadatas"]
    #     if ms.get("meeting_series")
    # }
    # if meeting.type == "new" and meeting.meetingSeries in existing_series:
    #     raise HTTPException(status_code=400, detail="Meeting series already exists.")
    # Store meeting summary (using meetingLink as dummy summary here)
    # meeting_id = meeting.emailId + "_" + meeting.meetingLink
    # meeting_id = db.get_next_meeting_id()
    
    meeting_id = str(uuid.uuid4())
    print(meeting_id, "meeting id")
    db.store_meeting_summary(meeting_id, meeting.summary, meeting.meetingSeries)
    return {"message": "Meeting saved successfully."}

@app.get("/api/get_status")
def get_meeting_series():
    results = db.collection.get(where={"item_type": "status"})
    print(results["documents"])

    if (len(results["documents"]) == 0):
        return "not started"
    else:
        return results["documents"][0]
    
@app.post("/api/update_status")
def update_status(status_in: StatusInput):
    # 1. Look for an existing entry with item_type=status
    results = db.collection.get(where={"item_type": "status"})
    
    # 2. If found, update the existing document
    if results["ids"]:
        status_id = results["ids"][0]  # There should only be one as per your design
        db.collection.update(
            ids=[status_id],
            documents=[status_in.status]
        )
        action = "updated"
    else:
        # 3. If not found, insert a new document for status
        new_id = str(uuid.uuid4())
        db.collection.add(
            ids=[new_id],
            documents=[status_in.status],
            metadatas=[{"item_type": "status"}],
            embeddings=None  # or [] if required by your schema
        )
        action = "inserted"

    return {"message": f"Status {action} successfully."}


@app.delete("/api/delete_status")
def delete_status():
    # Retrieve entries with item_type == "status"
    results = db.collection.get(where={"item_type": "status"})
    if results["ids"]:
        status_id = results["ids"][0]  # Should only be one
        db.collection.delete(ids=[status_id])
        return {"message": "Status entry deleted successfully."}
    else:
        return {"message": "No status entry found to delete."}




if __name__ == "__main__":
    uvicorn.run("app:app", host=API_HOST, port=API_PORT, reload=True)