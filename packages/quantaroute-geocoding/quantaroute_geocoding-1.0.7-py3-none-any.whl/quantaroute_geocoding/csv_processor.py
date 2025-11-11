"""
CSV processing utilities for bulk geocoding operations
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Callable, Union
from tqdm import tqdm
import time

from .client import QuantaRouteClient
from .offline import OfflineProcessor
from .exceptions import ValidationError, QuantaRouteError


class CSVProcessor:
    """
    CSV processor for bulk geocoding operations
    
    Supports both online API processing and offline DigiPin operations.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        use_offline: bool = False,
        batch_size: int = 50,
        delay_between_batches: float = 1.0
    ):
        """
        Initialize CSV processor
        
        Args:
            api_key: QuantaRoute API key (required for online processing)
            use_offline: Use offline processing when possible
            batch_size: Number of records to process in each batch
            delay_between_batches: Delay in seconds between API batches
        """
        self.use_offline = use_offline
        self.batch_size = min(batch_size, 100)  # API limit
        self.delay_between_batches = delay_between_batches
        
        if not use_offline and not api_key:
            raise ValidationError("API key is required for online processing")
        
        self.client = QuantaRouteClient(api_key) if api_key else None
        self.offline_processor = OfflineProcessor() if use_offline else None
    
    def process_geocoding_csv(
        self, 
        input_file: str, 
        output_file: str,
        address_column: str = 'address',
        city_column: Optional[str] = None,
        state_column: Optional[str] = None,
        pincode_column: Optional[str] = None,
        country_column: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process CSV file for address geocoding
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            address_column: Name of address column
            city_column: Name of city column (optional)
            state_column: Name of state column (optional)
            pincode_column: Name of pincode column (optional)
            country_column: Name of country column (optional)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict containing processing statistics
        """
        if not os.path.exists(input_file):
            raise ValidationError(f"Input file not found: {input_file}")
        
        # Read CSV
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            raise ValidationError(f"Failed to read CSV file: {str(e)}")
        
        if address_column not in df.columns:
            raise ValidationError(f"Address column '{address_column}' not found in CSV")
        
        # Initialize result columns
        df['digipin'] = None
        df['latitude'] = None
        df['longitude'] = None
        df['confidence'] = None
        df['geocoding_status'] = None
        df['geocoding_error'] = None
        
        total_rows = len(df)
        processed_count = 0
        success_count = 0
        error_count = 0
        
        # Process in batches
        with tqdm(total=total_rows, desc="Geocoding addresses") as pbar:
            for start_idx in range(0, total_rows, self.batch_size):
                end_idx = min(start_idx + self.batch_size, total_rows)
                batch_df = df.iloc[start_idx:end_idx].copy()
                
                if self.client and not self.use_offline:
                    # Online API processing
                    batch_results = self._process_batch_online(
                        batch_df, 
                        address_column,
                        city_column,
                        state_column,
                        pincode_column,
                        country_column
                    )
                else:
                    # Offline processing (coordinates to DigiPin only)
                    batch_results = self._process_batch_offline_geocoding(batch_df, address_column)
                
                # Update dataframe
                for i, result in enumerate(batch_results):
                    row_idx = start_idx + i
                    if result['success']:
                        df.at[row_idx, 'digipin'] = result['data'].get('digipin')
                        coords = result['data'].get('coordinates', {})
                        df.at[row_idx, 'latitude'] = coords.get('latitude')
                        df.at[row_idx, 'longitude'] = coords.get('longitude')
                        df.at[row_idx, 'confidence'] = result['data'].get('confidence')
                        df.at[row_idx, 'geocoding_status'] = 'success'
                        success_count += 1
                    else:
                        df.at[row_idx, 'geocoding_status'] = 'error'
                        df.at[row_idx, 'geocoding_error'] = result['error']
                        error_count += 1
                    
                    processed_count += 1
                
                pbar.update(len(batch_results))
                
                if progress_callback:
                    progress_callback(processed_count, total_rows, success_count, error_count)
                
                # Delay between batches to respect rate limits
                if start_idx + self.batch_size < total_rows:
                    time.sleep(self.delay_between_batches)
        
        # Save results
        try:
            df.to_csv(output_file, index=False)
        except Exception as e:
            raise QuantaRouteError(f"Failed to save output file: {str(e)}")
        
        return {
            'total_rows': total_rows,
            'processed_rows': processed_count,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / total_rows if total_rows > 0 else 0,
            'output_file': output_file
        }
    
    def process_coordinates_to_digipin_csv(
        self,
        input_file: str,
        output_file: str,
        latitude_column: str = 'latitude',
        longitude_column: str = 'longitude',
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process CSV file to convert coordinates to DigiPin codes
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            latitude_column: Name of latitude column
            longitude_column: Name of longitude column
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict containing processing statistics
        """
        if not os.path.exists(input_file):
            raise ValidationError(f"Input file not found: {input_file}")
        
        # Read CSV
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            raise ValidationError(f"Failed to read CSV file: {str(e)}")
        
        if latitude_column not in df.columns:
            raise ValidationError(f"Latitude column '{latitude_column}' not found in CSV")
        
        if longitude_column not in df.columns:
            raise ValidationError(f"Longitude column '{longitude_column}' not found in CSV")
        
        # Initialize result columns
        df['digipin'] = None
        df['processing_status'] = None
        df['processing_error'] = None
        
        total_rows = len(df)
        processed_count = 0
        success_count = 0
        error_count = 0
        
        # Process rows
        with tqdm(total=total_rows, desc="Converting coordinates to DigiPin") as pbar:
            for idx, row in df.iterrows():
                try:
                    lat = float(row[latitude_column])
                    lon = float(row[longitude_column])
                    
                    if self.use_offline and self.offline_processor:
                        # Use offline processing
                        result = self.offline_processor.coordinates_to_digipin(lat, lon)
                        df.at[idx, 'digipin'] = result['digipin']
                    elif self.client:
                        # Use API
                        result = self.client.coordinates_to_digipin(lat, lon)
                        df.at[idx, 'digipin'] = result['digipin']
                    else:
                        raise QuantaRouteError("No processing method available")
                    
                    df.at[idx, 'processing_status'] = 'success'
                    success_count += 1
                    
                except Exception as e:
                    df.at[idx, 'processing_status'] = 'error'
                    df.at[idx, 'processing_error'] = str(e)
                    error_count += 1
                
                processed_count += 1
                pbar.update(1)
                
                if progress_callback:
                    progress_callback(processed_count, total_rows, success_count, error_count)
        
        # Save results
        try:
            df.to_csv(output_file, index=False)
        except Exception as e:
            raise QuantaRouteError(f"Failed to save output file: {str(e)}")
        
        return {
            'total_rows': total_rows,
            'processed_rows': processed_count,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / total_rows if total_rows > 0 else 0,
            'output_file': output_file
        }
    
    def process_digipin_to_coordinates_csv(
        self,
        input_file: str,
        output_file: str,
        digipin_column: str = 'digipin',
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process CSV file to convert DigiPin codes to coordinates
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            digipin_column: Name of DigiPin column
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict containing processing statistics
        """
        if not os.path.exists(input_file):
            raise ValidationError(f"Input file not found: {input_file}")
        
        # Read CSV
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            raise ValidationError(f"Failed to read CSV file: {str(e)}")
        
        if digipin_column not in df.columns:
            raise ValidationError(f"DigiPin column '{digipin_column}' not found in CSV")
        
        # Initialize result columns
        df['latitude'] = None
        df['longitude'] = None
        df['processing_status'] = None
        df['processing_error'] = None
        
        total_rows = len(df)
        processed_count = 0
        success_count = 0
        error_count = 0
        
        # Process rows
        with tqdm(total=total_rows, desc="Converting DigiPin to coordinates") as pbar:
            for idx, row in df.iterrows():
                try:
                    digipin_code = str(row[digipin_column]).strip()
                    
                    if self.use_offline and self.offline_processor:
                        # Use offline processing
                        result = self.offline_processor.digipin_to_coordinates(digipin_code)
                        coords = result['coordinates']
                        df.at[idx, 'latitude'] = coords['latitude']
                        df.at[idx, 'longitude'] = coords['longitude']
                    elif self.client:
                        # Use API
                        result = self.client.reverse_geocode(digipin_code)
                        coords = result.get('coordinates', {})
                        df.at[idx, 'latitude'] = coords.get('latitude')
                        df.at[idx, 'longitude'] = coords.get('longitude')
                    else:
                        raise QuantaRouteError("No processing method available")
                    
                    df.at[idx, 'processing_status'] = 'success'
                    success_count += 1
                    
                except Exception as e:
                    df.at[idx, 'processing_status'] = 'error'
                    df.at[idx, 'processing_error'] = str(e)
                    error_count += 1
                
                processed_count += 1
                pbar.update(1)
                
                if progress_callback:
                    progress_callback(processed_count, total_rows, success_count, error_count)
        
        # Save results
        try:
            df.to_csv(output_file, index=False)
        except Exception as e:
            raise QuantaRouteError(f"Failed to save output file: {str(e)}")
        
        return {
            'total_rows': total_rows,
            'processed_rows': processed_count,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / total_rows if total_rows > 0 else 0,
            'output_file': output_file
        }
    
    def _process_batch_online(
        self,
        batch_df: pd.DataFrame,
        address_column: str,
        city_column: Optional[str],
        state_column: Optional[str],
        pincode_column: Optional[str],
        country_column: Optional[str]
    ) -> List[Dict]:
        """Process batch using online API"""
        addresses = []
        
        for _, row in batch_df.iterrows():
            addr_data = {'address': str(row[address_column])}
            
            if city_column and city_column in batch_df.columns:
                addr_data['city'] = str(row[city_column]) if pd.notna(row[city_column]) else None
            
            if state_column and state_column in batch_df.columns:
                addr_data['state'] = str(row[state_column]) if pd.notna(row[state_column]) else None
            
            if pincode_column and pincode_column in batch_df.columns:
                addr_data['pincode'] = str(row[pincode_column]) if pd.notna(row[pincode_column]) else None
            
            if country_column and country_column in batch_df.columns:
                addr_data['country'] = str(row[country_column]) if pd.notna(row[country_column]) else None
            
            addresses.append(addr_data)
        
        try:
            batch_result = self.client.batch_geocode(addresses)
            results = []
            
            for result_item in batch_result.get('results', []):
                if 'error' in result_item.get('result', {}):
                    results.append({
                        'success': False,
                        'error': result_item['result']['error']
                    })
                else:
                    results.append({
                        'success': True,
                        'data': result_item['result']
                    })
            
            return results
            
        except Exception as e:
            # Return error for all items in batch
            return [{'success': False, 'error': str(e)} for _ in addresses]
    
    def _process_batch_offline_geocoding(
        self,
        batch_df: pd.DataFrame,
        address_column: str
    ) -> List[Dict]:
        """Process batch using offline processing (limited functionality)"""
        results = []
        
        for _, row in batch_df.iterrows():
            # Offline geocoding is not possible without coordinates
            # This would require a local geocoding database
            results.append({
                'success': False,
                'error': 'Offline address geocoding not supported. Use coordinates_to_digipin instead.'
            })
        
        return results
