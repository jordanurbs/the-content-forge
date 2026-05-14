#!/usr/bin/env bash
# render-cards.sh — Render branded cards via Remotion
#
# Usage:
#   ./render-cards.sh --intro '{"lessonTitle":"...","moduleNumber":"3.1.1"}' \
#                     --outro '{"nextLessonTitle":"...","nextLessonNumber":"3.1.2"}' \
#                     --section '{"partLabel":"Part 1","title":"..."}' --section-output 01-name.mp4 \
#                     --roadmap '{"videoTitle":"...","items":["..."]}' --roadmap-output 00-roadmap.mp4 \
#                     --output-dir /path/to/cards
#
# Card types: --intro, --outro, --section, --roadmap
# Section/roadmap support custom output filenames via --section-output / --roadmap-output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENTRY_POINT="${SCRIPT_DIR}/src/index.ts"

INTRO_PROPS=""
OUTRO_PROPS=""
OUTPUT_DIR=""

# Arrays for section cards (multiple allowed)
SECTION_PROPS_LIST=()
SECTION_OUTPUT_LIST=()

# Roadmap card
ROADMAP_PROPS=""
ROADMAP_OUTPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --intro)
      INTRO_PROPS="$2"
      shift 2
      ;;
    --outro)
      OUTRO_PROPS="$2"
      shift 2
      ;;
    --section)
      SECTION_PROPS_LIST+=("$2")
      shift 2
      ;;
    --section-output)
      SECTION_OUTPUT_LIST+=("$2")
      shift 2
      ;;
    --roadmap)
      ROADMAP_PROPS="$2"
      shift 2
      ;;
    --roadmap-output)
      ROADMAP_OUTPUT="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: ./render-cards.sh [--intro '{...}'] [--outro '{...}'] [--section '{...}' --section-output name.mp4] [--roadmap '{...}'] --output-dir /path"
      exit 1
      ;;
  esac
done

if [ -z "$OUTPUT_DIR" ]; then
  echo "Error: --output-dir is required"
  exit 1
fi

HAS_WORK=false
[ -n "$INTRO_PROPS" ] && HAS_WORK=true
[ -n "$OUTRO_PROPS" ] && HAS_WORK=true
[ ${#SECTION_PROPS_LIST[@]} -gt 0 ] && HAS_WORK=true
[ -n "$ROADMAP_PROPS" ] && HAS_WORK=true

if [ "$HAS_WORK" = false ]; then
  echo "Error: At least one card type must be provided (--intro, --outro, --section, --roadmap)"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

cd "$SCRIPT_DIR"

# Render intro card (~4s = 120 frames at 30fps)
if [ -n "$INTRO_PROPS" ]; then
  echo "--- Rendering intro card ---"
  echo "  Props: $INTRO_PROPS"

  npx remotion render "$ENTRY_POINT" IntroCard "${OUTPUT_DIR}/intro.mp4" \
    --props="$INTRO_PROPS" \
    --concurrency=1 \
    --log=error \
    2>&1 | while IFS= read -r line; do echo "  $line"; done

  echo "  -> intro.mp4"
  echo ""
fi

# Render outro card (~6s = 180 frames at 30fps)
if [ -n "$OUTRO_PROPS" ]; then
  echo "--- Rendering outro card ---"
  echo "  Props: $OUTRO_PROPS"

  npx remotion render "$ENTRY_POINT" OutroCard "${OUTPUT_DIR}/outro.mp4" \
    --props="$OUTRO_PROPS" \
    --concurrency=1 \
    --log=error \
    2>&1 | while IFS= read -r line; do echo "  $line"; done

  echo "  -> outro.mp4"
  echo ""
fi

# Render section title cards (~2.5s = 75 frames at 30fps)
for i in "${!SECTION_PROPS_LIST[@]}"; do
  SECTION_PROPS="${SECTION_PROPS_LIST[$i]}"
  # Use custom output name if provided, otherwise default to section-NN.mp4
  if [ "$i" -lt "${#SECTION_OUTPUT_LIST[@]}" ]; then
    SECTION_FILE="${SECTION_OUTPUT_LIST[$i]}"
  else
    SECTION_FILE="section-$(printf '%02d' $((i + 1))).mp4"
  fi

  echo "--- Rendering section card: $SECTION_FILE ---"
  echo "  Props: $SECTION_PROPS"

  npx remotion render "$ENTRY_POINT" SectionTitleCard "${OUTPUT_DIR}/${SECTION_FILE}" \
    --props="$SECTION_PROPS" \
    --concurrency=1 \
    --log=error \
    2>&1 | while IFS= read -r line; do echo "  $line"; done

  echo "  -> $SECTION_FILE"
  echo ""
done

# Render roadmap card (~5s = 150 frames at 30fps)
if [ -n "$ROADMAP_PROPS" ]; then
  ROADMAP_FILE="${ROADMAP_OUTPUT:-roadmap.mp4}"
  echo "--- Rendering roadmap card: $ROADMAP_FILE ---"
  echo "  Props: $ROADMAP_PROPS"

  npx remotion render "$ENTRY_POINT" RoadmapCard "${OUTPUT_DIR}/${ROADMAP_FILE}" \
    --props="$ROADMAP_PROPS" \
    --concurrency=1 \
    --log=error \
    2>&1 | while IFS= read -r line; do echo "  $line"; done

  echo "  -> $ROADMAP_FILE"
  echo ""
fi

echo "Done! Cards rendered to ${OUTPUT_DIR}/"
