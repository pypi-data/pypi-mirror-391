"""
Command-line interface for QuantaRoute Geocoding
"""

import click
import os
from typing import Optional

from .csv_processor import CSVProcessor
from .client import QuantaRouteClient
from .location_lookup import LocationLookupClient
from .offline import OfflineProcessor
from .exceptions import QuantaRouteError


@click.group()
@click.version_option(version="2.0.0")
def main():
    """QuantaRoute Geocoding CLI - Revolutionary location intelligence with DigiPin and administrative boundaries"""
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', help='QuantaRoute API key')
@click.option('--address-column', default='address', help='Name of address column')
@click.option('--city-column', help='Name of city column')
@click.option('--state-column', help='Name of state column')
@click.option('--pincode-column', help='Name of pincode column')
@click.option('--country-column', help='Name of country column')
@click.option('--batch-size', default=50, help='Batch size for API requests')
@click.option('--delay', default=1.0, help='Delay between batches (seconds)')
@click.option('--offline', is_flag=True, help='Use offline processing (limited functionality)')
def geocode(
    input_file: str,
    output_file: str,
    api_key: Optional[str],
    address_column: str,
    city_column: Optional[str],
    state_column: Optional[str],
    pincode_column: Optional[str],
    country_column: Optional[str],
    batch_size: int,
    delay: float,
    offline: bool
):
    """Geocode addresses from CSV file to DigiPin codes"""
    
    if not offline and not api_key:
        click.echo("Error: API key is required for online geocoding. Set QUANTAROUTE_API_KEY environment variable or use --api-key option.")
        return
    
    try:
        processor = CSVProcessor(
            api_key=api_key,
            use_offline=offline,
            batch_size=batch_size,
            delay_between_batches=delay
        )
        
        def progress_callback(processed, total, success, errors):
            click.echo(f"Progress: {processed}/{total} ({processed/total*100:.1f}%) - Success: {success}, Errors: {errors}")
        
        click.echo(f"Processing {input_file}...")
        
        result = processor.process_geocoding_csv(
            input_file=input_file,
            output_file=output_file,
            address_column=address_column,
            city_column=city_column,
            state_column=state_column,
            pincode_column=pincode_column,
            country_column=country_column,
            progress_callback=progress_callback
        )
        
        click.echo(f"\nProcessing complete!")
        click.echo(f"Total rows: {result['total_rows']}")
        click.echo(f"Successful: {result['success_count']}")
        click.echo(f"Errors: {result['error_count']}")
        click.echo(f"Success rate: {result['success_rate']:.1%}")
        click.echo(f"Output saved to: {result['output_file']}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', help='QuantaRoute API key')
@click.option('--latitude-column', default='latitude', help='Name of latitude column')
@click.option('--longitude-column', default='longitude', help='Name of longitude column')
@click.option('--offline', is_flag=True, help='Use offline processing')
def coords_to_digipin(
    input_file: str,
    output_file: str,
    api_key: Optional[str],
    latitude_column: str,
    longitude_column: str,
    offline: bool
):
    """Convert coordinates to DigiPin codes from CSV file"""
    
    if not offline and not api_key:
        click.echo("Error: API key is required for online processing. Set QUANTAROUTE_API_KEY environment variable or use --api-key option.")
        return
    
    try:
        processor = CSVProcessor(
            api_key=api_key,
            use_offline=offline
        )
        
        def progress_callback(processed, total, success, errors):
            click.echo(f"Progress: {processed}/{total} ({processed/total*100:.1f}%) - Success: {success}, Errors: {errors}")
        
        click.echo(f"Processing {input_file}...")
        
        result = processor.process_coordinates_to_digipin_csv(
            input_file=input_file,
            output_file=output_file,
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            progress_callback=progress_callback
        )
        
        click.echo(f"\nProcessing complete!")
        click.echo(f"Total rows: {result['total_rows']}")
        click.echo(f"Successful: {result['success_count']}")
        click.echo(f"Errors: {result['error_count']}")
        click.echo(f"Success rate: {result['success_rate']:.1%}")
        click.echo(f"Output saved to: {result['output_file']}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', help='QuantaRoute API key')
@click.option('--digipin-column', default='digipin', help='Name of DigiPin column')
@click.option('--offline', is_flag=True, help='Use offline processing')
def digipin_to_coords(
    input_file: str,
    output_file: str,
    api_key: Optional[str],
    digipin_column: str,
    offline: bool
):
    """Convert DigiPin codes to coordinates from CSV file"""
    
    if not offline and not api_key:
        click.echo("Error: API key is required for online processing. Set QUANTAROUTE_API_KEY environment variable or use --api-key option.")
        return
    
    try:
        processor = CSVProcessor(
            api_key=api_key,
            use_offline=offline
        )
        
        def progress_callback(processed, total, success, errors):
            click.echo(f"Progress: {processed}/{total} ({processed/total*100:.1f}%) - Success: {success}, Errors: {errors}")
        
        click.echo(f"Processing {input_file}...")
        
        result = processor.process_digipin_to_coordinates_csv(
            input_file=input_file,
            output_file=output_file,
            digipin_column=digipin_column,
            progress_callback=progress_callback
        )
        
        click.echo(f"\nProcessing complete!")
        click.echo(f"Total rows: {result['total_rows']}")
        click.echo(f"Successful: {result['success_count']}")
        click.echo(f"Errors: {result['error_count']}")
        click.echo(f"Success rate: {result['success_rate']:.1%}")
        click.echo(f"Output saved to: {result['output_file']}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


@main.command()
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', required=True, help='QuantaRoute API key')
def usage():
    """Check API usage statistics"""
    
    try:
        client = QuantaRouteClient(api_key)
        usage_data = client.get_usage()
        
        click.echo("API Usage Statistics:")
        click.echo("-" * 30)
        
        usage_info = usage_data.get('usage', {})
        click.echo(f"Current Usage: {usage_info.get('currentUsage', 0)}")
        click.echo(f"Monthly Limit: {usage_info.get('monthlyLimit', 'Unknown')}")
        click.echo(f"Tier: {usage_info.get('tier', 'Unknown')}")
        click.echo(f"Reset Date: {usage_info.get('resetDate', 'Unknown')}")
        
        rate_limit = usage_data.get('rateLimit', {})
        click.echo(f"\nRate Limit:")
        click.echo(f"Requests per minute: {rate_limit.get('limit', 'Unknown')}")
        click.echo(f"Remaining: {rate_limit.get('remaining', 'Unknown')}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', help='QuantaRoute API key')
@click.option('--offline', is_flag=True, help='Use offline processing')
def single_coord_to_digipin(latitude: float, longitude: float, api_key: Optional[str], offline: bool):
    """Convert single coordinate pair to DigiPin"""
    
    try:
        if offline:
            processor = OfflineProcessor()
            result = processor.coordinates_to_digipin(latitude, longitude)
        else:
            if not api_key:
                click.echo("Error: API key is required for online processing.")
                return
            
            client = QuantaRouteClient(api_key)
            result = client.coordinates_to_digipin(latitude, longitude)
        
        click.echo(f"Coordinates: {latitude}, {longitude}")
        click.echo(f"DigiPin: {result['digipin']}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('digipin_code')
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', help='QuantaRoute API key')
@click.option('--offline', is_flag=True, help='Use offline processing')
def single_digipin_to_coords(digipin_code: str, api_key: Optional[str], offline: bool):
    """Convert single DigiPin to coordinates"""
    
    try:
        if offline:
            processor = OfflineProcessor()
            result = processor.digipin_to_coordinates(digipin_code)
        else:
            if not api_key:
                click.echo("Error: API key is required for online processing.")
                return
            
            client = QuantaRouteClient(api_key)
            result = client.reverse_geocode(digipin_code)
        
        coords = result['coordinates']
        click.echo(f"DigiPin: {digipin_code}")
        click.echo(f"Coordinates: {coords['latitude']}, {coords['longitude']}")
        
    except QuantaRouteError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


# 🚀 REVOLUTIONARY LOCATION LOOKUP COMMANDS

@main.command()
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', required=True, help='QuantaRoute API key')
def location_lookup(latitude: float, longitude: float, api_key: str):
    """🚀 REVOLUTIONARY: Get administrative boundaries from coordinates"""
    
    try:
        client = LocationLookupClient(api_key)
        result = client.lookup_coordinates(latitude, longitude)
        
        click.echo("🚀 REVOLUTIONARY LOCATION LOOKUP RESULT")
        click.echo("=" * 50)
        click.echo(f"📍 Coordinates: {latitude}, {longitude}")
        click.echo(f"📮 Pincode: {result.get('pincode', 'N/A')}")
        click.echo(f"🏢 Office Name: {result.get('office_name', 'N/A')}")
        click.echo(f"🏛️ Division: {result.get('division', 'N/A')}")
        click.echo(f"🌍 Region: {result.get('region', 'N/A')}")
        click.echo(f"⭕ Circle: {result.get('circle', 'N/A')}")
        click.echo(f"🗺️ DigiPin: {result.get('digipin', 'N/A')}")
        
        if result.get('cached'):
            click.echo(f"⚡ Response Time: {result.get('response_time_ms', 0)}ms (cached)")
        else:
            click.echo(f"🔍 Response Time: {result.get('response_time_ms', 0)}ms (database)")
        
        click.echo("\n✨ This precision is not available from government services!")
        
    except QuantaRouteError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('digipin_code')
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', required=True, help='QuantaRoute API key')
def location_from_digipin(digipin_code: str, api_key: str):
    """🚀 REVOLUTIONARY: Get administrative boundaries from DigiPin"""
    
    try:
        client = LocationLookupClient(api_key)
        result = client.lookup_digipin(digipin_code)
        
        click.echo("🚀 REVOLUTIONARY LOCATION LOOKUP FROM DIGIPIN")
        click.echo("=" * 55)
        click.echo(f"🔢 DigiPin: {digipin_code}")
        click.echo(f"📮 Pincode: {result.get('pincode', 'N/A')}")
        click.echo(f"🏢 Office Name: {result.get('office_name', 'N/A')}")
        click.echo(f"🏛️ Division: {result.get('division', 'N/A')}")
        click.echo(f"🌍 Region: {result.get('region', 'N/A')}")
        click.echo(f"⭕ Circle: {result.get('circle', 'N/A')}")
        
        coords = result.get('coordinates', {})
        if coords:
            click.echo(f"📍 Coordinates: {coords.get('latitude', 'N/A')}, {coords.get('longitude', 'N/A')}")
        
        if result.get('cached'):
            click.echo(f"⚡ Response Time: {result.get('response_time_ms', 0)}ms (cached)")
        else:
            click.echo(f"🔍 Response Time: {result.get('response_time_ms', 0)}ms (database)")
        
        click.echo("\n✨ Administrative boundary precision that governments don't provide!")
        
    except QuantaRouteError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)


@main.command()
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', required=True, help='QuantaRoute API key')
def location_stats(api_key: str):
    """📊 Get live statistics about the revolutionary Location Lookup service"""
    
    try:
        client = LocationLookupClient(api_key)
        stats = client.get_statistics()
        
        click.echo("📊 REVOLUTIONARY LOCATION LOOKUP STATISTICS")
        click.echo("=" * 50)
        click.echo(f"🗺️ Total Boundaries: {stats.get('total_boundaries', 'N/A'):,}")
        click.echo(f"🏛️ Total States: {stats.get('total_states', 'N/A')}")
        click.echo(f"📮 Total Divisions: {stats.get('total_divisions', 'N/A')}")
        click.echo(f"⚡ Cache Size: {stats.get('cache_size', 'N/A')}")
        
        performance = stats.get('performance_metrics', {})
        if performance:
            click.echo(f"\n⚡ PERFORMANCE METRICS:")
            click.echo(f"   Average Response Time: {performance.get('avg_response_time_ms', 'N/A')}ms")
            click.echo(f"   Cache Hit Rate: {performance.get('cache_hit_rate', 'N/A')}%")
            click.echo(f"   Total Requests: {performance.get('total_requests', 'N/A'):,}")
        
        click.echo("\n🚀 Revolutionary service with 36,000+ postal boundaries!")
        click.echo("✨ Precision that even government services don't provide!")
        
    except QuantaRouteError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--api-key', envvar='QUANTAROUTE_API_KEY', required=True, help='QuantaRoute API key')
@click.option('--latitude-column', default='latitude', help='Name of latitude column')
@click.option('--longitude-column', default='longitude', help='Name of longitude column')
@click.option('--batch-size', default=50, help='Batch size for API requests')
def location_lookup_csv(
    input_file: str,
    output_file: str,
    api_key: str,
    latitude_column: str,
    longitude_column: str,
    batch_size: int
):
    """🚀 REVOLUTIONARY: Batch location lookup from CSV coordinates"""
    
    try:
        # This would need to be implemented in csv_processor.py
        click.echo("🚀 REVOLUTIONARY BATCH LOCATION LOOKUP")
        click.echo("=" * 45)
        click.echo(f"📁 Input: {input_file}")
        click.echo(f"📁 Output: {output_file}")
        click.echo(f"📊 Batch Size: {batch_size}")
        click.echo("\n⚠️ CSV Location Lookup processing coming soon!")
        click.echo("✨ Will process thousands of coordinates to administrative boundaries!")
        
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)


if __name__ == '__main__':
    main()
