import subprocess
import os

def score_segment(text, config):
    score = 0
    keywords = config["scoring"]["keywords"]

    for word in keywords:
        if word.lower() in text.lower():
            score += config["scoring"]["keyword_boost"]

    if "?" in text:
        score += config["scoring"]["question_boost"]

    return score


def merge_segments(segments, config):
    min_len = config["clip"]["min_length"]
    max_len = config["clip"]["max_length"]
    min_score = config["scoring"]["min_score"]

    merged = []
    current = None

    for seg in segments:
        if current is None:
            current = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            }
        else:
            duration = seg["end"] - current["start"]

            if duration <= max_len:
                current["end"] = seg["end"]
                current["text"] += " " + seg["text"]
            else:
                merged.append(current)
                current = {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }

    if current:
        merged.append(current)

    # Filter by length + score
    final_clips = []
    for clip in merged:
        duration = clip["end"] - clip["start"]
        score = score_segment(clip["text"], config)

        if duration >= min_len and score >= min_score:
            clip["score"] = score
            final_clips.append(clip)

    return final_clips


def cut_clip(start, end, input_file, output_file):
    subprocess.run([
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", input_file,
        "-c", "copy",
        output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)