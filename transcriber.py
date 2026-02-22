import whisper
import os
import json

def transcribe(video_path, model_name="base", transcript_dir="output/transcripts"):
    os.makedirs(transcript_dir, exist_ok=True)

    model = whisper.load_model(model_name)
    result = model.transcribe(video_path)

    transcript_path = os.path.join(transcript_dir, "transcript.json")

    with open(transcript_path, "w") as f:
        json.dump(result, f, indent=4)

    return result["segments"]