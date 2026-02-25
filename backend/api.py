from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks
import yaml
import shutil
import os
import uuid
from typing import Dict
from backend.main import process_video

CONFIG_PATH = "./backend/config.yaml"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory="./backend/output"), name="/output")
UPLOAD_DIR = "./backend/input"
os.makedirs(UPLOAD_DIR, exist_ok=True)

jobs: Dict[str, dict] = {}


def run_job(job_id: str, file_path: str):
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["progress"] = 20

    clips = process_video(file_path)

    jobs[job_id]["progress"] = 100
    jobs[job_id]["status"] = "complete"
    jobs[job_id]["clips"] = clips


@app.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.mp4")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "clips": []
    }

    background_tasks.add_task(run_job, job_id, file_path)

    return {"job_id": job_id}


@app.post("/update-keywords")
def update_keywords(new_keywords: list[str] = Body(...)):
    """
    Update the keyword list in config.yaml dynamically.
    """
    if not os.path.exists(CONFIG_PATH):
        return {"error": "Config file not found"}

    # Load existing config
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Update keywords
    if "scoring" not in config:
        config["scoring"] = {}
    config["scoring"]["keywords"] = new_keywords

    # Save back to YAML
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

    return {"message": "Keywords updated successfully", "keywords": new_keywords}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"error": "Job not found"})