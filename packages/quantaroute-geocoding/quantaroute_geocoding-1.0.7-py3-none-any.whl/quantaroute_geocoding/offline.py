"""
Offline DigiPin processing using the official DigiPin library
"""

import math
from typing import Dict, Tuple, Optional, List
from .exceptions import OfflineProcessingError, ValidationError

try:
    import digipin
    DIGIPIN_AVAILABLE = True
except ImportError:
    DIGIPIN_AVAILABLE = False


class OfflineProcessor:
    """
    Offline DigiPin processor using the official DigiPin library
    
    This class provides offline DigiPin operations without requiring API calls.
    Perfect for processing large datasets or when internet connectivity is limited.
    """
    
    def __init__(self):
        """Initialize the offline processor"""
        if not DIGIPIN_AVAILABLE:
            raise OfflineProcessingError(
                "DigiPin library not available. Install with: pip install digipin"
            )
    
    def coordinates_to_digipin(self, latitude: float, longitude: float) -> Dict:
        """
        Convert coordinates to DigiPin code (offline)
        
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
        
        try:
            digipin_code = digipin.encode(latitude, longitude)
            
            if not digipin_code or digipin_code == "Invalid coordinates":
                raise OfflineProcessingError("Unable to generate DigiPin from coordinates")
            
            return {
                'digipin': digipin_code,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'source': 'offline'
            }
            
        except Exception as e:
            raise OfflineProcessingError(f"Failed to generate DigiPin: {str(e)}")
    
    def digipin_to_coordinates(self, digipin_code: str) -> Dict:
        """
        Convert DigiPin code to coordinates (offline)
        
        Args:
            digipin_code: The DigiPin code to convert
            
        Returns:
            Dict containing coordinates
        """
        if not digipin_code or not digipin_code.strip():
            raise ValidationError("DigiPin code is required")
        
        try:
            result = digipin.decode(digipin_code.strip())
            
            if result == "Invalid DIGIPIN":
                raise OfflineProcessingError("Invalid DigiPin code")
            
            return {
                'digipin': digipin_code.strip(),
                'coordinates': {
                    'latitude': result[0],
                    'longitude': result[1]
                },
                'source': 'offline'
            }
            
        except Exception as e:
            raise OfflineProcessingError(f"Failed to convert DigiPin: {str(e)}")
    
    def validate_digipin(self, digipin_code: str) -> Dict:
        """
        Validate DigiPin format (offline)
        
        Args:
            digipin_code: The DigiPin code to validate
            
        Returns:
            Dict containing validation results
        """
        if not digipin_code or not digipin_code.strip():
            return {
                'isValid': False,
                'digipin': digipin_code or '',
                'errors': ['DigiPin is required'],
                'source': 'offline'
            }
        
        clean_digipin = digipin_code.strip()
        errors = []
        
        # Basic format validation
        if len(clean_digipin) < 6 or len(clean_digipin) > 20:
            errors.append('DigiPin must be between 6 and 20 characters long')
        
        # Check for valid characters
        if not all(c.isalnum() or c in '-_' for c in clean_digipin):
            errors.append('DigiPin can only contain alphanumeric characters, hyphens, and underscores')
        
        # Try to validate with DigiPin library
        is_valid = len(errors) == 0
        if is_valid:
            try:
                result = digipin.decode(clean_digipin)
                if result == "Invalid DIGIPIN":
                    is_valid = False
                    errors.append('DigiPin does not correspond to a valid location')
            except:
                is_valid = False
                errors.append('DigiPin does not correspond to a valid location')
        
        return {
            'isValid': is_valid,
            'digipin': clean_digipin,
            'errors': errors if errors else None,
            'source': 'offline'
        }
    
    def calculate_distance(
        self, 
        lat1: float, lon1: float, 
        lat2: float, lon2: float,
        unit: str = 'km'
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lon1: First coordinate pair
            lat2, lon2: Second coordinate pair
            unit: Distance unit ('km' or 'miles')
            
        Returns:
            Distance in specified unit
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius
        r = 6371 if unit == 'km' else 3956  # km or miles
        
        return c * r
    
    def get_grid_info(self, digipin_code: str) -> Dict:
        """
        Get information about the DigiPin grid
        
        Args:
            digipin_code: The DigiPin code
            
        Returns:
            Dict containing grid information
        """
        try:
            coords = self.digipin_to_coordinates(digipin_code)
            lat = coords['coordinates']['latitude']
            lon = coords['coordinates']['longitude']
            
            # Each DigiPin represents a 4x4 meter grid
            grid_size_meters = 4
            
            # Calculate approximate grid bounds
            # 1 degree latitude ≈ 111,320 meters
            # 1 degree longitude ≈ 111,320 * cos(latitude) meters
            lat_offset = grid_size_meters / 111320
            lon_offset = grid_size_meters / (111320 * math.cos(math.radians(lat)))
            
            return {
                'digipin': digipin_code,
                'center': {
                    'latitude': lat,
                    'longitude': lon
                },
                'bounds': {
                    'north': lat + lat_offset/2,
                    'south': lat - lat_offset/2,
                    'east': lon + lon_offset/2,
                    'west': lon - lon_offset/2
                },
                'grid_size_meters': grid_size_meters,
                'area_square_meters': grid_size_meters * grid_size_meters,
                'source': 'offline'
            }
            
        except Exception as e:
            raise OfflineProcessingError(f"Failed to get grid info: {str(e)}")
    
    def find_nearby_grids(
        self, 
        latitude: float, 
        longitude: float, 
        radius_meters: int = 100
    ) -> List[Dict]:
        """
        Find nearby DigiPin grids within a radius
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
            
        Returns:
            List of nearby DigiPin codes with distances
        """
        if radius_meters > 1000:  # Limit to 1km for performance
            raise ValidationError("Radius cannot exceed 1000 meters")
        
        # Calculate grid step size (4 meters per grid)
        grid_size = 4
        steps = math.ceil(radius_meters / grid_size)
        
        # 1 degree latitude ≈ 111,320 meters
        lat_step = grid_size / 111320
        lon_step = grid_size / (111320 * math.cos(math.radians(latitude)))
        
        nearby_grids = []
        
        for i in range(-steps, steps + 1):
            for j in range(-steps, steps + 1):
                test_lat = latitude + (i * lat_step)
                test_lon = longitude + (j * lon_step)
                
                # Calculate actual distance
                distance = self.calculate_distance(latitude, longitude, test_lat, test_lon) * 1000  # Convert to meters
                
                if distance <= radius_meters:
                    try:
                        result = self.coordinates_to_digipin(test_lat, test_lon)
                        nearby_grids.append({
                            'digipin': result['digipin'],
                            'coordinates': result['coordinates'],
                            'distance_meters': round(distance, 2)
                        })
                    except:
                        continue  # Skip invalid coordinates
        
        # Sort by distance and remove duplicates
        seen = set()
        unique_grids = []
        for grid in sorted(nearby_grids, key=lambda x: x['distance_meters']):
            if grid['digipin'] not in seen:
                seen.add(grid['digipin'])
                unique_grids.append(grid)
        
        return unique_grids
