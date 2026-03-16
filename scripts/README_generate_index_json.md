# Generate Index JSON Script

This script generates `index.json` files for dive site directories by parsing markdown frontmatter.

## Overview

The `generate_index_json.py` script scans a directory containing markdown files with dive site information and generates an `index.json` file with metadata extracted from the YAML frontmatter.

## Usage

```bash
# Generate index.json for the current directory
python scripts/generate_index_json.py

# Generate index.json for a specific directory
python scripts/generate_index_json.py divesites/bonaire

# Generate index.json for multiple directories
for dir in divesites/*/; do
    python scripts/generate_index_json.py "$dir"
done
```

## Requirements

- Python 3.6+
- PyYAML library (`pip install pyyaml`)

## Input Format

The script expects markdown files with YAML frontmatter in this format:

```markdown
---
name: Dive Site Name
lat: 12.2106695
lng: -68.3217112
difficulty: Intermediate
maxDepth: 30
entryType: shore
siteType: reef
ref: 16
osmId: 313863131
addedBy: username
---

# Dive Site Name

Content of the dive site description...
```

## Output Format

The script generates an `index.json` file containing an array of dive site objects:

```json
[
  {
    "name": "Dive Site Name",
    "lat": 12.2106695,
    "lng": -68.3217112,
    "difficulty": "Intermediate",
    "maxDepth": 30,
    "entryType": "shore",
    "siteType": "reef",
    "ref": 16,
    "osmId": 313863131,
    "addedBy": "username",
    "filename": "dive-site-name.md"
  }
]
```

## Field Descriptions

- **name**: The name of the dive site (required)
- **lat**: Latitude in decimal degrees (default: 0.0)
- **lng**: Longitude in decimal degrees (default: 0.0)
- **difficulty**: Skill level - "Beginner", "Intermediate", or "Advanced" (default: "Intermediate")
- **maxDepth**: Maximum depth in meters (default: 30)
- **entryType**: Entry method - "shore", "boat", etc. (default: "shore")
- **siteType**: Type of site - "reef", "wreck", "beach", etc. (default: "reef")
- **ref**: Reference number or identifier (default: "")
- **osmId**: OpenStreetMap ID (default: 0)
- **addedBy**: Username of contributor (default: "unknown")
- **filename**: Automatically added by the script

## Features

- **Automatic name extraction**: If no name is in frontmatter, extracts from the first heading (# Name)
- **Data validation**: Validates and converts numeric fields
- **Default values**: Provides sensible defaults for missing fields
- **Error handling**: Gracefully handles malformed frontmatter
- **Sorting**: Sorts dive sites alphabetically by name
- **Summary statistics**: Provides counts by difficulty and coordinate coverage

## Error Handling

The script handles various error conditions:

- Missing frontmatter: Skips files without YAML frontmatter
- Invalid YAML: Warns and skips malformed frontmatter
- Invalid numeric values: Warns and uses default values
- Missing required fields: Uses sensible defaults

## Examples

### Basic usage
```bash
cd divesites/bonaire
python ../../scripts/generate_index_json.py
```

### Batch processing
```bash
# Process all dive site directories
find divesites -name "*.md" -exec dirname {} \; | sort -u | while read dir; do
    python scripts/generate_index_json.py "$dir"
done
```

### Integration with git
```bash
# Add to git hooks to auto-generate index files
# In .git/hooks/pre-commit:
for dir in divesites/*/; do
    python scripts/generate_index_json.py "$dir"
    git add "$dir/index.json"
done
```

## Troubleshooting

### Common Issues

1. **"No frontmatter found"**: Ensure markdown files have YAML frontmatter between `---` markers
2. **"Invalid maxDepth value"**: The script now handles "30m" format automatically
3. **"No markdown files found"**: Check that the directory contains `.md` files (excluding `overview.md`)

### Debug Mode

To see more detailed output, you can modify the script to add debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new dive sites:

1. Create markdown files with proper YAML frontmatter
2. Run the script to generate/update index.json
3. Commit both the markdown files and the updated index.json

## License

This script is part of the dive-vibe project and follows the same license terms. 