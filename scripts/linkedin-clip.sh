#!/usr/bin/env bash
# linkedin-clip.sh -- Trim intro from video + append YouTube CTA card for LinkedIn
#
# Usage:
#   scripts/linkedin-clip.sh \
#     --input /path/to/video.mp4 \
#     --duration 180 \
#     --title "Video Title" \
#     --output-dir social/linkedin/
#
# Output: <output-dir>/linkedin-clip.mp4

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BROLL_DIR="${PROJECT_DIR}/tools/broll-animator"
ENTRY_POINT="${BROLL_DIR}/src/index.ts"

INPUT=""
DURATION=180
TITLE=""
OUTPUT_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)
      INPUT="$2"
      shift 2
      ;;
    --duration)
      DURATION="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: scripts/linkedin-clip.sh --input <video> --duration <seconds> --title <title> --output-dir <dir>"
      exit 1
      ;;
  esac
done

# Validate required args
if [ -z "$INPUT" ]; then
  echo "Error: --input is required"
  exit 1
fi

if [ -z "$TITLE" ]; then
  echo "Error: --title is required"
  exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
  echo "Error: --output-dir is required"
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: Input file not found: $INPUT"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "--- Step 1: Trimming first ${DURATION}s ---"

ffmpeg -y -i "$INPUT" -t "$DURATION" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 192k \
  -r 30 \
  -pix_fmt yuv420p \
  "$TEMP_DIR/trimmed.mp4" \
  2>&1 | tail -5

echo "  -> trimmed.mp4"
echo ""

echo "--- Step 2: Rendering YouTube CTA card ---"

# Escape title for JSON
JSON_TITLE=$(printf '%s' "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
CTA_PROPS="{\"videoTitle\":${JSON_TITLE}}"

cd "$BROLL_DIR"
npx remotion render "$ENTRY_POINT" YouTubeCtaCard "$TEMP_DIR/cta-raw.mp4" \
  --props="$CTA_PROPS" \
  --concurrency=1 \
  --log=error \
  2>&1 | while IFS= read -r line; do echo "  $line"; done
cd "$PROJECT_DIR"

# Re-encode CTA card to match trimmed clip codec/resolution
ffmpeg -y -i "$TEMP_DIR/cta-raw.mp4" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 192k -ar 48000 \
  -r 30 \
  -pix_fmt yuv420p \
  "$TEMP_DIR/cta.mp4" \
  2>&1 | tail -3

echo "  -> cta.mp4"
echo ""

echo "--- Step 3: Concatenating clip + CTA ---"

# Create concat list
cat > "$TEMP_DIR/concat.txt" <<EOF
file 'trimmed.mp4'
file 'cta.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$TEMP_DIR/concat.txt" \
  -c copy \
  "$OUTPUT_DIR/linkedin-clip.mp4" \
  2>&1 | tail -3

echo "  -> linkedin-clip.mp4"
echo ""

# Validate output
OUTPUT_FILE="$OUTPUT_DIR/linkedin-clip.mp4"
if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Error: Output file not created"
  exit 1
fi

FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat --printf="%s" "$OUTPUT_FILE" 2>/dev/null)
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))

# Get duration via ffprobe
OUTPUT_DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" | cut -d. -f1)

echo "--- Validation ---"
echo "  File: $OUTPUT_FILE"
echo "  Size: ${FILE_SIZE_MB}MB"
echo "  Duration: ${OUTPUT_DURATION}s"

# Check limits (5GB, 15min)
MAX_SIZE=$((5 * 1024 * 1024 * 1024))
if [ "$FILE_SIZE" -gt "$MAX_SIZE" ]; then
  echo "  WARNING: File exceeds LinkedIn 5GB limit"
fi

if [ "$OUTPUT_DURATION" -gt 900 ]; then
  echo "  WARNING: File exceeds LinkedIn 15min limit"
fi

echo ""
echo "Done! LinkedIn clip: $OUTPUT_FILE"
