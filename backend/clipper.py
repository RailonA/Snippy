# clipper.py
import os
import subprocess
from typing import List, Dict
from pydub import AudioSegment, silence

from backend.transcriber import transcribe, diarize_speakers

def extract_audio(video_path: str, output_audio="temp.wav"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        output_audio
    ]
    subprocess.run(cmd, check=True)
    return output_audio

def detect_silence_segments(audio_path: str, min_silence_len=500, silence_thresh=-35):
    """
    Returns list of non-silent segments in milliseconds
    """
    audio = AudioSegment.from_file(audio_path)
    nonsilent_ranges = silence.detect_nonsilent(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )
    return nonsilent_ranges  # list of [start_ms, end_ms]

    keywords = config.get("scoring", {}).get("keywords", [])
    """
    Returns a viral score based on keywords, duration, and energy
    """
    score = 0
    text_lower = segment_text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            score += 20

    # Energy estimation
    try:
        audio = AudioSegment.from_file(audio_path)
        rms = audio.rms / 1000  # normalize
        score += min(rms * 50, 30)
    except:
        score += 10

    # Ideal length bonus
    if 15 <= duration_s <= 60:
        score += 20

    return min(score, 100)

def burn_subtitles(input_video: str, srt_path: str, output_video: str):
    """
    Burn-in subtitles onto video
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=36,PrimaryColour=&HFFFFFF&'",
        output_video
    ]
    subprocess.run(cmd, check=True)

def convert_to_vertical(input_video: str, output_video: str):
    """
    Crop and scale video to 9:16 vertical format
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", "crop=in_h*9/16:in_h,scale=1080:1920",
        output_video
    ]
    subprocess.run(cmd, check=True)

def cut_clip(start_s: float, end_s: float, input_file: str, output_file: str):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-ss", str(start_s),
        "-to", str(end_s),
        "-c", "copy",
        output_file
    ]
    subprocess.run(cmd, check=True)

def score_clip(text: str, keywords: List[str], duration_s: float, audio_path: str):
    score = 0
    text_lower = text.lower()

    # Keyword scoring
    for kw in keywords:
        if kw.lower() in text_lower:
            score += 20

    # Ideal duration bonus
    if 15 <= duration_s <= 60:
        score += 20

    # Energy bonus
    try:
        audio = AudioSegment.from_file(audio_path)
        rms = audio.rms / 1000
        score += min(rms * 40, 30)
    except:
        pass

    return min(score, 100)
