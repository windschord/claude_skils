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

# Generate TOC from a markdown file
generate_toc() {
  local file="$1"
  local toc=""

  while IFS= read -r line; do
    # Match ## and ### headings (skip # which is the title)
    if echo "$line" | grep -qE '^#{2,3} '; then
      local level
      level=$(echo "$line" | sed 's/^\(#*\).*/\1/' | wc -c | tr -d ' ')
      level=$((level - 1))  # wc -c counts newline
      local heading
      heading=$(echo "$line" | sed 's/^#* //')

      # Create anchor: lowercase ASCII, keep Japanese chars, replace spaces with hyphens
      local anchor
      anchor=$(echo "$heading" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/[(){}`*\[\]'"'"'\"!@#$%^&+=|\\<>,;:?\/]//g')

      local indent=""
      if [ "$level" -gt 2 ]; then
        indent="  "
      fi

      toc="${toc}${indent}- [${heading}](#${anchor})"$'\n'
    fi
  done < "$file"

  echo "$toc"
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
  toc_block="<!-- TOC -->
## 目次

${toc_content}<!-- /TOC -->"

  if $DRY_RUN; then
    echo "[DRY-RUN] $rel_path:"
    echo "$toc_block"
    echo "---"
    continue
  fi

  # Write TOC to temp file for insertion
  toc_tmp="${file}.toc.tmp"
  echo "$toc_block" > "$toc_tmp"

  # Check if TOC markers exist
  if grep -q '<!-- TOC -->' "$file" && grep -q '<!-- /TOC -->' "$file"; then
    # Update existing TOC: remove old TOC, insert new
    awk '
      /<!-- TOC -->/ { skip=1; next }
      /<!-- \/TOC -->/ { skip=0; next }
      !skip { print }
    ' "$file" > "${file}.tmp"
    # Find the line number of the first ## heading to insert before
    first_h2=$(grep -n '^## ' "${file}.tmp" | head -1 | cut -d: -f1)
    if [ -n "$first_h2" ]; then
      head -n $((first_h2 - 1)) "${file}.tmp" > "${file}.tmp2"
      cat "$toc_tmp" >> "${file}.tmp2"
      echo "" >> "${file}.tmp2"
      tail -n +${first_h2} "${file}.tmp" >> "${file}.tmp2"
      mv "${file}.tmp2" "$file"
    fi
    rm -f "${file}.tmp"
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
      head -n ${insert_after} "$file" > "${file}.tmp"
      echo "" >> "${file}.tmp"
      cat "$toc_tmp" >> "${file}.tmp"
      echo "" >> "${file}.tmp"
      tail -n +$((insert_after + 1)) "$file" >> "${file}.tmp"
      mv "${file}.tmp" "$file"
    fi
    echo "[INSERT] $rel_path: TOC inserted"
  fi
  rm -f "$toc_tmp"
done
