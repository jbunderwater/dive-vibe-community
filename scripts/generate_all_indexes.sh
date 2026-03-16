#!/bin/bash

# Script to generate index.json files for all dive site directories
# Usage: ./generate_all_indexes.sh [base_directory]

set -e  # Exit on any error

# Default to divesites directory if not specified
BASE_DIR="${1:-divesites}"

if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory '$BASE_DIR' does not exist"
    exit 1
fi

echo "Generating index.json files for all dive site directories in $BASE_DIR"
echo "================================================================"

# Find all subdirectories that contain markdown files
find "$BASE_DIR" -type d | while read -r dir; do
    # Check if directory contains markdown files (excluding overview.md)
    if [ -d "$dir" ] && ls "$dir"/*.md >/dev/null 2>&1; then
        # Skip if only overview.md exists
        markdown_count=$(find "$dir" -name "*.md" ! -name "overview.md" | wc -l)
        if [ "$markdown_count" -gt 0 ]; then
            echo "Processing: $dir"
            python3 scripts/generate_index_json.py "$dir"
            echo "----------------------------------------"
        fi
    fi
done

echo "Index generation complete!"
echo ""
echo "Summary of generated files:"
find "$BASE_DIR" -name "index.json" -exec ls -la {} \; 