"""
Revolutionary Location Lookup Client

Provides administrative boundary lookup capabilities - a service that even
the government doesn't provide at this level of precision and accessibility.
"""

import requests
import time
from typing import Dict, List, Optional, Union
from .exceptions import APIError, RateLimitError, AuthenticationError, ValidationError


class LocationLookupClient:
    """
    Revolutionary Location Lookup Client
    
    Get administrative boundaries (state, division, locality, pincode) from
    coordinates or DigiPin codes. Access to 36,000+ postal boundaries across India.
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.quantaroute.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the Location Lookup client
        
        Args:
            api_key: Your QuantaRoute API key
            base_url: Base URL for the API (default: https://api.quantaroute.com)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'User-Agent': 'quantaroute-geocoding-python/2.0.0',
            'Content-Type': 'application/json'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                else:
                    response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < self.max_retries:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(
                        "Rate limit exceeded", 
                        retry_after=retry_after
                    )
                
                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError()
                
                # Handle other client/server errors
                if not response.ok:
                    try:
                        error_data = response.json()
                        message = error_data.get('message', f'HTTP {response.status_code}')
                        error_code = error_data.get('code')
                    except:
                        message = f'HTTP {response.status_code}: {response.text}'
                        error_code = None
                    
                    raise APIError(message, response.status_code, error_code)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError("Max retries exceeded")
    
    def lookup_coordinates(self, latitude: float, longitude: float) -> Dict:
        """
        🚀 REVOLUTIONARY: Get administrative boundaries from coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dict containing administrative boundary information:
            - pincode: 6-digit postal code
            - office_name: Post office name
            - division: Postal division
            - region: Postal region
            - circle: Postal circle
            - state: State name
            - coordinates: Input coordinates
            - digipin: DigiPin code for the location
            - administrative_info: Dict with country, state, division, locality, pincode, delivery, district, mean_population_density, min_population_density, max_population_density
            - confidence: Accuracy score (0.0 to 1.0)
            - source: Data source (cache, database, calculation)
            - cached: Whether result was from cache
            - response_time_ms: Response time in milliseconds
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValidationError("Latitude and longitude must be numbers")
        
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90")
        
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180")
        
        data = {
            'latitude': float(latitude),
            'longitude': float(longitude)
        }
        
        response = self._make_request('POST', '/v1/location/lookup', data)
        return response.get('data', {})
    
    def lookup_digipin(self, digipin: str) -> Dict:
        """
        🚀 REVOLUTIONARY: Get administrative boundaries from DigiPin
        
        Args:
            digipin: DigiPin code (format: XXX-XXX-XXXX)
            
        Returns:
            Dict containing administrative boundary information
        """
        if not digipin or not digipin.strip():
            raise ValidationError("DigiPin is required")
        
        # Validate DigiPin format
        import re
        digipin_pattern = re.compile(r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{4}$')
        if not digipin_pattern.match(digipin.strip()):
            raise ValidationError("Invalid DigiPin format. Expected format: XXX-XXX-XXXX")
        
        # Use API endpoint directly (accepts digipin in request body)
        data = {'digipin': digipin.strip()}
        response = self._make_request('POST', '/v1/location/lookup', data)
        return response.get('data', {})
    
    def batch_lookup(self, locations: List[Dict]) -> Dict:
        """
        🚀 REVOLUTIONARY: Batch lookup for multiple locations
        
        Args:
            locations: List of location dictionaries, each containing either:
                      - {'latitude': float, 'longitude': float}
                      - {'digipin': str}
            
        Returns:
            Dict containing batch processing results with administrative boundaries
        """
        if not locations or not isinstance(locations, list):
            raise ValidationError("Locations must be a non-empty list")
        
        if len(locations) > 100:
            raise ValidationError("Maximum 100 locations allowed per batch")
        
        # Validate and normalize locations
        normalized_locations = []
        import re
        digipin_pattern = re.compile(r'^[A-Z0-9]{3}-[A-Z0-9]{3}-[A-Z0-9]{4}$')
        
        for i, loc in enumerate(locations):
            if not isinstance(loc, dict):
                raise ValidationError(f"Location {i+1} must be a dictionary")
            
            if 'latitude' in loc and 'longitude' in loc:
                # Coordinate-based lookup
                if not isinstance(loc['latitude'], (int, float)) or not isinstance(loc['longitude'], (int, float)):
                    raise ValidationError(f"Location {i+1}: latitude and longitude must be numbers")
                if not (-90 <= loc['latitude'] <= 90):
                    raise ValidationError(f"Location {i+1}: latitude must be between -90 and 90")
                if not (-180 <= loc['longitude'] <= 180):
                    raise ValidationError(f"Location {i+1}: longitude must be between -180 and 180")
                normalized_locations.append({
                    'latitude': float(loc['latitude']),
                    'longitude': float(loc['longitude'])
                })
            elif 'digipin' in loc:
                # DigiPin-based lookup - send directly to API
                digipin = loc['digipin'].strip()
                if not digipin_pattern.match(digipin):
                    raise ValidationError(f"Location {i+1}: Invalid DigiPin format. Expected format: XXX-XXX-XXXX")
                normalized_locations.append({'digipin': digipin})
            else:
                raise ValidationError(f"Location {i+1} must contain either 'latitude'+'longitude' or 'digipin'")
        
        data = {'locations': normalized_locations}
        response = self._make_request('POST', '/v1/location/batch-lookup', data)
        return response.get('data', {})
    
    def get_statistics(self) -> Dict:
        """
        📊 Get live statistics about the Location Lookup service
        
        Returns:
            Dict containing:
            - total_boundaries: Total number of postal boundaries
            - total_states: Number of states covered
            - total_divisions: Number of postal divisions
            - cache_size: Current cache size
            - performance_metrics: Response time statistics
        """
        response = self._make_request('GET', '/v1/location/stats')
        return response.get('data', {})
    
    def get_coverage_info(self) -> Dict:
        """
        🌍 Get coverage information about the Location Lookup service
        
        Returns:
            Dict containing coverage details and service capabilities
        """
        response = self._make_request('GET', '/v1/location')
        return response
    
    def find_nearby_boundaries(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        🎯 Find nearby postal boundaries (experimental feature)
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers (default: 5.0)
            limit: Maximum number of results (default: 10, max: 50)
            
        Returns:
            List of nearby postal boundaries with distances
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValidationError("Latitude and longitude must be numbers")
        
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90")
        
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180")
        
        if radius_km <= 0 or radius_km > 100:
            raise ValidationError("Radius must be between 0 and 100 km")
        
        if limit > 50:
            limit = 50
        
        params = {
            'lat': latitude,
            'lng': longitude,
            'radius': radius_km,
            'limit': limit
        }
        
        response = self._make_request('GET', '/v1/location/nearby', params=params)
        return response.get('data', [])
