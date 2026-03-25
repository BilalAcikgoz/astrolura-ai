from typing import Dict, Optional
import logging
from functools import lru_cache

from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

from config import app_settings

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    pass


class GeocodingService:
    def __init__(self):
        self.provider = app_settings.geocoding_provider.lower()
        self.tf = TimezoneFinder()

        if self.provider == "google":
            self.geocoder = GoogleV3(api_key=getattr(app_settings, "google_maps_api_key", ""))
            logger.info("Initialized Google Maps geocoding service")
        else:
            self.geocoder = Nominatim(user_agent="astrolura-ai-v1.0")
            logger.info("Initialized Nominatim geocoding service")

    @lru_cache(maxsize=1000)
    def geocode_location(self, location: str) -> Dict[str, any]:
        try:
            result = self._geocode_with_retry(location)
            if result is None:
                raise GeocodingError(f"Location not found: {location}")

            latitude = result.latitude
            longitude = result.longitude

            timezone_str = self.tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str is None:
                timezone_str = self._guess_timezone_from_longitude(longitude)
                logger.warning(f"Could not find exact timezone, using fallback: {timezone_str}")

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
        parsed = {}
        city = (
            address.get("city") or address.get("town") or
            address.get("village") or address.get("municipality") or
            address.get("county") or address.get("state")
        )
        if city:
            parsed["city"] = city
        country = address.get("country")
        if country:
            parsed["country"] = country
        return parsed

    def _guess_timezone_from_longitude(self, longitude: float) -> str:
        utc_offset = round(longitude / 15)
        utc_offset = max(-12, min(14, utc_offset))
        if utc_offset >= 0:
            return f"Etc/GMT-{utc_offset}"
        else:
            return f"Etc/GMT+{abs(utc_offset)}"

    def convert_to_utc(self, local_datetime: datetime, timezone_str: str) -> datetime:
        try:
            tz = pytz.timezone(timezone_str)
            local_dt = tz.localize(local_datetime, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.UTC)
            logger.debug(f"Converted {local_datetime} ({timezone_str}) to {utc_dt} (UTC)")
            return utc_dt
        except pytz.exceptions.UnknownTimeZoneError:
            raise GeocodingError(f"Invalid timezone: {timezone_str}")
        except pytz.exceptions.AmbiguousTimeError:
            local_dt = tz.localize(local_datetime, is_dst=True)
            return local_dt.astimezone(pytz.UTC)
        except pytz.exceptions.NonExistentTimeError:
            local_dt = tz.localize(local_datetime, is_dst=False)
            return local_dt.astimezone(pytz.UTC)
        except Exception as e:
            raise GeocodingError(f"Failed to convert to UTC: {str(e)}")

    def get_timezone_offset(self, timezone_str: str, dt: datetime) -> float:
        try:
            tz = pytz.timezone(timezone_str)
            offset = tz.utcoffset(dt)
            return offset.total_seconds() / 3600
        except Exception:
            return 0.0


_geocoding_service: Optional[GeocodingService] = None


def get_geocoding_service() -> GeocodingService:
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service
