from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks
import shutil
import os
import uuid
from typing import Dict

from main import process_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory="output"), name="output")

UPLOAD_DIR = "input"
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


@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"error": "Job not found"})