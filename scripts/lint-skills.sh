#!/usr/bin/env bash
# lint-skills.sh - Skill best practices linter
# Checks SKILL.md files against Anthropic's skill authoring best practices
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Options
STRICT=false
if [ "${1:-}" = "--strict" ]; then
  STRICT=true
fi

# Thresholds
MAX_SKILL_LINES=500
MAX_DESCRIPTION_CHARS=1024
MAX_FILE_SIZE_KB=50
MIN_REF_LINES_FOR_TOC=100

# Counters
warnings=0
errors=0
checks=0

warn() {
  echo "[WARN] $1"
  warnings=$((warnings + 1))
}

ok() {
  echo "[OK]   $1"
}

err() {
  echo "[ERR]  $1"
  errors=$((errors + 1))
}

check() {
  checks=$((checks + 1))
}

# Find all SKILL.md files
find_skills() {
  find "$ROOT_DIR" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | sort
}

# Find all reference markdown files
find_references() {
  find "$ROOT_DIR" -path "*/references/*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | sort
}

echo "=== Skill Best Practices Lint ==="
echo ""

# --- Check 1: SKILL.md line count ---
echo "--- SKILL.md line count (limit: ${MAX_SKILL_LINES}) ---"
while IFS= read -r skill_file; do
  check
  rel_path="${skill_file#"$ROOT_DIR/"}"
  line_count=$(wc -l < "$skill_file" | tr -d ' ')
  if [ "$line_count" -gt "$MAX_SKILL_LINES" ]; then
    warn "$rel_path: ${line_count} lines (limit: ${MAX_SKILL_LINES})"
  else
    ok "$rel_path: ${line_count} lines"
  fi
done < <(find_skills)
echo ""

# --- Check 2: Frontmatter validation ---
echo "--- Frontmatter validation ---"
while IFS= read -r skill_file; do
  check
  rel_path="${skill_file#"$ROOT_DIR/"}"

  # Check frontmatter exists
  first_line=$(head -1 "$skill_file")
  if [ "$first_line" != "---" ]; then
    err "$rel_path: Missing YAML frontmatter"
    continue
  fi

  # Extract frontmatter (between first and second ---)
  frontmatter=$(awk 'NR==1{next} /^---$/{exit} {print}' "$skill_file")

  # Check name field
  name_value=$(echo "$frontmatter" | grep -E '^name:' | head -1 | sed 's/^name:[[:space:]]*//')
  if [ -z "$name_value" ]; then
    err "$rel_path: Missing 'name' field in frontmatter"
  else
    # Check name format: lowercase, numbers, hyphens only
    if ! echo "$name_value" | grep -qE '^[a-z0-9-]+$'; then
      warn "$rel_path: name '$name_value' should only contain lowercase letters, numbers, and hyphens"
    fi
    # Check max length
    name_len=${#name_value}
    if [ "$name_len" -gt 64 ]; then
      warn "$rel_path: name is ${name_len} chars (limit: 64)"
    fi
    ok "$rel_path: name='${name_value}'"
  fi

  # Check description field
  desc_value=$(echo "$frontmatter" | grep -E '^description:' | head -1 | sed 's/^description:[[:space:]]*//')
  # Handle YAML block scalar indicators (|, |-, >, >-)
  if [ -z "$desc_value" ] || echo "$desc_value" | grep -qE '^\|[-]?$|^>[-]?$'; then
    # Multi-line: extract indented lines after "description:" until next top-level field
    desc_value=$(echo "$frontmatter" | awk '
      /^description:/ { found=1; next }
      found && /^[a-zA-Z0-9_-]+:/ { exit }
      found { gsub(/^[[:space:]]+/, ""); printf "%s ", $0 }
    ')
    desc_value=$(echo "$desc_value" | sed 's/[[:space:]]*$//')
  fi

  if [ -z "$desc_value" ]; then
    err "$rel_path: Missing 'description' field in frontmatter"
  else
    desc_len=${#desc_value}
    if [ "$desc_len" -gt "$MAX_DESCRIPTION_CHARS" ]; then
      warn "$rel_path: description is ${desc_len} chars (limit: ${MAX_DESCRIPTION_CHARS})"
    fi
  fi
done < <(find_skills)
echo ""

# --- Check 3: Reference files TOC check ---
echo "--- Reference files TOC check (>${MIN_REF_LINES_FOR_TOC} lines need TOC) ---"
while IFS= read -r ref_file; do
  check
  rel_path="${ref_file#"$ROOT_DIR/"}"
  line_count=$(wc -l < "$ref_file" | tr -d ' ')

  if [ "$line_count" -gt "$MIN_REF_LINES_FOR_TOC" ]; then
    # Check for TOC markers or common TOC patterns
    if grep -qiE '(## 目次|## Contents|## Table of Contents|<!-- TOC -->)' "$ref_file"; then
      ok "$rel_path: TOC found (${line_count} lines)"
    else
      warn "$rel_path: No TOC found (${line_count} lines)"
    fi
  fi
done < <(find_references)
echo ""

# --- Check 4: File size check ---
echo "--- File size check (limit: ${MAX_FILE_SIZE_KB}KB) ---"
while IFS= read -r md_file; do
  check
  rel_path="${md_file#"$ROOT_DIR/"}"
  file_size_bytes=$(wc -c < "$md_file" | tr -d ' ')
  file_size_limit_bytes=$((MAX_FILE_SIZE_KB * 1024))
  file_size_kb=$(( (file_size_bytes + 1023) / 1024 ))  # Round up

  if [ "$file_size_bytes" -gt "$file_size_limit_bytes" ]; then
    warn "$rel_path: ${file_size_kb}KB (limit: ${MAX_FILE_SIZE_KB}KB)"
  fi
done < <(find "$ROOT_DIR" -name "*.md" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/docs/*" \
  -not -name "CLAUDE.md" \
  -not -name "MEMORY.md" \
  -not -name "README.md" \
  -not -name "package-lock.json" | sort)
echo ""

# --- Summary ---
echo "=== Summary ==="
echo "Checks: ${checks}"
echo "Warnings: ${warnings}"
echo "Errors: ${errors}"

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "Lint FAILED with ${errors} error(s) and ${warnings} warning(s)"
  exit 1
elif [ "$warnings" -gt 0 ]; then
  echo ""
  if $STRICT; then
    echo "Lint FAILED (strict mode) with ${warnings} warning(s)"
    exit 1
  else
    echo "Lint PASSED with ${warnings} warning(s)"
    exit 0
  fi
else
  echo ""
  echo "Lint PASSED - all checks OK"
  exit 0
fi
