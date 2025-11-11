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
    def __init__(self):
        self.geocoding_service = get_geocoding_service()
        logger.info("BirthChartCalculator initialized")

    def _format_degree(self, decimal_degree: float) -> str:
        """
        Convert decimal degree to degrees and minutes format
        Example: 8.95 -> "8°57'"
        """
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        return f"{degrees}°{minutes}'"

    def _format_speed(self, decimal_speed: float) -> str:
        """
        Convert decimal speed to degrees, minutes, and seconds format
        Example: 0.9537 -> "00°57'13\""
        """
        # Handle negative speeds (retrograde)
        is_negative = decimal_speed < 0
        abs_speed = abs(decimal_speed)

        degrees = int(abs_speed)
        remainder = (abs_speed - degrees) * 60
        minutes = int(remainder)
        seconds = int((remainder - minutes) * 60)

        sign = "-" if is_negative else ""
        return f"{sign}{degrees:02d}°{minutes:02d}'{seconds:02d}\""

    def calculate_birth_chart(
        self,
        name: str,
        birth_date: str,
        birth_time: str,
        birth_place: str,
        house_system: str = "placidus"
    ) -> Tuple[str, BirthChartData]:
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

            # Step 5: Calculate houses FIRST
            houses, angles = self._calculate_houses(
                julian_day,
                location_info["latitude"],
                location_info["longitude"],
                house_system
            )

            # Step 6: Calculate planet positions (with house assignments)
            planets = self._calculate_planets(julian_day, houses)

            # Step 6.5: Add all angles to planets list
            # These angles are used in element/quality calculations
            planets.append(angles["ascendant"])
            planets.append(angles["descendant"])
            planets.append(angles["midheaven"])
            planets.append(angles["ic"])

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
                planets=planets,  # Already includes Ascendant and Midheaven at the end
                houses=houses,
                aspects=aspects,
                elements=elements,
                qualities=qualities
            )

            logger.info(f"Successfully calculated birth chart for {name}, chart_id: {chart_id}")
            return chart_id, chart_data

        except Exception as e:
            logger.error(f"Error calculating birth chart: {str(e)}")
            raise

    def _calculate_julian_day(self, dt: datetime) -> float:
        return swe.julday(
            dt.year,
            dt.month,
            dt.day,
            dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        )

    def _get_house_system_enum(self, house_system: str) -> HouseSystem:
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
        """
        FIX: Swiss Ephemeris cusps array is 0-indexed:
        cusps[0] = House 1, cusps[11] = House 12
        """
        house_system_enum = self._get_house_system_enum(house_system)

        result = swe.houses(
            julian_day,
            latitude,
            longitude,
            house_system_enum.value.encode('ascii')
        )

        cusps = result[0]  # 0-indexed array
        ascmc = result[1]

        # Build houses list
        houses = []
        for i in range(1, 13):
            cusp_longitude = cusps[i - 1]  # FIX: cusps[0] is House 1!
            sign_enum = get_zodiac_sign(cusp_longitude)
            degree_in_sign = get_degree_in_sign(cusp_longitude)

            house_info = HouseInfo(
                number=i,
                name=HOUSE_NAMES[i],
                cusp_longitude=round(cusp_longitude, 4),
                sign=ZODIAC_NAMES[sign_enum],
                sign_en=sign_enum.name.title(),
                sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                degree_in_sign=round(degree_in_sign, 2),
                degree_display=self._format_degree(degree_in_sign)
            )
            houses.append(house_info)

        # Ascendant and Midheaven
        asc_longitude = ascmc[0]
        mc_longitude = ascmc[1]

        asc_sign = get_zodiac_sign(asc_longitude)
        mc_sign = get_zodiac_sign(mc_longitude)

        asc_degree_in_sign = get_degree_in_sign(asc_longitude)
        mc_degree_in_sign = get_degree_in_sign(mc_longitude)

        # Calculate Descendant (opposite of Ascendant)
        dsc_longitude = (asc_longitude + 180) % 360
        dsc_sign = get_zodiac_sign(dsc_longitude)
        dsc_degree_in_sign = get_degree_in_sign(dsc_longitude)

        # Calculate IC (opposite of Midheaven)
        ic_longitude = (mc_longitude + 180) % 360
        ic_sign = get_zodiac_sign(ic_longitude)
        ic_degree_in_sign = get_degree_in_sign(ic_longitude)

        ascendant = PlanetPosition(
            name="Yukselen",
            name_en="Ascendant",
            symbol="ASC",
            longitude=round(asc_longitude, 4),
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[asc_sign],
            sign_en=asc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[asc_sign],
            degree_in_sign=round(asc_degree_in_sign, 2),
            degree_display=self._format_degree(asc_degree_in_sign),
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
            speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[mc_sign],
            sign_en=mc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[mc_sign],
            degree_in_sign=round(mc_degree_in_sign, 2),
            degree_display=self._format_degree(mc_degree_in_sign),
            house=10,
            retrograde=False,
            dignity="neutral"
        )

        descendant = PlanetPosition(
            name="Inen",
            name_en="Descendant",
            symbol="DSC",
            longitude=round(dsc_longitude, 4),
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[dsc_sign],
            sign_en=dsc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[dsc_sign],
            degree_in_sign=round(dsc_degree_in_sign, 2),
            degree_display=self._format_degree(dsc_degree_in_sign),
            house=7,
            retrograde=False,
            dignity="neutral"
        )

        ic = PlanetPosition(
            name="Gok Alti",
            name_en="Imum Coeli",
            symbol="IC",
            longitude=round(ic_longitude, 4),
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[ic_sign],
            sign_en=ic_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[ic_sign],
            degree_in_sign=round(ic_degree_in_sign, 2),
            degree_display=self._format_degree(ic_degree_in_sign),
            house=4,
            retrograde=False,
            dignity="neutral"
        )

        angles = {
            "ascendant": ascendant,
            "midheaven": midheaven,
            "descendant": descendant,
            "ic": ic
        }

        return houses, angles

    def _get_planet_house(self, planet_longitude: float, houses: List[HouseInfo]) -> int:
        """
        NEW: Determine which house a planet is in.
        A planet is in a house if it's between that house's cusp and the next house's cusp.
        """
        house_cusps = [h.cusp_longitude for h in houses]
        planet_long = planet_longitude % 360
        
        for i in range(12):
            current_cusp = house_cusps[i]
            next_cusp = house_cusps[(i + 1) % 12]
            
            # Handle wrap-around at 0°/360°
            if current_cusp < next_cusp:
                if current_cusp <= planet_long < next_cusp:
                    return i + 1
            else:
                if planet_long >= current_cusp or planet_long < next_cusp:
                    return i + 1
        
        return 1

    def _calculate_planets(self, julian_day: float, houses: List[HouseInfo]) -> List[PlanetPosition]:
        planet_positions = []
        north_node_longitude = None

        for planet_enum in Planet:
            try:
                # Skip South Node for now, we'll calculate it after getting North Node
                if planet_enum == Planet.SOUTH_NODE:
                    continue

                result, ret_flag = swe.calc_ut(julian_day, planet_enum.value)

                longitude = result[0]
                latitude = result[1]
                distance = result[2]
                speed = result[3]

                # Store North Node longitude for South Node calculation
                if planet_enum == Planet.NORTH_NODE:
                    north_node_longitude = longitude

                sign_enum = get_zodiac_sign(longitude)
                degree_in_sign = get_degree_in_sign(longitude)
                is_retrograde = speed < 0
                dignity = get_planet_dignity(planet_enum, sign_enum)

                # FIX: Calculate which house the planet is in
                planet_house = self._get_planet_house(longitude, houses)

                planet_position = PlanetPosition(
                    name=PLANET_NAMES[planet_enum],
                    name_en=planet_enum.name.title(),
                    symbol=PLANET_SYMBOLS[planet_enum],
                    longitude=round(longitude, 4),
                    latitude=round(latitude, 4),
                    distance=round(distance, 4),
                    speed=round(speed, 4),
                    speed_display=self._format_speed(speed),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 2),
                    degree_display=self._format_degree(degree_in_sign),
                    house=planet_house,
                    retrograde=is_retrograde,
                    dignity=dignity.value
                )

                planet_positions.append(planet_position)

            except Exception as e:
                logger.error(f"Error calculating {planet_enum.name}: {str(e)}")
                continue

        # Now calculate South Node (North Node + 180°)
        if north_node_longitude is not None:
            try:
                south_node_longitude = (north_node_longitude + 180) % 360
                sign_enum = get_zodiac_sign(south_node_longitude)
                degree_in_sign = get_degree_in_sign(south_node_longitude)
                planet_house = self._get_planet_house(south_node_longitude, houses)

                south_node = PlanetPosition(
                    name=PLANET_NAMES[Planet.SOUTH_NODE],
                    name_en=Planet.SOUTH_NODE.name.title().replace("_", " "),
                    symbol=PLANET_SYMBOLS[Planet.SOUTH_NODE],
                    longitude=round(south_node_longitude, 4),
                    latitude=0.0,
                    distance=0.0,
                    speed=0.0,
                    speed_display=self._format_speed(0.0),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 2),
                    degree_display=self._format_degree(degree_in_sign),
                    house=planet_house,
                    retrograde=False,
                    dignity="neutral"
                )
                planet_positions.append(south_node)
            except Exception as e:
                logger.error(f"Error calculating South Node: {str(e)}")

        return planet_positions

    def _calculate_aspects(self, planets: List[PlanetPosition]) -> List[AspectInfo]:
        aspects = []

        # Create a reverse mapping from Turkish planet name to Planet enum
        planet_name_to_enum = {name: planet for planet, name in PLANET_NAMES.items()}
        # Handle angles (they use default orbs)
        planet_name_to_enum["Yukselen"] = None  # Ascendant
        planet_name_to_enum["Inen"] = None  # Descendant
        planet_name_to_enum["Orta Gogu"] = None  # Midheaven
        planet_name_to_enum["Gok Alti"] = None  # IC

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]

                # Get planet enums for orb calculation
                planet1_enum = planet_name_to_enum.get(planet1.name)
                planet2_enum = planet_name_to_enum.get(planet2.name)

                aspect_type, orb = get_aspect(
                    planet1.longitude,
                    planet2.longitude,
                    planet1_enum,
                    planet2_enum
                )

                if aspect_type is not None:
                    aspect_info = AspectInfo(
                        planet1=planet1.name,
                        aspect=ASPECT_NAMES[aspect_type],
                        aspect_en=aspect_type.name.title().replace("_", " "),
                        aspect_symbol=ASPECT_SYMBOLS.get(aspect_type, ""),
                        planet2=planet2.name,
                        orb=round(orb, 2),
                        angle=aspect_type.value,
                        nature=ASPECT_NATURE[aspect_type]
                    )
                    aspects.append(aspect_info)

        logger.info(f"Calculated {len(aspects)} aspects")
        return aspects

    def _calculate_element_balance(self, planets: List[PlanetPosition]) -> ElementBalance:
        element_counts = {"ates": 0, "toprak": 0, "hava": 0, "su": 0}

        # Use 15 points: 10 planets + North Node + 4 angles (ASC, DSC, MC, IC)
        # Exclude: South Node only (it's the opposite of North Node)
        for planet in planets:
            # Skip South Node
            if planet.name == "Guney Node":
                continue

            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    element = ZODIAC_ELEMENTS[sign_enum]
                    element_counts[element] += 1
                    break

        total = sum(element_counts.values())
        if total == 0:
            total = 1  # Prevent division by zero

        return ElementBalance(
            fire=round(element_counts["ates"] / total * 100, 1),
            earth=round(element_counts["toprak"] / total * 100, 1),
            air=round(element_counts["hava"] / total * 100, 1),
            water=round(element_counts["su"] / total * 100, 1)
        )

    def _calculate_quality_balance(self, planets: List[PlanetPosition]) -> QualityBalance:
        quality_counts = {"oncu": 0, "sabit": 0, "degisken": 0}

        # Use 15 points: 10 planets + North Node + 4 angles (ASC, DSC, MC, IC)
        # Exclude: South Node only (it's the opposite of North Node)
        for planet in planets:
            # Skip South Node
            if planet.name == "Guney Node":
                continue

            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    quality = ZODIAC_QUALITIES[sign_enum]
                    quality_counts[quality] += 1
                    break

        total = sum(quality_counts.values())
        if total == 0:
            total = 1  # Prevent division by zero

        return QualityBalance(
            cardinal=round(quality_counts["oncu"] / total * 100, 1),
            fixed=round(quality_counts["sabit"] / total * 100, 1),
            mutable=round(quality_counts["degisken"] / total * 100, 1)
        )

# Global calculator instance
_calculator: Optional[BirthChartCalculator] = None

def get_calculator() -> BirthChartCalculator:
    global _calculator
    if _calculator is None:
        _calculator = BirthChartCalculator()
    return _calculator

