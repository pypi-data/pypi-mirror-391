#!/usr/bin/env python3
"""
🚀 Batch Location Lookup Example

Demonstrates how to process multiple locations efficiently using the
revolutionary Location Lookup API.
"""

import os
import csv
import time
from quantaroute_geocoding import LocationLookupClient

def process_coordinates_file(api_key: str, input_file: str, output_file: str):
    """Process a CSV file with coordinates and add administrative boundaries"""
    
    client = LocationLookupClient(api_key=api_key)
    
    print(f"🚀 Processing {input_file}...")
    print("=" * 50)
    
    locations = []
    
    # Read input file
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
                locations.append({
                    'latitude': lat,
                    'longitude': lng,
                    'original_data': row
                })
            except (ValueError, KeyError) as e:
                print(f"⚠️ Skipping invalid row: {row} - {e}")
    
    print(f"📊 Found {len(locations)} valid locations")
    
    # Process in batches of 50 (API limit is 100, but 50 is safer)
    batch_size = 50
    all_results = []
    
    for i in range(0, len(locations), batch_size):
        batch = locations[i:i + batch_size]
        batch_locations = [{'latitude': loc['latitude'], 'longitude': loc['longitude']} for loc in batch]
        
        print(f"🔄 Processing batch {i//batch_size + 1} ({len(batch)} locations)...")
        
        try:
            start_time = time.time()
            results = client.batch_lookup(batch_locations)
            end_time = time.time()
            
            batch_results = results.get('results', [])
            
            # Combine with original data
            for j, result in enumerate(batch_results):
                if j < len(batch):
                    combined_result = {
                        **batch[j]['original_data'],
                        **result
                    }
                    all_results.append(combined_result)
            
            print(f"   ✅ Processed {len(batch_results)} locations in {(end_time - start_time) * 1000:.1f}ms")
            print(f"   ⚡ Avg: {((end_time - start_time) * 1000) / len(batch):.1f}ms per location")
            
            # Small delay between batches to be respectful
            if i + batch_size < len(locations):
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Batch failed: {e}")
            # Add failed results with error info
            for loc in batch:
                combined_result = {
                    **loc['original_data'],
                    'error': str(e),
                    'pincode': 'ERROR',
                    'office_name': 'ERROR',
                    'division': 'ERROR'
                }
                all_results.append(combined_result)
    
    # Write results
    if all_results:
        fieldnames = list(all_results[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n🎉 PROCESSING COMPLETE!")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Total processed: {len(all_results)}")
        
        # Show some statistics
        successful = sum(1 for r in all_results if 'error' not in r)
        failed = len(all_results) - successful
        
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success rate: {(successful / len(all_results)) * 100:.1f}%")
        
        # Show sample results
        print(f"\n📋 SAMPLE RESULTS:")
        for i, result in enumerate(all_results[:3]):
            print(f"   {i+1}. {result.get('latitude', 'N/A')}, {result.get('longitude', 'N/A')} → "
                  f"Pincode: {result.get('pincode', 'N/A')}, "
                  f"Office: {result.get('office_name', 'N/A')}")
        
        if len(all_results) > 3:
            print(f"   ... and {len(all_results) - 3} more results")
    
    else:
        print("❌ No results to save")


def create_sample_file():
    """Create a sample coordinates file for testing"""
    sample_data = [
        {'name': 'India Gate, Delhi', 'latitude': 28.6139, 'longitude': 77.2090},
        {'name': 'Gateway of India, Mumbai', 'latitude': 18.9220, 'longitude': 72.8347},
        {'name': 'Bangalore Palace', 'latitude': 12.9984, 'longitude': 77.5946},
        {'name': 'Charminar, Hyderabad', 'latitude': 17.3616, 'longitude': 78.4747},
        {'name': 'Victoria Memorial, Kolkata', 'latitude': 22.5448, 'longitude': 88.3426},
        {'name': 'Hawa Mahal, Jaipur', 'latitude': 26.9239, 'longitude': 75.8267},
        {'name': 'Red Fort, Delhi', 'latitude': 28.6562, 'longitude': 77.2410},
        {'name': 'Marine Drive, Mumbai', 'latitude': 18.9435, 'longitude': 72.8234}
    ]
    
    filename = 'sample_coordinates.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'latitude', 'longitude'])
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"📁 Created sample file: {filename}")
    return filename


def main():
    print("🚀 BATCH LOCATION LOOKUP EXAMPLE")
    print("=" * 60)
    print("✨ Process multiple coordinates to get administrative boundaries!")
    print()
    
    # Get API key
    api_key = os.getenv('QUANTAROUTE_API_KEY')
    if not api_key:
        api_key = input("Enter your QuantaRoute API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return
    
    # Check if user has input file or wants to use sample
    input_file = input("Enter CSV file path (or press Enter to use sample): ").strip()
    
    if not input_file:
        print("📝 Creating sample coordinates file...")
        input_file = create_sample_file()
        print()
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    # Generate output filename
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_with_boundaries.csv"
    
    print(f"📍 Input file: {input_file}")
    print(f"📁 Output file: {output_file}")
    print()
    
    # Process the file
    try:
        process_coordinates_file(api_key, input_file, output_file)
        
        print(f"\n🌟 REVOLUTIONARY RESULTS!")
        print("✨ You've just processed coordinates to administrative boundaries")
        print("🎯 with precision that government services don't provide!")
        print("📍 36,000+ postal boundaries at your service!")
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
