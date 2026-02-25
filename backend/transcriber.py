# transcriber.py
def transcribe(video_path: str, model_name="small"):
    """
    Replace this with Whisper integration later.
    Currently returns simple test segment.
    """
    return [{
        "start": 0,
        "end": 30,
        "text": "This is a crazy unbelievable moment from the podcast."
    }]

def diarize_speakers(video_path: str, segments: list) -> list:
    """
    Add speaker labels to segments
    """
    # Placeholder: use pyannote.audio for production
    for seg in segments:
        seg["speaker"] = "host"
    return segments

def load_config():
    import yaml
    with open("backend/config.yaml", "r") as f:
        return yaml.safe_load(f)