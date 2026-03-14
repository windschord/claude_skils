#!/usr/bin/env bash
# generate-toc.sh - Auto-generate Table of Contents for Markdown files
# Scans ## headings and inserts/updates TOC between <!-- TOC --> markers
# Uses github-slugger via node for exact GitHub anchor compatibility
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SLUG_SCRIPT="$SCRIPT_DIR/github-slug.mjs"

MIN_LINES_FOR_TOC=100
DRY_RUN=false
ALL_MODE=false
FILES=()

# Verify dependencies
if ! command -v node > /dev/null 2>&1; then
  echo "Error: node is required but not found" >&2
  exit 1
fi
if [ ! -f "$SLUG_SCRIPT" ]; then
  echo "Error: $SLUG_SCRIPT not found" >&2
  exit 1
fi

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

# Generate TOC from a markdown file
generate_toc() {
  local file="$1"
  local in_code_block=false

  # Collect headings (skip code blocks)
  local headings_tmp
  headings_tmp=$(mktemp)

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
      echo "$line" >> "$headings_tmp"
    fi
  done < "$file"

  if [ ! -s "$headings_tmp" ]; then
    rm -f "$headings_tmp"
    return
  fi

  # Extract heading texts and generate slugs in batch (single node invocation)
  local texts_tmp slugs_tmp
  texts_tmp=$(mktemp)
  slugs_tmp=$(mktemp)

  sed 's/^#* //' "$headings_tmp" > "$texts_tmp"
  node "$SLUG_SCRIPT" < "$texts_tmp" > "$slugs_tmp"

  # Build TOC by combining heading levels with slugs
  local toc=""
  local line_num=0

  while IFS= read -r heading_line; do
    line_num=$((line_num + 1))
    local level
    level=$(echo "$heading_line" | sed 's/^\(#*\).*/\1/' | wc -c | tr -d ' ')
    level=$((level - 1))  # wc -c counts newline
    local heading
    heading=$(echo "$heading_line" | sed 's/^#* //')
    local anchor
    anchor=$(sed -n "${line_num}p" "$slugs_tmp")

    local indent=""
    if [ "$level" -gt 2 ]; then
      indent="  "
    fi

    toc="${toc}${indent}- [${heading}](#${anchor})"$'\n'
  done < "$headings_tmp"

  rm -f "$headings_tmp" "$texts_tmp" "$slugs_tmp"
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

  # Build full TOC block
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
    title_line=$(grep -n '^# ' "$file" | head -1 | cut -d: -f1 || true)
    if [ -z "$title_line" ]; then
      echo "[SKIP] $rel_path: No top-level heading found"
      rm -f "$toc_tmp"
      continue
    fi
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
    echo "[INSERT] $rel_path: TOC inserted"
  fi
  rm -f "$toc_tmp"
done
