#!/usr/bin/env python3
"""
Basic usage examples for QuantaRoute Geocoding SDK
"""

import os
from quantaroute_geocoding import QuantaRouteClient, OfflineProcessor, CSVProcessor

# Example 1: Online API Usage
def example_online_api():
    print("=== Online API Usage ===")
    
    # Get API key from environment or use test key
    api_key = os.getenv('QUANTAROUTE_API_KEY', 'free_test_key_hash_12345')
    client = QuantaRouteClient(api_key)
    
    try:
        # Geocode an address
        print("1. Geocoding address...")
        result = client.geocode("India Gate, New Delhi, India")
        print(f"   Address: India Gate, New Delhi, India")
        print(f"   DigiPin: {result['digipin']}")
        print(f"   Coordinates: {result['coordinates']['latitude']}, {result['coordinates']['longitude']}")
        print(f"   Confidence: {result['confidence']}")
        
        # Convert coordinates to DigiPin
        print("\n2. Converting coordinates to DigiPin...")
        result = client.coordinates_to_digipin(28.6139, 77.2090)
        print(f"   Coordinates: 28.6139, 77.2090")
        print(f"   DigiPin: {result['digipin']}")
        
        # Reverse geocode DigiPin
        print("\n3. Reverse geocoding DigiPin...")
        result = client.reverse_geocode(result['digipin'])
        print(f"   DigiPin: {result['digipin']}")
        print(f"   Coordinates: {result['coordinates']['latitude']}, {result['coordinates']['longitude']}")
        
        # Check usage
        print("\n4. Checking API usage...")
        usage = client.get_usage()
        usage_info = usage['usage']
        print(f"   Current usage: {usage_info['currentUsage']}")
        print(f"   Monthly limit: {usage_info['monthlyLimit']}")
        print(f"   Tier: {usage_info['tier']}")
        
        # Check API health
        print("\n5. Checking API health...")
        health = client.get_health()
        print(f"   Status: {health.get('status', 'unknown')}")
        if 'uptime' in health:
            print(f"   Uptime: {health['uptime']}")
        
    except Exception as e:
        print(f"   Error: {e}")


# Example 2: Offline Processing
def example_offline_processing():
    print("\n=== Offline Processing ===")
    
    try:
        processor = OfflineProcessor()
        
        # Convert coordinates to DigiPin (offline)
        print("1. Converting coordinates to DigiPin (offline)...")
        result = processor.coordinates_to_digipin(28.6139, 77.2090)
        print(f"   Coordinates: 28.6139, 77.2090")
        print(f"   DigiPin: {result['digipin']}")
        
        # Convert DigiPin to coordinates (offline)
        print("\n2. Converting DigiPin to coordinates (offline)...")
        result = processor.digipin_to_coordinates(result['digipin'])
        print(f"   DigiPin: {result['digipin']}")
        print(f"   Coordinates: {result['coordinates']['latitude']}, {result['coordinates']['longitude']}")
        
        # Validate DigiPin
        print("\n3. Validating DigiPin...")
        result = processor.validate_digipin("39J-438-TJC7")
        print(f"   DigiPin: 39J-438-TJC7")
        print(f"   Valid: {result['isValid']}")
        
        # Get grid information
        print("\n4. Getting grid information...")
        grid_info = processor.get_grid_info("39J-438-TJC7")
        print(f"   DigiPin: 39J-438-TJC7")
        print(f"   Center: {grid_info['center']['latitude']}, {grid_info['center']['longitude']}")
        print(f"   Grid size: {grid_info['grid_size_meters']}m x {grid_info['grid_size_meters']}m")
        
        # Find nearby grids
        print("\n5. Finding nearby grids...")
        nearby = processor.find_nearby_grids(28.6139, 77.2090, radius_meters=50)
        print(f"   Found {len(nearby)} grids within 50m of 28.6139, 77.2090:")
        for i, grid in enumerate(nearby[:3]):  # Show first 3
            print(f"   {i+1}. {grid['digipin']} - {grid['distance_meters']:.1f}m away")
        
    except Exception as e:
        print(f"   Error: {e}")


# Example 3: CSV Processing
def example_csv_processing():
    print("\n=== CSV Processing Example ===")
    
    # Create sample CSV files
    import pandas as pd
    
    # Sample coordinates CSV
    coords_data = {
        'latitude': [28.6139, 19.0760, 13.0827, 22.5726],
        'longitude': [77.2090, 72.8777, 80.2707, 88.3639],
        'location': ['New Delhi', 'Mumbai', 'Chennai', 'Kolkata']
    }
    coords_df = pd.DataFrame(coords_data)
    coords_df.to_csv('sample_coordinates.csv', index=False)
    print("Created sample_coordinates.csv")
    
    try:
        # Process coordinates to DigiPin (offline)
        print("\n1. Processing coordinates to DigiPin (offline)...")
        processor = CSVProcessor(use_offline=True)
        
        def progress_callback(processed, total, success, errors):
            print(f"   Progress: {processed}/{total} - Success: {success}, Errors: {errors}")
        
        result = processor.process_coordinates_to_digipin_csv(
            input_file='sample_coordinates.csv',
            output_file='coordinates_with_digipin.csv',
            progress_callback=progress_callback
        )
        
        print(f"\n   Processing complete!")
        print(f"   Total rows: {result['total_rows']}")
        print(f"   Success rate: {result['success_rate']:.1%}")
        print(f"   Output saved to: coordinates_with_digipin.csv")
        
        # Show results
        result_df = pd.read_csv('coordinates_with_digipin.csv')
        print(f"\n   Sample results:")
        for _, row in result_df.head(2).iterrows():
            print(f"   {row['location']}: {row['latitude']}, {row['longitude']} -> {row['digipin']}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Cleanup
    try:
        os.remove('sample_coordinates.csv')
        os.remove('coordinates_with_digipin.csv')
        print("\n   Cleaned up sample files")
    except:
        pass


if __name__ == '__main__':
    print("QuantaRoute Geocoding SDK - Basic Usage Examples")
    print("=" * 50)
    
    example_online_api()
    example_offline_processing()
    example_csv_processing()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nFor more examples, check the documentation at:")
    print("https://github.com/quantaroute/quantaroute-geocoding-python")
