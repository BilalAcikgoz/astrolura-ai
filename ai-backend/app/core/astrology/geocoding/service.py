from typing import Dict, Tuple, Optional
import logging
from functools import lru_cache

from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GeocodingError(Exception):
    # Custom exception for geocoding errors
    pass

class GeocodingService:
    # Service for geocoding locations and timezone detection
    def __init__(self):
        # Initialize geocoding service with configured provider
        self.provider = settings.geocoding_provider.lower()
        self.tf = TimezoneFinder()

        # Initialize geocoder based on provider
        if self.provider == "google" and settings.google_maps_api_key:
            self.geocoder = GoogleV3(api_key=settings.google_maps_api_key)
            logger.info("Initialized Google Maps geocoding service")
        else:
            # Default to Nominatim (free)
            self.geocoder = Nominatim(user_agent="astro-fala-v1.0")
            logger.info("Initialized Nominatim geocoding service")

    @lru_cache(maxsize=1000)
    def geocode_location(self, location: str) -> Dict[str, any]:
        # Geocode a location string to get coordinates and timezone
        try:
            # Try to geocode the location
            result = self._geocode_with_retry(location)

            if result is None:
                raise GeocodingError(f"Location not found: {location}")

            # Extract coordinates
            latitude = result.latitude
            longitude = result.longitude

            # Get timezone
            timezone_str = self.tf.timezone_at(lat=latitude, lng=longitude)

            if timezone_str is None:
                # Fallback: try to guess from longitude
                timezone_str = self._guess_timezone_from_longitude(longitude)
                logger.warning(f"Could not find exact timezone, using fallback: {timezone_str}")

            # Parse address components
            address_parts = self._parse_address(result.raw.get("address", {}))

            geocode_result = {
                "city": address_parts.get("city", location.split(",")[0].strip()),
                "country": address_parts.get("country", "Unknown"),
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "timezone": timezone_str,
            }

            logger.info(f"Successfully geocoded: {location} -> {geocode_result}")
            return geocode_result

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {location}: {str(e)}")
            raise GeocodingError(f"Geocoding service error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error geocoding {location}: {str(e)}")
            raise GeocodingError(f"Failed to geocode location: {str(e)}")

    def _geocode_with_retry(self, location: str, max_retries: int = 3):
        # Geocode with retry logic
        for attempt in range(max_retries):
            try:
                result = self.geocoder.geocode(location, timeout=10)
                if result:
                    return result
            except GeocoderTimedOut:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Geocoding timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                continue

        return None

    def _parse_address(self, address: Dict) -> Dict[str, str]:
        # Parse address components from geocoding result. Different providers return different address formats
        parsed = {}

        # Try to extract city
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("municipality") or
            address.get("county") or
            address.get("state")
        )
        if city:
            parsed["city"] = city

        # Extract country
        country = address.get("country")
        if country:
            parsed["country"] = country

        return parsed

    def _guess_timezone_from_longitude(self, longitude: float) -> str:
        # Fallback: Guess timezone from longitude. This is approximate and should only be used as last resort
        # Rough estimate: 15 degrees per hour
        utc_offset = round(longitude / 15)
        utc_offset = max(-12, min(14, utc_offset))  # Clamp to valid range

        if utc_offset >= 0:
            return f"Etc/GMT-{utc_offset}"
        else:
            return f"Etc/GMT+{abs(utc_offset)}"

    def convert_to_utc(
        self,
        local_datetime: datetime,
        timezone_str: str
    ) -> datetime:
        # Convert local datetime to UTC
        try:
            # Get timezone
            tz = pytz.timezone(timezone_str)

            # Localize the naive datetime
            local_dt = tz.localize(local_datetime, is_dst=None)

            # Convert to UTC
            utc_dt = local_dt.astimezone(pytz.UTC)

            logger.debug(f"Converted {local_datetime} ({timezone_str}) to {utc_dt} (UTC)")
            return utc_dt

        except pytz.exceptions.UnknownTimeZoneError:
            logger.error(f"Unknown timezone: {timezone_str}")
            raise GeocodingError(f"Invalid timezone: {timezone_str}")
        except pytz.exceptions.AmbiguousTimeError:
            # During DST transition, time can be ambiguous
            # Choose the DST version
            local_dt = tz.localize(local_datetime, is_dst=True)
            utc_dt = local_dt.astimezone(pytz.UTC)
            logger.warning(f"Ambiguous time during DST transition, chose DST: {local_dt}")
            return utc_dt
        except pytz.exceptions.NonExistentTimeError:
            # During DST transition, time might not exist
            # Move forward by one hour
            local_dt = tz.localize(local_datetime, is_dst=False)
            utc_dt = local_dt.astimezone(pytz.UTC)
            logger.warning(f"Non-existent time during DST transition, adjusted: {local_dt}")
            return utc_dt
        except Exception as e:
            logger.error(f"Error converting to UTC: {str(e)}")
            raise GeocodingError(f"Failed to convert to UTC: {str(e)}")

    def get_timezone_offset(self, timezone_str: str, dt: datetime) -> float:
        # Get timezone offset in hours for a specific datetime
        try:
            tz = pytz.timezone(timezone_str)
            offset = tz.utcoffset(dt)
            return offset.total_seconds() / 3600
        except Exception as e:
            logger.error(f"Error getting timezone offset: {str(e)}")
            return 0.0

# Global geocoding service instance
_geocoding_service: Optional[GeocodingService] = None

def get_geocoding_service() -> GeocodingService:
    # Get or create global geocoding service instance
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service
