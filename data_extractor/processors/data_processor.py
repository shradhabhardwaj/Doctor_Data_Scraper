# data_extractor/processors/data_processor.py

import re
from thefuzz import process
import httpx

from ..utils.config import STANDARDIZED_CLINIC_NAMES, FUZZY_MATCH_THRESHOLD
from ..utils.taxonomy import classify_specialty
from ..utils.geo_validator import get_coordinates, is_within_pune
from ..utils.logger import app_logger

class DataProcessor:
    def __init__(self, raw_data: dict, url: str):
        self.raw_data = raw_data
        self.url = url
        self.processed_data = {}

    async def process(self, geo_client: httpx.AsyncClient) -> dict | None:
        # --- KEY CHANGE: Process data even if some fields are missing ---
        address_info = self._parse_address()
        
        is_pune_doctor = False
        coords = None

        if address_info:
            is_pune_doctor, coords = await self._validate_location(address_info['full_address'], geo_client)
            if not is_pune_doctor:
                app_logger.info(f"Doctor at {self.url} appears to be outside Pune. Skipping.")
                return None
        else:
            # If we couldn't parse an address, we can't validate the location, so we must skip.
            app_logger.warning(f"Address could not be parsed for {self.url}. Skipping.")
            return None

        # --- Data Cleaning and Structuring ---
        self.processed_data['doctor_name'] = self.raw_data.get('doctor_name')
        self.processed_data['specialty_raw'] = self.raw_data.get('specialty')
        self.processed_data['specialty_classified'] = classify_specialty(self.raw_data.get('specialty'))
        self.processed_data['years_of_experience'] = self.raw_data.get('years_of_experience')
        
        clinic_name = self.raw_data.get('clinic_name')
        self.processed_data['clinic_hospital_raw'] = clinic_name
        self.processed_data['clinic_hospital_standardized'] = self._standardize_clinic_name(clinic_name)
        
        self.processed_data['complete_address'] = address_info.get('full_address')
        self.processed_data['locality'] = address_info.get('locality')
        self.processed_data['pincode'] = address_info.get('pincode')
        self.processed_data['geo_coordinates'] = coords
        
        reviews = self.raw_data.get('ratings_and_reviews', {})
        self.processed_data['ratings'] = reviews.get('overall_rating')
        self.processed_data['review_count'] = reviews.get('total_reviews')
        self.processed_data['reviews_summary'] = reviews.get('reviews_summary')
        
        self.processed_data['recommendation_percent'] = self.raw_data.get('recommendation_percent')

        self.processed_data['contact_number'] = self.raw_data.get('contact_number')
        self.processed_data['contact_email']  = self.raw_data.get('contact_email')

        self.processed_data['source_url'] = self.url

        
        
        return self.processed_data

    def _parse_address(self) -> dict | None:
        address_str = self.raw_data.get('address')
        if not address_str:
            return None

        pincode_match = re.search(r'\b(411\d{3})\b', address_str)
        pincode = pincode_match.group(1) if pincode_match else None
        
        locality_parts = address_str.split(',')
        locality = locality_parts[-2].strip() if len(locality_parts) > 1 else locality_parts[0].strip()
        
        return {
            "full_address": ' '.join(address_str.split()),
            "locality": locality,
            "pincode": pincode
        }

    async def _validate_location(self, address: str, client: httpx.AsyncClient) -> tuple[bool, dict | None]:
        if "pune" not in address.lower():
            return False, None
            
        coords = await get_coordinates(address, client)
        if coords and is_within_pune(coords['lat'], coords['lon']):
            return True, coords
        
        if not coords and "pune" in address.lower():
            return True, None

        return False, None

    def _standardize_clinic_name(self, name: str | None) -> str | None:
        if not name:
            return None
        best_match = process.extractOne(name, STANDARDIZED_CLINIC_NAMES)
        if best_match and best_match[1] >= FUZZY_MATCH_THRESHOLD:
            return best_match[0]
        return name