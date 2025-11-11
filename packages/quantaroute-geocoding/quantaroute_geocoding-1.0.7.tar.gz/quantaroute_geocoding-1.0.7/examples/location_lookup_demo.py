#!/usr/bin/env python3
"""
🚀 Revolutionary Location Lookup API Demo

This example showcases the groundbreaking Location Lookup API that provides
administrative boundary information with precision that even government 
services don't offer.

Features demonstrated:
- Single coordinate to administrative boundaries
- DigiPin to administrative boundaries  
- Batch processing multiple locations
- Live statistics and performance metrics
- Service coverage information
"""

import os
import time
from quantaroute_geocoding import QuantaRouteClient, LocationLookupClient

def main():
    # Get API key from environment or prompt user
    api_key = os.getenv('QUANTAROUTE_API_KEY')
    if not api_key:
        api_key = input("Enter your QuantaRoute API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return

    print("🚀 REVOLUTIONARY LOCATION LOOKUP API DEMO")
    print("=" * 60)
    print("✨ Administrative boundary lookup with government-level precision!")
    print()

    # Initialize clients
    client = QuantaRouteClient(api_key=api_key)
    location_client = LocationLookupClient(api_key=api_key)

    # Demo 1: Single coordinate lookup
    print("📍 DEMO 1: Single Coordinate Lookup")
    print("-" * 40)
    
    # Delhi coordinates (India Gate area)
    lat, lng = 28.6139, 77.2090
    print(f"Looking up coordinates: {lat}, {lng}")
    
    try:
        start_time = time.time()
        result = client.lookup_location_from_coordinates(lat, lng)
        end_time = time.time()
        
        print(f"🎯 RESULTS:")
        print(f"   📮 Pincode: {result.get('pincode', 'N/A')}")
        print(f"   🏢 Office Name: {result.get('office_name', 'N/A')}")
        print(f"   🏛️ Division: {result.get('division', 'N/A')}")
        print(f"   🌍 Region: {result.get('region', 'N/A')}")
        print(f"   ⭕ Circle: {result.get('circle', 'N/A')}")
        print(f"   🗺️ DigiPin: {result.get('digipin', 'N/A')}")
        
        if result.get('cached'):
            print(f"   ⚡ Response Time: {result.get('response_time_ms', 0)}ms (cached)")
        else:
            print(f"   🔍 Response Time: {result.get('response_time_ms', 0)}ms (database)")
        
        print(f"   🕒 Total Time: {(end_time - start_time) * 1000:.1f}ms")
        print("   ✨ This precision is not available from government services!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

    # Demo 2: DigiPin to boundaries
    print("🔢 DEMO 2: DigiPin to Administrative Boundaries")
    print("-" * 50)
    
    digipin = "39J-438-TJC7"  # Delhi area DigiPin
    print(f"Looking up DigiPin: {digipin}")
    
    try:
        start_time = time.time()
        result = location_client.lookup_digipin(digipin)
        end_time = time.time()
        
        print(f"🎯 RESULTS:")
        print(f"   📮 Pincode: {result.get('pincode', 'N/A')}")
        print(f"   🏢 Office Name: {result.get('office_name', 'N/A')}")
        print(f"   🏛️ Division: {result.get('division', 'N/A')}")
        print(f"   🌍 Region: {result.get('region', 'N/A')}")
        print(f"   ⭕ Circle: {result.get('circle', 'N/A')}")
        
        coords = result.get('coordinates', {})
        if coords:
            print(f"   📍 Coordinates: {coords.get('latitude', 'N/A')}, {coords.get('longitude', 'N/A')}")
        
        print(f"   🕒 Total Time: {(end_time - start_time) * 1000:.1f}ms")
        print("   ✨ Administrative boundary precision that governments don't provide!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

    # Demo 3: Batch processing
    print("📊 DEMO 3: Batch Location Lookup")
    print("-" * 35)
    
    locations = [
        {"latitude": 28.6139, "longitude": 77.2090},  # Delhi
        {"latitude": 19.0760, "longitude": 72.8777},  # Mumbai
        {"latitude": 12.9716, "longitude": 77.5946},  # Bangalore
        {"digipin": "39J-438-TJC7"}                   # Delhi DigiPin
    ]
    
    print(f"Processing {len(locations)} locations in batch...")
    
    try:
        start_time = time.time()
        results = location_client.batch_lookup(locations)
        end_time = time.time()
        
        print(f"🎯 BATCH RESULTS:")
        print(f"   📊 Total Processed: {results.get('total_processed', 0)}")
        print(f"   ✅ Successful: {results.get('successful', 0)}")
        print(f"   ❌ Failed: {results.get('failed', 0)}")
        print(f"   🕒 Total Time: {(end_time - start_time) * 1000:.1f}ms")
        print(f"   ⚡ Avg Time per Location: {((end_time - start_time) * 1000) / len(locations):.1f}ms")
        
        # Show first few results
        batch_results = results.get('results', [])
        for i, result in enumerate(batch_results[:2]):
            print(f"\n   📍 Location {i+1}:")
            print(f"      Pincode: {result.get('pincode', 'N/A')}")
            print(f"      Office: {result.get('office_name', 'N/A')}")
            print(f"      Division: {result.get('division', 'N/A')}")
        
        if len(batch_results) > 2:
            print(f"   ... and {len(batch_results) - 2} more results")
        
        print("   🚀 Batch processing with revolutionary precision!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

    # Demo 4: Live statistics
    print("📈 DEMO 4: Live Service Statistics")
    print("-" * 35)
    
    try:
        stats = location_client.get_statistics()
        
        print(f"🎯 REVOLUTIONARY SERVICE STATS:")
        print(f"   🗺️ Total Boundaries: {stats.get('total_boundaries', 'N/A'):,}")
        print(f"   🏛️ Total States: {stats.get('total_states', 'N/A')}")
        print(f"   📮 Total Divisions: {stats.get('total_divisions', 'N/A')}")
        print(f"   ⚡ Cache Size: {stats.get('cache_size', 'N/A')}")
        
        performance = stats.get('performance_metrics', {})
        if performance:
            print(f"\n   ⚡ PERFORMANCE METRICS:")
            print(f"      Avg Response Time: {performance.get('avg_response_time_ms', 'N/A')}ms")
            print(f"      Cache Hit Rate: {performance.get('cache_hit_rate', 'N/A')}%")
            print(f"      Total Requests: {performance.get('total_requests', 'N/A'):,}")
        
        print("\n   🚀 Revolutionary service with 36,000+ postal boundaries!")
        print("   ✨ Precision that even government services don't provide!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

    # Demo 5: Coverage information
    print("🌍 DEMO 5: Service Coverage Information")
    print("-" * 40)
    
    try:
        coverage = location_client.get_coverage_info()
        
        print(f"🎯 SERVICE COVERAGE:")
        print(f"   Message: {coverage.get('message', 'N/A')}")
        print(f"   USP: {coverage.get('unique_selling_point', 'N/A')}")
        
        endpoints = coverage.get('endpoints', {})
        if endpoints:
            print(f"\n   📡 AVAILABLE ENDPOINTS:")
            for name, endpoint in endpoints.items():
                print(f"      {name}: {endpoint}")
        
        live_stats = coverage.get('live_statistics', {})
        if live_stats:
            print(f"\n   📊 LIVE STATISTICS:")
            print(f"      Boundaries: {live_stats.get('total_boundaries', 'N/A'):,}")
            print(f"      States: {live_stats.get('total_states', 'N/A')}")
            print(f"      Cache: {live_stats.get('cache_size', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("🚀 You've experienced the revolutionary Location Lookup API!")
    print("✨ Administrative boundary precision that governments don't provide!")
    print("📍 36,000+ postal boundaries at your fingertips!")
    print("⚡ Sub-100ms performance with intelligent caching!")
    print()
    print("🌟 Ready to revolutionize your location intelligence applications!")


if __name__ == "__main__":
    main()
