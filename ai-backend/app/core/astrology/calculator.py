# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import uuid
import swisseph as swe

from app.config import get_settings
from app.core.astrology.constants import (
    Planet, ZodiacSign, AspectType, HouseSystem, Dignity,
    PLANET_NAMES, PLANET_SYMBOLS, ZODIAC_NAMES, ZODIAC_SYMBOLS,
    ZODIAC_ELEMENTS, ZODIAC_QUALITIES, ASPECT_NAMES, ASPECT_SYMBOLS,
    ASPECT_NATURE, HOUSE_NAMES, HOUSE_SYSTEM_NAMES,
    get_zodiac_sign, get_degree_in_sign, get_planet_dignity, get_aspect
)
from app.core.geocoding.service import get_geocoding_service
from app.api.models.response import (
    BirthChartData, ChartInfo, LocationInfo, PlanetPosition,
    HouseInfo, AspectInfo, ElementBalance, QualityBalance
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Set Swiss Ephemeris path
swe.set_ephe_path(settings.ephe_path)

class BirthChartCalculator:
    # Calculator for natal astrology charts using Swiss Ephemeris
    def __init__(self):
        # Initialize the birth chart calculator
        self.geocoding_service = get_geocoding_service()
        logger.info("BirthChartCalculator initialized")

    def calculate_birth_chart(
        self,
        name: str,
        birth_date: str,
        birth_time: str,
        birth_place: str,
        house_system: str = "placidus"
    ) -> Tuple[str, BirthChartData]:
        # Calculate complete birth chart
        try:
            # Step 1: Geocode location
            location_info = self.geocoding_service.geocode_location(birth_place)

            # Step 2: Convert to datetime
            birth_datetime = datetime.strptime(
                f"{birth_date} {birth_time}",
                "%Y-%m-%d %H:%M"
            )

            # Step 3: Convert to UTC
            utc_datetime = self.geocoding_service.convert_to_utc(
                birth_datetime,
                location_info["timezone"]
            )

            # Step 4: Calculate Julian Day
            julian_day = self._calculate_julian_day(utc_datetime)

            # Step 5: Calculate planet positions
            planets = self._calculate_planets(julian_day)

            # Step 6: Calculate houses
            houses, angles = self._calculate_houses(
                julian_day,
                location_info["latitude"],
                location_info["longitude"],
                house_system
            )

            # Step 7: Calculate aspects
            aspects = self._calculate_aspects(planets)

            # Step 8: Calculate element and quality balance
            elements = self._calculate_element_balance(planets)
            qualities = self._calculate_quality_balance(planets)

            # Step 9: Generate chart ID
            chart_id = str(uuid.uuid4())

            # Step 10: Assemble chart data
            chart_data = BirthChartData(
                chart_info=ChartInfo(
                    name=name,
                    birth_date=birth_date,
                    birth_time=birth_time,
                    birth_datetime_local=birth_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    birth_datetime_utc=utc_datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    location=LocationInfo(**location_info),
                    house_system=HOUSE_SYSTEM_NAMES[self._get_house_system_enum(house_system)],
                    julian_day=julian_day
                ),
                planets=planets,
                houses=houses,
                aspects=aspects,
                elements=elements,
                qualities=qualities,
                ascendant=angles["ascendant"],
                midheaven=angles["midheaven"]
            )

            logger.info(f"Successfully calculated birth chart for {name}, chart_id: {chart_id}")
            return chart_id, chart_data

        except Exception as e:
            logger.error(f"Error calculating birth chart: {str(e)}")
            raise

    def _calculate_julian_day(self, dt: datetime) -> float:
        # Calculate Julian Day from UTC datetime
        return swe.julday(
            dt.year,
            dt.month,
            dt.day,
            dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        )

    def _calculate_planets(self, julian_day: float) -> List[PlanetPosition]:
        # Calculate positions of all planets
        planet_positions = []

        for planet_enum in Planet:
            try:
                # Calculate planet position
                result, ret_flag = swe.calc_ut(julian_day, planet_enum.value)

                longitude = result[0]
                latitude = result[1]
                distance = result[2]
                speed = result[3]

                # Determine zodiac sign
                sign_enum = get_zodiac_sign(longitude)
                degree_in_sign = get_degree_in_sign(longitude)

                # Check if retrograde (negative speed)
                is_retrograde = speed < 0

                # Get planet dignity
                dignity = get_planet_dignity(planet_enum, sign_enum)

                # For now, set house to 0 (will be updated after house calculation)
                planet_position = PlanetPosition(
                    name=PLANET_NAMES[planet_enum],
                    name_en=planet_enum.name.title(),
                    symbol=PLANET_SYMBOLS[planet_enum],
                    longitude=round(longitude, 4),
                    latitude=round(latitude, 4),
                    distance=round(distance, 4),
                    speed=round(speed, 4),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 2),
                    house=0,  # Will be calculated later
                    retrograde=is_retrograde,
                    dignity=dignity.value
                )

                planet_positions.append(planet_position)

            except Exception as e:
                logger.error(f"Error calculating {planet_enum.name}: {str(e)}")
                continue

        return planet_positions

    def _get_house_system_enum(self, house_system: str) -> HouseSystem:
        # Convert house system string to enum
        mapping = {
            "placidus": HouseSystem.PLACIDUS,
            "koch": HouseSystem.KOCH,
            "equal": HouseSystem.EQUAL,
            "whole_sign": HouseSystem.WHOLE_SIGN,
            "campanus": HouseSystem.CAMPANUS,
            "regiomontanus": HouseSystem.REGIOMONTANUS,
        }
        return mapping.get(house_system.lower(), HouseSystem.PLACIDUS)

    def _calculate_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        house_system: str
    ) -> Tuple[List[HouseInfo], Dict[str, PlanetPosition]]:
        # Calculate house cusps and angles
        house_system_enum = self._get_house_system_enum(house_system)

        # Calculate houses
        # Note: swe.houses returns two arrays
        # cusps: array of 13 elements (cusps[0] is unused, cusps[1-12] are house cusps)
        # ascmc: array with Ascendant, MC, ARMC, Vertex, etc.
        result = swe.houses(
            julian_day,
            latitude,
            longitude,
            house_system_enum.value.encode('ascii')
        )

        # Unpack the result tuple
        cusps = result[0]
        ascmc = result[1]

        # cusps is a tuple, we need to access elements properly
        # NOTE: cusps is 0-indexed, so cusps[0] = House 1, cusps[11] = House 12
        houses = []
        for i in range(1, 13):
            cusp_longitude = cusps[i - 1]  # cusps is 0-indexed
            sign_enum = get_zodiac_sign(cusp_longitude)
            degree_in_sign = get_degree_in_sign(cusp_longitude)

            house_info = HouseInfo(
                number=i,
                name=HOUSE_NAMES[i],
                cusp_longitude=round(cusp_longitude, 4),
                sign=ZODIAC_NAMES[sign_enum],
                sign_en=sign_enum.name.title(),
                sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                degree_in_sign=round(degree_in_sign, 2)
            )
            houses.append(house_info)

        # Calculate Ascendant and Midheaven as special positions
        asc_longitude = ascmc[0]
        mc_longitude = ascmc[1]

        asc_sign = get_zodiac_sign(asc_longitude)
        mc_sign = get_zodiac_sign(mc_longitude)

        ascendant = PlanetPosition(
            name="Yukselen",
            name_en="Ascendant",
            symbol="ASC",
            longitude=round(asc_longitude, 4),
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            sign=ZODIAC_NAMES[asc_sign],
            sign_en=asc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[asc_sign],
            degree_in_sign=round(get_degree_in_sign(asc_longitude), 2),
            house=1,
            retrograde=False,
            dignity="neutral"
        )

        midheaven = PlanetPosition(
            name="Orta Gogu",
            name_en="Midheaven",
            symbol="MC",
            longitude=round(mc_longitude, 4),
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            sign=ZODIAC_NAMES[mc_sign],
            sign_en=mc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[mc_sign],
            degree_in_sign=round(get_degree_in_sign(mc_longitude), 2),
            house=10,
            retrograde=False,
            dignity="neutral"
        )

        angles = {
            "ascendant": ascendant,
            "midheaven": midheaven
        }

        return houses, angles

    def _calculate_aspects(self, planets: List[PlanetPosition]) -> List[AspectInfo]:
        # Calculate aspects between planets
        aspects = []

        # Compare each planet with every other planet
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]

                # Get aspect
                aspect_type, orb = get_aspect(planet1.longitude, planet2.longitude)

                if aspect_type is not None:
                    aspect_info = AspectInfo(
                        planet1=planet1.name,
                        planet2=planet2.name,
                        aspect=ASPECT_NAMES[aspect_type],
                        aspect_en=aspect_type.name.title().replace("_", " "),
                        aspect_symbol=ASPECT_SYMBOLS.get(aspect_type, ""),
                        angle=aspect_type.value,
                        orb=round(orb, 2),
                        nature=ASPECT_NATURE[aspect_type]
                    )
                    aspects.append(aspect_info)

        logger.info(f"Calculated {len(aspects)} aspects")
        return aspects

    def _calculate_element_balance(self, planets: List[PlanetPosition]) -> ElementBalance:
        # Calculate distribution of elements in the chart
        element_counts = {"ates": 0, "toprak": 0, "hava": 0, "su": 0}

        # Count planets in each element
        for planet in planets[:10]:  # Only consider main 10 planets
            # Get sign from Turkish name
            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    element = ZODIAC_ELEMENTS[sign_enum]
                    element_counts[element] += 1
                    break

        total = sum(element_counts.values())

        return ElementBalance(
            fire=round(element_counts["ates"] / total * 100, 1),
            earth=round(element_counts["toprak"] / total * 100, 1),
            air=round(element_counts["hava"] / total * 100, 1),
            water=round(element_counts["su"] / total * 100, 1)
        )

    def _calculate_quality_balance(self, planets: List[PlanetPosition]) -> QualityBalance:
        # Calculate distribution of qualities (modalities) in the chart
        quality_counts = {"oncu": 0, "sabit": 0, "degisken": 0}

        # Count planets in each quality
        for planet in planets[:10]:  # Only consider main 10 planets
            # Get sign from Turkish name
            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    quality = ZODIAC_QUALITIES[sign_enum]
                    quality_counts[quality] += 1
                    break

        total = sum(quality_counts.values())

        return QualityBalance(
            cardinal=round(quality_counts["oncu"] / total * 100, 1),
            fixed=round(quality_counts["sabit"] / total * 100, 1),
            mutable=round(quality_counts["degisken"] / total * 100, 1)
        )

# Global calculator instance
_calculator: Optional[BirthChartCalculator] = None

def get_calculator() -> BirthChartCalculator:
    # Get or create global calculator instance
    global _calculator
    if _calculator is None:
        _calculator = BirthChartCalculator()
    return _calculator
