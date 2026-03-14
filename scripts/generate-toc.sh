#!/usr/bin/env bash
# generate-toc.sh - Auto-generate Table of Contents for Markdown files
# Scans ## headings and inserts/updates TOC between <!-- TOC --> markers
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MIN_LINES_FOR_TOC=100
DRY_RUN=false
ALL_MODE=false
FILES=()

usage() {
  echo "Usage: $(basename "$0") [OPTIONS] [FILE...]"
  echo ""
  echo "Options:"
  echo "  --all       Process all reference files with >${MIN_LINES_FOR_TOC} lines"
  echo "  --dry-run   Preview changes without modifying files"
  echo "  -h, --help  Show this help"
  echo ""
  echo "Examples:"
  echo "  $(basename "$0") path/to/file.md"
  echo "  $(basename "$0") --all"
  echo "  $(basename "$0") --dry-run --all"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      ALL_MODE=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

# Collect files to process
if $ALL_MODE; then
  while IFS= read -r ref_file; do
    line_count=$(wc -l < "$ref_file" | tr -d ' ')
    if [ "$line_count" -gt "$MIN_LINES_FOR_TOC" ]; then
      FILES+=("$ref_file")
    fi
  done < <(find "$ROOT_DIR" -path "*/references/*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | sort)
fi

if [ ${#FILES[@]} -eq 0 ]; then
  echo "No files to process. Use --all or specify file paths."
  exit 0
fi

# Generate GitHub-compatible anchor from heading text
# GitHub rules: lowercase, spaces->hyphens, remove punctuation except hyphens and CJK chars
generate_anchor() {
  local heading="$1"
  echo "$heading" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/ /-/g' \
    | sed 's/[][()*{}+`'"'"'"!@#$%^&=|\\<>,;:.?\/]//g'
}

# Generate TOC from a markdown file
generate_toc() {
  local file="$1"
  local toc=""
  local in_code_block=false

  # Track duplicate anchors using a temp file (bash 3 compatible)
  local anchor_tracker
  anchor_tracker=$(mktemp)
  trap "rm -f '$anchor_tracker'" RETURN

  while IFS= read -r line; do
    # Track fenced code blocks (``` or ~~~)
    if echo "$line" | grep -qE '^\s*(```|~~~)'; then
      if $in_code_block; then
        in_code_block=false
      else
        in_code_block=true
      fi
      continue
    fi

    # Skip headings inside code blocks
    if $in_code_block; then
      continue
    fi

    # Match ## and ### headings (skip # title and ## 目次 itself)
    if echo "$line" | grep -qE '^#{2,3} ' && ! echo "$line" | grep -qE '^## 目次$'; then
      local level
      level=$(echo "$line" | sed 's/^\(#*\).*/\1/' | wc -c | tr -d ' ')
      level=$((level - 1))  # wc -c counts newline
      local heading
      heading=$(echo "$line" | sed 's/^#* //')

      local base_anchor
      base_anchor=$(generate_anchor "$heading")

      # Count previous occurrences of this anchor
      local count
      count=$(grep -c "^${base_anchor}$" "$anchor_tracker" 2>/dev/null || true)
      echo "$base_anchor" >> "$anchor_tracker"

      local anchor
      if [ "$count" -eq 0 ]; then
        anchor="$base_anchor"
      else
        anchor="${base_anchor}-${count}"
      fi

      local indent=""
      if [ "$level" -gt 2 ]; then
        indent="  "
      fi

      toc="${toc}${indent}- [${heading}](#${anchor})"$'\n'
    fi
  done < "$file"

  rm -f "$anchor_tracker"
  printf '%s' "$toc"
}

# Process each file
for file in "${FILES[@]}"; do
  # Resolve to absolute path if relative
  if [[ "$file" != /* ]]; then
    file="$ROOT_DIR/$file"
  fi

  if [ ! -f "$file" ]; then
    echo "[SKIP] File not found: $file"
    continue
  fi

  rel_path="${file#"$ROOT_DIR/"}"
  toc_content=$(generate_toc "$file")

  if [ -z "$toc_content" ]; then
    echo "[SKIP] $rel_path: No headings found"
    continue
  fi

  # Build full TOC block with explicit trailing newline
  toc_tmp="${file}.toc.tmp"
  {
    echo "<!-- TOC -->"
    echo "## 目次"
    echo ""
    printf '%s' "$toc_content"
    echo ""
    echo "<!-- /TOC -->"
  } > "$toc_tmp"

  if $DRY_RUN; then
    echo "[DRY-RUN] $rel_path:"
    cat "$toc_tmp"
    echo "---"
    rm -f "$toc_tmp"
    continue
  fi

  # Check if TOC markers exist
  if grep -q '<!-- TOC -->' "$file" && grep -q '<!-- /TOC -->' "$file"; then
    # Update existing TOC: replace content between markers (preserve position)
    toc_start=$(grep -n '<!-- TOC -->' "$file" | head -1 | cut -d: -f1)
    toc_end=$(grep -n '<!-- /TOC -->' "$file" | head -1 | cut -d: -f1)

    if [ -n "$toc_start" ] && [ -n "$toc_end" ]; then
      {
        head -n $((toc_start - 1)) "$file"
        cat "$toc_tmp"
        tail -n +$((toc_end + 1)) "$file"
      } > "${file}.tmp"
      mv "${file}.tmp" "$file"
    fi
    echo "[UPDATE] $rel_path: TOC updated"
  else
    # Insert TOC after the first # heading line and its following empty line
    title_line=$(grep -n '^# ' "$file" | head -1 | cut -d: -f1)
    if [ -n "$title_line" ]; then
      # Check if next line is empty, if so include it
      insert_after=$title_line
      next_line=$(sed -n "$((title_line + 1))p" "$file")
      if [ -z "$next_line" ]; then
        insert_after=$((title_line + 1))
      fi
      {
        head -n ${insert_after} "$file"
        echo ""
        cat "$toc_tmp"
        echo ""
        tail -n +$((insert_after + 1)) "$file"
      } > "${file}.tmp"
      mv "${file}.tmp" "$file"
    fi
    echo "[INSERT] $rel_path: TOC inserted"
  fi
  rm -f "$toc_tmp"
done
