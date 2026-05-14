#!/usr/bin/env python3
"""Transcribe video/audio files using faster-whisper (large-v3).

Usage:
    python3 transcribe.py <video_or_audio_file> [--model MODEL] [--output-dir DIR]

Outputs:
    <basename>.transcript.txt  - Plain text with [MM:SS] timestamps
    <basename>.srt             - SRT subtitle file
    <basename>.clean.txt       - Transcript with corrections applied (if .corrections.json exists)
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path


def load_corrections(search_dirs):
    """Load corrections dictionary from .corrections.json."""
    for d in search_dirs:
        path = Path(d) / ".corrections.json"
        if path.exists():
            with open(path) as f:
                return json.load(f)
    return {}


def apply_corrections(text, corrections):
    """Apply case-insensitive corrections to text."""
    for wrong, right in corrections.items():
        pattern = re.compile(re.escape(wrong), re.IGNORECASE)
        text = pattern.sub(right, text)
    return text


def format_timestamp_mm_ss(seconds):
    """Format seconds as MM:SS."""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"


def format_srt_time(seconds):
    """Format seconds as HH:MM:SS,mmm for SRT."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{secs:06.3f}".replace(".", ",")


def transcribe(filepath, model_size="large-v3", output_dir=None):
    """Transcribe a video/audio file and save outputs."""
    from faster_whisper import WhisperModel

    filepath = Path(filepath).resolve()
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    basename = filepath.stem
    if output_dir:
        out = Path(output_dir)
    else:
        out = filepath.parent
    out.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {model_size}...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcribing: {filepath.name}...")
    segments, info = model.transcribe(str(filepath), beam_size=5)

    transcript_lines = []
    srt_lines = []
    full_text_parts = []

    for i, seg in enumerate(segments, 1):
        text = seg.text.strip()
        full_text_parts.append(text)

        # Timestamped transcript
        ts = format_timestamp_mm_ss(seg.start)
        transcript_lines.append(f"[{ts}] {text}")

        # SRT format
        srt_lines.append(str(i))
        srt_lines.append(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}")
        srt_lines.append(text)
        srt_lines.append("")

        # Progress indicator
        if i % 50 == 0:
            print(f"  ...{i} segments processed")

    # Save transcript
    transcript_path = out / f"{basename}.transcript.txt"
    with open(transcript_path, "w") as f:
        f.write("\n".join(transcript_lines))

    # Save SRT
    srt_path = out / f"{basename}.srt"
    with open(srt_path, "w") as f:
        f.write("\n".join(srt_lines))

    # Apply corrections if available
    corrections = load_corrections([filepath.parent, out, Path.cwd()])
    if corrections:
        clean_lines = []
        for line in transcript_lines:
            clean_lines.append(apply_corrections(line, corrections))
        clean_path = out / f"{basename}.clean.txt"
        with open(clean_path, "w") as f:
            f.write("\n".join(clean_lines))
        print(f"Corrections applied: {clean_path}")

    print(f"\nDone! {len(transcript_lines)} segments transcribed.")
    print(f"Language: {info.language} (confidence: {info.language_probability:.2f})")
    print(f"Transcript: {transcript_path}")
    print(f"SRT:        {srt_path}")

    return transcript_path, srt_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe video/audio with faster-whisper")
    parser.add_argument("file", help="Path to video or audio file")
    parser.add_argument("--model", default="large-v3", help="Whisper model size (default: large-v3)")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: same as input file)")
    args = parser.parse_args()

    transcribe(args.file, model_size=args.model, output_dir=args.output_dir)
