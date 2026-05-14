#!/usr/bin/env bash
# render.sh — Animate screenshots and reference images into B-roll MP4 clips
#
# Usage: ./render.sh /path/to/storyboard/ref
#
# Scans ref/ for *.png/.jpg (screenshots, web grabs, UI captures),
# applies deterministic randomized 3D camera animations, and outputs
# chroma-keyable MP4 clips on #00FF00 green screen.
#
# Each image gets a unique animation (direction, speed, angle, zoom)
# derived from a hash of its filename — deterministic but varied.
#
# NOTE: This is for STATIC reference images only.
#       AI-generated storyboard images (storyboard/*.png) go
#       through Veo 3.1 / Venice for video generation instead.

set -euo pipefail

REF_DIR="${1:?Usage: ./render.sh /path/to/storyboard/ref}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUBLIC_DIR="${SCRIPT_DIR}/public"
ENTRY_POINT="${SCRIPT_DIR}/src/index.ts"

# Resolve ref dir to absolute path
REF_DIR="$(cd "$REF_DIR" && pwd)"
OUTPUT_DIR="${REF_DIR}/animated"

# Validate input
if [ ! -d "$REF_DIR" ]; then
  echo "Error: Directory not found: $REF_DIR"
  exit 1
fi

# Collect PNGs and JPGs, compatible with bash and zsh
IMAGES=()
while IFS= read -r -d '' img; do
  IMAGES+=("$img")
done < <(find "$REF_DIR" -maxdepth 1 \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \) -print0 | sort -z)

if [ ${#IMAGES[@]} -eq 0 ]; then
  echo "No image files found in $REF_DIR"
  exit 1
fi

echo "Found ${#IMAGES[@]} reference images to animate"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Track copied files for cleanup
COPIES=()

cleanup() {
  for f in "${COPIES[@]}"; do
    rm -f "$f" 2>/dev/null || true
  done
}
trap cleanup EXIT

# Copy ALL images into public/ first so the bundle includes them all
for img_path in "${IMAGES[@]}"; do
  filename="$(basename "$img_path")"
  cp "$img_path" "${PUBLIC_DIR}/${filename}"
  COPIES+=("${PUBLIC_DIR}/${filename}")
done

# Compute djb2 hash and describe the animation for logging
compute_hash() {
  node -e "
    const s = process.argv[1];
    let h = 5381;
    for (let i = 0; i < s.length; i++) h = (h * 33) ^ s.charCodeAt(i);
    h = h >>> 0;

    // Reproduce the mulberry32 PRNG to describe the motion type
    let seed = h | 0;
    function rng() {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    const roll = rng();
    const type = roll < 0.30 ? '3D Tilt' : roll < 0.60 ? 'Orbit' : roll < 0.80 ? 'Zoom' : 'Drift';

    console.log(JSON.stringify({ hash: h, type }));
  " "$1"
}

# Render each image
FIRST=true
for img_path in "${IMAGES[@]}"; do
  filename="$(basename "$img_path")"
  stem="${filename%.*}"

  echo "--- ${filename} ---"

  # Compute hash
  info_json="$(compute_hash "$filename")"
  file_hash="$(node -e "process.stdout.write(String(JSON.parse(process.argv[1]).hash))" "$info_json")"
  motion_type="$(node -e "process.stdout.write(JSON.parse(process.argv[1]).type)" "$info_json")"

  echo "  Motion: ${motion_type} (hash=$file_hash)"

  # Build props JSON
  full_props=$(node -e "
    console.log(JSON.stringify({
      imageFile: process.argv[1],
      hash: parseInt(process.argv[2])
    }));
  " "$filename" "$file_hash")

  # First render: bust cache to pick up copied images. Subsequent renders reuse bundle.
  CACHE_FLAG=""
  if [ "$FIRST" = true ]; then
    CACHE_FLAG="--bundle-cache=false"
    FIRST=false
  fi

  # Render (concurrency=1 avoids Remotion v4 multi-tab issue)
  cd "$SCRIPT_DIR"
  npx remotion render "$ENTRY_POINT" BrollClip "${OUTPUT_DIR}/${stem}.mp4" \
    --props="$full_props" \
    --concurrency=1 \
    --log=error \
    $CACHE_FLAG \
    2>&1 | while IFS= read -r line; do echo "  $line"; done

  echo "  -> ${stem}.mp4"
  echo ""
done

echo "Done! ${#IMAGES[@]} clips rendered to ${OUTPUT_DIR}/"
