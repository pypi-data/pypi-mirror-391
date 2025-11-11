"""
QuantaRoute Geocoding API Client
"""

import requests
import time
from typing import Dict, List, Optional, Union
from .exceptions import APIError, RateLimitError, AuthenticationError, ValidationError


class QuantaRouteClient:
    """
    Client for QuantaRoute Geocoding API
    
    Provides methods to interact with the QuantaRoute Geocoding API for
    address geocoding, reverse geocoding, and DigiPin operations.
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.quantaroute.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the QuantaRoute client
        
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
    
    def geocode(
        self, 
        address: str, 
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        country: Optional[str] = None
    ) -> Dict:
        """
        Geocode an address to get DigiPin and coordinates
        
        Args:
            address: The address to geocode
            city: City name (optional)
            state: State name (optional)
            pincode: Postal code (optional)
            country: Country name (optional, defaults to India)
            
        Returns:
            Dict containing DigiPin, coordinates, and address information
        """
        if not address or not address.strip():
            raise ValidationError("Address is required")
        
        data = {
            'address': address.strip(),
            'city': city,
            'state': state,
            'pincode': pincode,
            'country': country or 'India'
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self._make_request('POST', '/v1/digipin/geocode', data)
        return response.get('data', {})
    
    def reverse_geocode(self, digipin: str) -> Dict:
        """
        Reverse geocode a DigiPin to get coordinates and address
        
        Args:
            digipin: The DigiPin code to reverse geocode
            
        Returns:
            Dict containing coordinates and address information
        """
        if not digipin or not digipin.strip():
            raise ValidationError("DigiPin is required")
        
        data = {'digipin': digipin.strip()}
        response = self._make_request('POST', '/v1/digipin/reverse', data)
        return response.get('data', {})
    
    def coordinates_to_digipin(self, latitude: float, longitude: float) -> Dict:
        """
        Convert coordinates to DigiPin
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dict containing DigiPin and coordinates
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
        
        response = self._make_request('POST', '/v1/digipin/coordinates-to-digipin', data)
        return response.get('data', {})
    
    def validate_digipin(self, digipin: str) -> Dict:
        """
        Validate a DigiPin format and check if it's a real location
        
        Args:
            digipin: The DigiPin code to validate
            
        Returns:
            Dict containing validation results
        """
        if not digipin or not digipin.strip():
            raise ValidationError("DigiPin is required")
        
        response = self._make_request('GET', f'/v1/digipin/validate/{digipin.strip()}')
        return response.get('data', {})
    
    def batch_geocode(self, addresses: List[Dict]) -> Dict:
        """
        Geocode multiple addresses in batch
        
        Args:
            addresses: List of address dictionaries
            
        Returns:
            Dict containing batch processing results
        """
        if not addresses or not isinstance(addresses, list):
            raise ValidationError("Addresses must be a non-empty list")
        
        if len(addresses) > 100:
            raise ValidationError("Maximum 100 addresses allowed per batch")
        
        # Validate each address
        for i, addr in enumerate(addresses):
            if not isinstance(addr, dict) or 'address' not in addr:
                raise ValidationError(f"Address {i+1} must be a dict with 'address' key")
        
        data = {'addresses': addresses}
        response = self._make_request('POST', '/v1/digipin/batch', data)
        return response.get('data', {})
    
    def get_usage(self) -> Dict:
        """
        Get API usage statistics
        
        Returns:
            Dict containing usage information
        """
        response = self._make_request('GET', '/v1/digipin/usage')
        return response.get('data', {})
    
    def autocomplete(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Get autocomplete suggestions for addresses
        
        Args:
            query: Search query (minimum 3 characters)
            limit: Maximum number of suggestions (default: 5, max: 10)
            
        Returns:
            List of address suggestions
        """
        if not query or len(query.strip()) < 3:
            raise ValidationError("Query must be at least 3 characters long")
        
        if limit > 10:
            limit = 10
        
        params = {
            'q': query.strip(),
            'limit': limit
        }
        
        response = self._make_request('GET', '/v1/digipin/autocomplete', params=params)
        return response.get('data', [])
    
    
    # 🚀 REVOLUTIONARY LOCATION LOOKUP METHODS
    
    def lookup_location_from_coordinates(self, latitude: float, longitude: float) -> Dict:
        """
        🚀 REVOLUTIONARY: Get administrative boundaries from coordinates
        
        This is a revolutionary service that provides administrative boundary lookup
        with precision that even government services don't offer.
        
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
    
    def lookup_location_from_digipin(self, digipin: str) -> Dict:
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
    
    def batch_location_lookup(self, locations: List[Dict]) -> Dict:
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
    
    def get_location_statistics(self) -> Dict:
        """
        📊 Get live statistics about the revolutionary Location Lookup service
        
        Returns:
            Dict containing:
            - total_boundaries: Total number of postal boundaries (36,000+)
            - total_states: Number of states covered
            - total_divisions: Number of postal divisions
            - cache_size: Current cache size
            - performance_metrics: Response time statistics
        """
        response = self._make_request('GET', '/v1/location/stats')
        return response.get('data', {})
    
    def get_health(self) -> Dict:
        """
        Get API health status
        
        Returns:
            Dict containing API health information
        """
        response = self._make_request('GET', '/health')
        return response.get('data', response)