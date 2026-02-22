import os
import yaml
from typing import List, Dict

from transcriber import transcribe
from clipper import merge_segments, cut_clip


# -----------------------------
# Load Configuration
# -----------------------------
def load_config(config_path: str = "config.yaml") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.yaml not found.")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# -----------------------------
# Core Processing Function
# (Used by FastAPI)
# -----------------------------
def process_video(input_video: str) -> List[Dict]:
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Input video not found: {input_video}")

    config = load_config()

    output_dir = config["output_dir"]
    transcript_dir = config["transcript_dir"]
    whisper_model = config["whisper_model"]
    padding = config["clip"]["padding"]

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(transcript_dir, exist_ok=True)

    segments = transcribe(
        video_path=input_video,
        model_name=whisper_model,
        transcript_dir=transcript_dir
    )

    clips = merge_segments(segments, config)

    saved_clips = []

    for i, clip in enumerate(clips):
        start = max(0, clip["start"] - padding)
        end = clip["end"] + padding

        output_file = os.path.join(
            output_dir,
            f"clip_{i+1}.mp4"
        )

        cut_clip(start, end, input_video, output_file)

        saved_clips.append({
            "file": output_file,
            "score": clip.get("score", 0),
            "text": clip.get("text", ""),
            "start": start,
            "end": end
        })

    return saved_clips


# -----------------------------
# CLI Entry Point
# -----------------------------
if __name__ == "__main__":
    config = load_config()
    input_video = config["input_video"]

    try:
        process_video(input_video)
    except Exception as e:
        print(f"🔥 Error: {e}")