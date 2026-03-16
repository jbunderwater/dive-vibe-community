# Dive Sites API Script

This script uses the World Scuba Diving Sites API from RapidAPI to collect dive site information for any destination worldwide.

## Features

- 🔍 Search dive sites by destination (city, country, or region)
- 📍 Extract GPS coordinates (latitude/longitude)
- 🌍 Get region and ocean information
- 💾 Save results as CSV files for easy analysis
- 🛡️ Robust error handling and graceful failure recovery

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Install the required Python package:
```bash
pip install requests
```

2. The script is ready to use with the pre-configured RapidAPI key.

## Usage

### Basic Usage

```bash
python get_dive_sites.py "Bonaire"
```

This will create a file named `bonaire_divesites.csv` with all available dive sites.

### Examples

```bash
# Search for dive sites in specific destinations
python get_dive_sites.py "Great Barrier Reef"
python get_dive_sites.py "Maldives"
python get_dive_sites.py "Cozumel"
python get_dive_sites.py "Red Sea"

# Search by country
python get_dive_sites.py "Australia"

# Search by city
python get_dive_sites.py "Cairns"
```

## Output Format

The script generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `id` | Unique identifier from the API |
| `name` | Dive site name |
| `region` | Region or area where the dive site is located |
| `latitude` | GPS latitude coordinate |
| `longitude` | GPS longitude coordinate |
| `ocean` | Ocean and sea information |
| `location` | Detailed location information |
| `description` | Dive site description (may be null) |

## API Information

- **API Provider**: World Scuba Diving Sites API via RapidAPI
- **Endpoint**: `https://world-scuba-diving-sites-api.p.rapidapi.com/divesites`
- **Rate Limits**: Subject to RapidAPI plan limits
- **Data Source**: Comprehensive global dive site database

## Error Handling

The script includes comprehensive error handling for:

- Network connectivity issues
- API rate limiting
- Invalid responses
- Missing or malformed data
- File system errors

## Sample Output

```
============================================================
DIVE SITE COLLECTOR - World Scuba Diving Sites API
============================================================
Destination: Bonaire
API Key: 6308f3267d...
============================================================
Requesting: https://world-scuba-diving-sites-api.p.rapidapi.com/divesites
Query parameters: {'query': 'Bonaire'}
Found 88 dive sites for 'Bonaire'

Extracting information from 88 dive sites...
  1. Leonora's Reef - South America, Bonaire
  2. Atlantis - South America, Bonaire
  3. Nukove (Doblet) - South America, Bonaire
  ... and 85 more sites

Saving dive sites to CSV file...
Successfully saved 88 dive sites to bonaire_divesites.csv

✅ Success! Dive sites saved to: bonaire_divesites.csv
📊 Total dive sites collected: 88
📍 Regions: South America, Bonaire
```

## Troubleshooting

### Common Issues

1. **No dive sites found**: Try different search terms or broader locations
2. **API errors**: Check your internet connection and API key validity
3. **Permission errors**: Ensure you have write permissions in the current directory

### Getting Help

If you encounter issues:

1. Check the error messages for specific details
2. Verify your internet connection
3. Try searching for a different destination
4. Check if the API service is available

## Data Quality

- The script handles missing data gracefully by using empty strings
- GPS coordinates are validated before saving
- Duplicate entries are preserved as they may represent different aspects of the same site

## License

This script is part of the Dive Vibe project and follows the same licensing terms. 