import yaml
import os
from transcriber import transcribe
from clipper import merge_segments, cut_clip

from pathlib import Path

path = Path("input/podcast.mp4")

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

print('Here')

def main():
    config = load_config()

    input_video = config["input_video"]
    output_dir = config["output_dir"]
    transcript_dir = config["transcript_dir"]

    os.makedirs(output_dir, exist_ok=True)

    print("🔎 Transcribing...")
    segments = transcribe(
        input_video,
        config["whisper_model"],
        transcript_dir
    )

    print("🧠 Finding smart clips...")
    clips = merge_segments(segments, config)

    print(f"✂️ Cutting {len(clips)} clips...")

    padding = config["clip"]["padding"]

    for i, clip in enumerate(clips):
        start = max(0, clip["start"] - padding)
        end = clip["end"] + padding

        output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")

        cut_clip(start, end, input_video, output_file)

        print(f"Saved: {output_file}")

    print("✅ Done!")


if __name__ == "__main__":
    main()