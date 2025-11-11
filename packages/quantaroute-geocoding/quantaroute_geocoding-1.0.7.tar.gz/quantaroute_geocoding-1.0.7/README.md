# QuantaRoute Geocoding Python SDK

A **revolutionary** Python library for geocoding addresses to DigiPin codes with **groundbreaking Location Lookup API** and offline processing capabilities.

## 🚀 Revolutionary Features

### 🎯 **NEW: Location Lookup API** - *Service that even government doesn't provide!*
- 🗺️ **Administrative Boundary Lookup**: Get state, division, locality, pincode, district, delivery status from coordinates
- 📊 **Population Density Data**: Mean, min, and max population density from Meta's 30-meter gridded data
- 📍 **36,000+ Postal Boundaries**: Complete coverage across India
- ⚡ **Sub-100ms Response**: Cached responses with database fallback
- 🎯 **Government-Level Precision**: Accuracy that official services don't offer
- 🔄 **Batch Processing**: Up to 100 locations per request

### 🌟 **Core Features**
- 🌐 **Online API Integration**: Full access to QuantaRoute Geocoding API
- 🔌 **Offline Processing**: Process coordinates ↔ DigiPin without internet
- 📊 **CSV Bulk Processing**: Handle large datasets efficiently
- 🚀 **CLI Tools**: Command-line interface for quick operations
- 📈 **Progress Tracking**: Real-time progress bars for bulk operations
- 🔄 **Retry Logic**: Automatic retry with exponential backoff
- 🎯 **Rate Limit Handling**: Intelligent rate limit management

## Installation

```bash
pip install quantaroute-geocoding
```

## Upgrade

```bash
pip install --upgrade quantaroute-geocoding
or
pip install quantaroute-geocoding==<version>
or
pip install --force-reinstall quantaroute-geocoding==<version>
or
pip cache purge
pip install --upgrade quantaroute-geocoding
or
pip install --no-cache-dir --upgrade quantaroute-geocoding
```

For offline DigiPin processing, also install the official DigiPin library:

```bash
pip install digipin
```

## Quick Start

### 🚀 **NEW: Revolutionary Location Lookup API**

```python
from quantaroute_geocoding import QuantaRouteClient, LocationLookupClient

# Initialize client
client = QuantaRouteClient(api_key="your-api-key")

# 🚀 REVOLUTIONARY: Get administrative boundaries from coordinates
result = client.lookup_location_from_coordinates(28.6139, 77.2090)
print(f"Pincode: {result['administrative_info']['pincode']}")           # 110001
print(f"Office: {result['administrative_info']['locality']}")          # New Delhi GPO
print(f"Division: {result['administrative_info']['division']}")         # New Delhi GPO
print(f"State: {result['administrative_info']['state']}")             # Delhi
print(f"District: {result['administrative_info']['district']}")         # New Delhi
print(f"Delivery: {result['administrative_info']['delivery']}")         # Delivery
print(f"Pop Density: {result['administrative_info']['mean_population_density']}")  # 11234.56
print(f"DigiPin: {result['digipin']}")           # 39J-438-TJC7
print(f"Response Time: {result['response_time_ms']}ms")  # <100ms

# 🚀 REVOLUTIONARY: Get boundaries from DigiPin
result = client.lookup_location_from_digipin("39J-438-TJC7")
print(f"Pincode: {result['administrative_info']['pincode']}")
print(f"State: {result['administrative_info']['state']}")
print(f"Division: {result['administrative_info']['division']}")
print(f"Locality: {result['administrative_info']['locality']}")
print(f"District: {result['administrative_info']['district']}")

# 📊 Get live statistics (36,000+ boundaries)
stats = client.get_location_statistics()
print(f"Total Boundaries: {stats['totalBoundaries']:,}")
print(f"Total States: {stats['totalStates']}")
```

### 🌟 **Traditional Geocoding API**

```python
# Geocode an address
result = client.geocode("India Gate, New Delhi, India")
print(f"DigiPin: {result['digipin']}")
print(f"Coordinates: {result['coordinates']}")

# Convert coordinates to DigiPin
result = client.coordinates_to_digipin(28.6139, 77.2090)
print(f"DigiPin: {result['digipin']}")

# Reverse geocode DigiPin
result = client.reverse_geocode("39J-438-TJC7")
print(f"Coordinates: {result['coordinates']}")

# Check API health
health = client.get_health()
print(f"Status: {health.get('status')}")
```

### Offline Processing

```python
from quantaroute_geocoding import OfflineProcessor

# Initialize offline processor
processor = OfflineProcessor()

# Convert coordinates to DigiPin (offline)
result = processor.coordinates_to_digipin(28.6139, 77.2090)
print(f"DigiPin: {result['digipin']}")

# Convert DigiPin to coordinates (offline)
result = processor.digipin_to_coordinates("39J-438-TJC7")
print(f"Coordinates: {result['coordinates']}")

# Validate DigiPin format
result = processor.validate_digipin("39J-438-TJC7")
print(f"Valid: {result['isValid']}")
```

### CSV Bulk Processing

```python
from quantaroute_geocoding import CSVProcessor

# Initialize processor
processor = CSVProcessor(api_key="your-api-key")

# Process addresses to DigiPin
result = processor.process_geocoding_csv(
    input_file="addresses.csv",
    output_file="results.csv",
    address_column="address"
)

print(f"Processed {result['total_rows']} rows")
print(f"Success rate: {result['success_rate']:.1%}")

# Process coordinates to DigiPin (can use offline mode)
processor_offline = CSVProcessor(use_offline=True)
result = processor_offline.process_coordinates_to_digipin_csv(
    input_file="coordinates.csv",
    output_file="digipins.csv"
)
```

## Command Line Interface

The package includes a **revolutionary** CLI with Location Lookup capabilities:

### 🚀 **NEW: Revolutionary Location Lookup Commands**

```bash
# Get administrative boundaries from coordinates
quantaroute-geocode location-lookup 28.6139 77.2090 --api-key your-key

# Get boundaries from DigiPin
quantaroute-geocode location-from-digipin "39J-438-TJC7" --api-key your-key

# Get live statistics (36,000+ boundaries)
quantaroute-geocode location-stats --api-key your-key

# Batch location lookup from CSV (coming soon)
quantaroute-geocode location-lookup-csv coordinates.csv boundaries.csv --api-key your-key
```

### 🌟 **Traditional Geocoding Commands**

```bash
# Using API
quantaroute-geocode geocode addresses.csv results.csv --api-key your-key

# With custom columns
quantaroute-geocode geocode data.csv output.csv \
    --address-column street_address \
    --city-column city_name \
    --state-column state_name
```

### Convert coordinates to DigiPin

```bash
# Online processing
quantaroute-geocode coords-to-digipin coordinates.csv digipins.csv --api-key your-key

# Offline processing (no API key needed)
quantaroute-geocode coords-to-digipin coordinates.csv digipins.csv --offline
```

### Convert DigiPin to coordinates

```bash
# Online processing
quantaroute-geocode digipin-to-coords digipins.csv coordinates.csv --api-key your-key

# Offline processing
quantaroute-geocode digipin-to-coords digipins.csv coordinates.csv --offline
```

### Single operations

```bash
# Convert single coordinate to DigiPin
quantaroute-geocode single-coord-to-digipin 28.6139 77.2090 --offline

# Convert single DigiPin to coordinates
quantaroute-geocode single-digipin-to-coords "39J-438-TJC7" --offline

# Check API usage
quantaroute-geocode usage --api-key your-key
```

## CSV File Formats

### Input CSV for Address Geocoding

```csv
address,city,state,pincode,country
"123 Main Street","New Delhi","Delhi","110001","India"
"456 Park Avenue","Mumbai","Maharashtra","400001","India"
```

### Input CSV for Coordinates to DigiPin

```csv
latitude,longitude
28.6139,77.2090
19.0760,72.8777
```

### Input CSV for DigiPin to Coordinates

```csv
digipin
39J-438-TJC7
39J-49J-4867
```

## 🚀 Revolutionary Location Lookup API

### Dedicated Location Lookup Client

```python
from quantaroute_geocoding import LocationLookupClient

# Initialize dedicated location client
location_client = LocationLookupClient(api_key="your-api-key")

# Single coordinate lookup
result = location_client.lookup_coordinates(28.6139, 77.2090)
print(f"📮 Pincode: {result['pincode']}")
print(f"🏢 Office: {result['office_name']}")
print(f"🏛️ Division: {result['division']}")
print(f"⚡ Response Time: {result['response_time_ms']}ms")

# DigiPin to boundaries
result = location_client.lookup_digipin("39J-438-TJC7")
print(f"Administrative boundaries: {result}")

# Batch processing (up to 100 locations)
locations = [
    {"latitude": 28.6139, "longitude": 77.2090},
    {"latitude": 19.0760, "longitude": 72.8777},
    {"digipin": "39J-438-TJC7"}
]
results = location_client.batch_lookup(locations)
print(f"Processed {len(results['results'])} locations")

# Live statistics
stats = location_client.get_statistics()
print(f"🗺️ Total Boundaries: {stats['total_boundaries']:,}")
print(f"⚡ Cache Size: {stats['cache_size']}")

# Coverage information
coverage = location_client.get_coverage_info()
print(f"Service capabilities: {coverage}")
```

### Location Lookup Output Format

```json
{
  "pincode": "110001",
  "office_name": "New Delhi GPO",
  "division": "New Delhi GPO",
  "region": "",
  "circle": "Delhi",
  "coordinates": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "digipin": "39J-438-TJC7",
  "cached": true,
  "response_time_ms": 45
}
```

### Why This is Revolutionary

🎯 **Government-Level Precision**: Access to administrative boundaries that even government APIs don't provide at this level of detail and accessibility.

📍 **36,000+ Boundaries**: Complete coverage of Indian postal boundaries with sub-district level precision.

⚡ **Performance**: Sub-100ms cached responses, <500ms database queries.

🔄 **Batch Processing**: Process up to 100 locations in a single API call.

✨ **Unique Value**: The only service providing this level of administrative boundary lookup precision for India.

## Advanced Features

### Webhook Management

```python
# Register webhook
webhook = client.register_webhook(
    url="https://your-app.com/webhook",
    events=["bulk_processing.completed", "geocoding.completed"]
)

# List webhooks
webhooks = client.list_webhooks()

# Delete webhook
client.delete_webhook(webhook['id'])
```

### Batch Processing with Progress Callback

```python
def progress_callback(processed, total, success, errors):
    print(f"Progress: {processed}/{total} - Success: {success}, Errors: {errors}")

processor = CSVProcessor(api_key="your-key")
result = processor.process_geocoding_csv(
    input_file="large_dataset.csv",
    output_file="results.csv",
    progress_callback=progress_callback
)
```

### Offline Grid Operations

```python
processor = OfflineProcessor()

# Get grid information
grid_info = processor.get_grid_info("39J-438-TJC7")
print(f"Grid center: {grid_info['center']}")
print(f"Grid bounds: {grid_info['bounds']}")

# Find nearby grids
nearby = processor.find_nearby_grids(28.6139, 77.2090, radius_meters=100)
for grid in nearby:
    print(f"DigiPin: {grid['digipin']}, Distance: {grid['distance_meters']}m")

# Calculate distance between coordinates
distance = processor.calculate_distance(28.6139, 77.2090, 28.6150, 77.2100)
print(f"Distance: {distance:.2f} km")
```

## Configuration

### Environment Variables

Set your API key as an environment variable:

```bash
export QUANTAROUTE_API_KEY="your-api-key"
```

### API Configuration

```python
client = QuantaRouteClient(
    api_key="your-key",
    base_url="https://api.quantaroute.com",  # Custom base URL
    timeout=30,  # Request timeout in seconds
    max_retries=3  # Maximum retry attempts
)
```

### CSV Processor Configuration

```python
processor = CSVProcessor(
    api_key="your-key",
    use_offline=False,  # Use offline processing when possible
    batch_size=50,  # Records per API batch
    delay_between_batches=1.0  # Delay in seconds between batches
)
```

## Error Handling

```python
from quantaroute_geocoding import (
    QuantaRouteError,
    APIError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)

try:
    result = client.geocode("Invalid address")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error: {e} (Status: {e.status_code})")
```

## Performance Tips

1. **Use Batch Processing**: Process multiple addresses in batches for better performance
2. **Offline Mode**: Use offline processing for coordinate ↔ DigiPin conversions
3. **Caching**: The API includes intelligent caching - repeated requests are faster
4. **Rate Limits**: The SDK handles rate limits automatically with retry logic
5. **CSV Processing**: Use the CSV processor for large datasets instead of individual API calls

## API Limits

### Traditional Geocoding API

| Tier | Requests/Minute | Monthly Limit | Batch Size |
|------|----------------|---------------|------------|
| Free | 10 | 1,000 | 50 |
| Paid | 100 | 10,000 | 100 |
| Enterprise | 1,000 | Unlimited | 100 |

### 🚀 Revolutionary Location Lookup API

| Tier | Requests/Minute | Monthly Limit | Batch Size | Boundaries |
|------|----------------|---------------|------------|------------|
| Free | 20 | 2,000 | 50 | 36,000+ |
| Paid | 200 | 20,000 | 100 | 36,000+ |
| Enterprise | 2,000 | Unlimited | 100 | 36,000+ |

**Performance Guarantees:**
- ⚡ Cached responses: <100ms
- 🔍 Database queries: <500ms
- 📊 Batch processing: <50ms per location
- 🎯 99.9% uptime SLA (Enterprise)

## Support

- 📧 Email: hello@quantaroute.com
- 🌐 Website: https://quantaroute.com
- 📖 Traditional API Docs: https://api.quantaroute.com/v1/digipin/docs
- 🚀 **NEW: Location Lookup API**: https://api.quantaroute.com/v1/location
- 📊 **Live Statistics**: https://api.quantaroute.com/v1/location/stats

### 🚀 What Makes This Revolutionary?

**QuantaRoute's Location Lookup API is the first and only service to provide:**

✨ **Government-Level Precision**: Administrative boundary data that even government APIs don't provide at this level of detail and accessibility.

📍 **Complete Coverage**: 36,000+ postal boundaries across India with sub-district precision.

⚡ **Blazing Performance**: Sub-100ms cached responses, guaranteed <500ms database queries.

🎯 **Unique Value Proposition**: The only service providing this level of administrative boundary lookup precision for India.

🔄 **Developer-Friendly**: Simple APIs, comprehensive SDKs, and excellent documentation.

**Ready to revolutionize your location intelligence applications?**

## Changelog

### [1.0.7] - 2025-11-10
#### Backend Migration
- 🚀 **Supabase Backend**: Fully compatible with the new Supabase-powered backend infrastructure
- ✅ **API Stability**: Verified compatibility with production API at `https://api.quantaroute.com`
- 🔒 **Enhanced Reliability**: Improved API connection stability and error handling
- 📊 **Production Ready**: Tested and verified with live Supabase backend

#### Technical
- No breaking changes - full backward compatibility maintained
- All existing functionality works seamlessly with new backend
- Improved error messages for better debugging

### [1.0.6] - 2025-11-10
#### Fixed
- ✅ **Location Lookup from DigiPin**: Now uses API endpoint directly instead of offline conversion (more efficient)
- ✅ **Batch Location Lookup**: Now sends DigiPin codes directly to API endpoint (performance improvement)
- ✅ **Version Consistency**: Fixed version mismatch between __init__.py and setup files

#### Added
- ✅ **Health Check**: Added `get_health()` method to check API health status

#### Enhanced
- Improved location lookup performance by using API endpoints directly
- Better error handling for DigiPin format validation

### [1.0.5] - 2025-11-01
#### Added
- 🎉 **Population Density Data**: Added mean, min, and max population density fields from Meta's 30-meter gridded data
- 📍 **District Information**: Added district field for Indian district division as per official records
- ✅ **Delivery Status**: Added delivery field for pincode delivery status
- 🌍 **Complete Geographic Data**: Added state and country fields for comprehensive location information

#### Enhanced
- Improved administrative boundary data with complete coverage (36,000+ postal boundaries)
- All Location Lookup API responses now include population density and district information

### [1.0.5] - Previous Release
- Enhanced Location Lookup API with comprehensive boundary data

### [1.0.0] - Initial Release
- Traditional geocoding API with DigiPin support
- Offline processing capabilities

## License

MIT License - see LICENSE file for details.
