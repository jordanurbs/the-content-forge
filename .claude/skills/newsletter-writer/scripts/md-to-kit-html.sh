#!/usr/bin/env bash
# md-to-kit-html.sh — Convert a newsletter markdown draft to Kit-ready HTML
# Usage: ./md-to-kit-html.sh <input.md> [output.html]
#
# Strips YAML frontmatter, converts markdown formatting to HTML paragraphs,
# preserves {{ subscriber.first_name }} template tags, and extracts the
# subject from the first H1.
#
# Implementation: delegates to a Python helper for reliable regex backreferences
# (the previous awk-based implementation had a known bug where `\\1` emitted
# literal `\1` instead of the captured group, breaking bold and italic spans).

set -euo pipefail

INPUT="${1:?Usage: md-to-kit-html.sh <input.md> [output.html]}"
OUTPUT="${2:-}"

if [ ! -f "$INPUT" ]; then
  echo "Error: File not found: $INPUT" >&2
  exit 1
fi

python3 - "$INPUT" "$OUTPUT" <<'PYEOF'
import re
import sys

input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else ""

with open(input_path) as f:
    text = f.read()

# Strip YAML frontmatter
fm_match = re.match(r"^---\n.*?\n---\n", text, re.S)
if fm_match:
    text = text[fm_match.end():]

# Extract subject from first H1
subject = ""
h1_match = re.search(r"^#\s+(.+)$", text, re.M)
if h1_match:
    subject = h1_match.group(1).strip()
    text = re.sub(r"^#\s+.+\n?", "", text, count=1, flags=re.M)

def inline(line):
    """Apply inline markdown: bold, italic, links."""
    line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", line)
    line = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", line)
    line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
    return line

out = []
para = []
bq_lines = []

class State:
    in_blockquote = False
state = State()

def flush_para():
    if para:
        joined = "<br>".join(inline(p) for p in para)
        out.append(f"<p>{joined}</p>")
        para.clear()

def flush_bq():
    if bq_lines:
        joined = "<br>".join(inline(p) for p in bq_lines)
        out.append(f"<blockquote><p>{joined}</p></blockquote>")
        bq_lines.clear()
    state.in_blockquote = False

for raw in text.splitlines():
    line = raw.rstrip()

    # Blank line — paragraph break
    if not line.strip():
        flush_para()
        flush_bq()
        continue

    # Horizontal rule
    if re.match(r"^-{3,}$", line):
        flush_para()
        flush_bq()
        out.append("<hr>")
        continue

    # H2 / H3
    m = re.match(r"^(#{2,3})\s+(.+)$", line)
    if m:
        flush_para()
        flush_bq()
        level = len(m.group(1))
        out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        continue

    # Blockquote
    if line.startswith(">"):
        flush_para()
        bq_text = line[1:].lstrip()
        bq_lines.append(bq_text)
        state.in_blockquote = True
        continue
    elif state.in_blockquote:
        flush_bq()

    # Regular paragraph line
    para.append(line)

flush_para()
flush_bq()

html = "\n".join(out)

if output_path:
    with open(output_path, "w") as f:
        f.write(html + "\n")
    print(f"Subject: {subject}")
    print(f"HTML written to: {output_path}")
else:
    print(f"SUBJECT: {subject}")
    print("---")
    print(html)
PYEOF
