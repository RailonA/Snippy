import os
from backend.clipper import (
    extract_audio,
    detect_silence_segments,
    score_clip,
    burn_subtitles,
    convert_to_vertical,
    cut_clip
)
from backend.transcriber import transcribe, load_config
import os
from backend.clipper import cut_clip, score_clip, burn_subtitles, convert_to_vertical, detect_silence_segments
from backend.transcriber import transcribe, diarize_speakers, load_config


def process_video(input_video: str) -> list:
    config = load_config()
    output_dir = config["output_dir"]
    keywords = config["scoring"]["keywords"]
    vertical_enabled = config["clip"]["vertical"]
    burn_subs_enabled = config["clip"]["burn_subtitles"]

    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract audio
    audio_path = extract_audio(input_video)

    # Step 2: Silence detection
    silence_ranges = detect_silence_segments(audio_path)

    # Step 3: Transcription
    segments = transcribe(input_video)

    clips = []

    for i, (start_ms, end_ms) in enumerate(silence_ranges):
        start_s = start_ms / 1000
        end_s = end_ms / 1000

        clip_path = os.path.join(output_dir, f"clip_{i+1}.mp4")

        cut_clip(start_s, end_s, input_video, clip_path)

        duration = end_s - start_s
        text = segments[0]["text"]

        score = score_clip(text, keywords, duration, audio_path)

        if burn_subs_enabled:
            burn_subtitles(clip_path, text)

        if vertical_enabled:
            convert_to_vertical(clip_path)

        clips.append({
            "file": clip_path,
            "score": score,
            "text": text,
            "start": start_s,
            "end": end_s
        })

    return clips