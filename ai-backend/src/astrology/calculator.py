# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import uuid
import swisseph as swe

from config import app_settings
from src.astrology.constants import (
    Planet, ZodiacSign, AspectType, HouseSystem, Dignity,
    PLANET_NAMES, PLANET_SYMBOLS, ZODIAC_NAMES, ZODIAC_SYMBOLS,
    ZODIAC_ELEMENTS, ZODIAC_QUALITIES, ASPECT_NAMES, ASPECT_SYMBOLS,
    ASPECT_NATURE, HOUSE_NAMES, HOUSE_SYSTEM_NAMES, PLANET_RULERSHIPS,
    get_zodiac_sign, get_degree_in_sign, get_planet_dignity, get_aspect,
    get_triplicity_lord, get_term_lord, get_face_lord, PLANET_DIGNITIES,
    TRANSIT_ORBS
)
from src.astrology.geocoding import get_geocoding_service
from api.models import (
    BirthChartData, ChartInfo, LocationInfo, PlanetPosition,
    HouseInfo, AspectInfo, ElementBalance, QualityBalance,
    EssentialDignitiesTable, EssentialDignityRow
)

logger = logging.getLogger(__name__)

# Set Swiss Ephemeris path
swe.set_ephe_path(app_settings.ephe_path)


class BirthChartCalculator:
    def __init__(self):
        self.geocoding_service = get_geocoding_service()
        logger.info("BirthChartCalculator initialized")

    def _format_degree(self, decimal_degree: float) -> str:
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        return f"{degrees}°{minutes}'"

    def _format_speed(self, decimal_speed: float) -> str:
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
            location_info = self.geocoding_service.geocode_location(birth_place)

            birth_datetime = datetime.strptime(
                f"{birth_date} {birth_time}",
                "%Y-%m-%d %H:%M"
            )

            utc_datetime = self.geocoding_service.convert_to_utc(
                birth_datetime,
                location_info["timezone"]
            )

            julian_day = self._calculate_julian_day(utc_datetime)

            houses, angles = self._calculate_houses(
                julian_day,
                location_info["latitude"],
                location_info["longitude"],
                house_system
            )

            planets = self._calculate_planets(julian_day, houses)
            planets.append(angles["ascendant"])
            planets.append(angles["midheaven"])

            aspects = self._calculate_aspects(planets)
            elements = self._calculate_element_balance(planets)
            qualities = self._calculate_quality_balance(planets)

            sun_data = next((p for p in planets if p.name == "Güneş"), None)
            sun_longitude = sun_data.longitude if sun_data else 0.0
            dignities = self._calculate_essential_dignities(planets, sun_longitude)

            chart_id = str(uuid.uuid4())

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
                dignities=dignities
            )

            logger.info(f"Successfully calculated birth chart for {name}, chart_id: {chart_id}")
            return chart_id, chart_data

        except Exception as e:
            logger.error(f"Error calculating birth chart: {str(e)}")
            raise

    def _calculate_julian_day(self, dt: datetime) -> float:
        return swe.julday(
            dt.year, dt.month, dt.day,
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
        house_system_enum = self._get_house_system_enum(house_system)

        result = swe.houses_ex(
            julian_day, latitude, longitude,
            house_system_enum.value.encode('ascii')
        )

        cusps = result[0]
        ascmc = result[1]

        houses = []
        for i in range(1, 13):
            cusp_longitude = cusps[i - 1]
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

        asc_longitude = ascmc[0]
        mc_longitude = ascmc[1]
        asc_sign = get_zodiac_sign(asc_longitude)
        mc_sign = get_zodiac_sign(mc_longitude)
        asc_degree_in_sign = get_degree_in_sign(asc_longitude)
        mc_degree_in_sign = get_degree_in_sign(mc_longitude)

        dsc_longitude = (asc_longitude + 180) % 360
        dsc_sign = get_zodiac_sign(dsc_longitude)
        dsc_degree_in_sign = get_degree_in_sign(dsc_longitude)

        ic_longitude = (mc_longitude + 180) % 360
        ic_sign = get_zodiac_sign(ic_longitude)
        ic_degree_in_sign = get_degree_in_sign(ic_longitude)

        ascendant = PlanetPosition(
            name="Yükselen", name_en="Ascendant", symbol="ASC",
            longitude=round(asc_longitude, 4), latitude=0.0, distance=0.0,
            speed=0.0, speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[asc_sign], sign_en=asc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[asc_sign],
            degree_in_sign=round(asc_degree_in_sign, 2),
            degree_display=self._format_degree(asc_degree_in_sign),
            house=1, retrograde=False, dignity="neutral"
        )

        midheaven = PlanetPosition(
            name="Orta Gök", name_en="Midheaven", symbol="MC",
            longitude=round(mc_longitude, 4), latitude=0.0, distance=0.0,
            speed=0.0, speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[mc_sign], sign_en=mc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[mc_sign],
            degree_in_sign=round(mc_degree_in_sign, 2),
            degree_display=self._format_degree(mc_degree_in_sign),
            house=10, retrograde=False, dignity="neutral"
        )

        descendant = PlanetPosition(
            name="İnen", name_en="Descendant", symbol="DSC",
            longitude=round(dsc_longitude, 4), latitude=0.0, distance=0.0,
            speed=0.0, speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[dsc_sign], sign_en=dsc_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[dsc_sign],
            degree_in_sign=round(dsc_degree_in_sign, 2),
            degree_display=self._format_degree(dsc_degree_in_sign),
            house=7, retrograde=False, dignity="neutral"
        )

        ic = PlanetPosition(
            name="Gök Altı", name_en="Imum Coeli", symbol="IC",
            longitude=round(ic_longitude, 4), latitude=0.0, distance=0.0,
            speed=0.0, speed_display=self._format_speed(0.0),
            sign=ZODIAC_NAMES[ic_sign], sign_en=ic_sign.name.title(),
            sign_symbol=ZODIAC_SYMBOLS[ic_sign],
            degree_in_sign=round(ic_degree_in_sign, 2),
            degree_display=self._format_degree(ic_degree_in_sign),
            house=4, retrograde=False, dignity="neutral"
        )

        angles = {
            "ascendant": ascendant, "midheaven": midheaven,
            "descendant": descendant, "ic": ic
        }
        return houses, angles

    def _get_planet_house(self, planet_longitude: float, houses: List[HouseInfo]) -> int:
        house_cusps = [h.cusp_longitude for h in houses]
        planet_long = planet_longitude % 360

        for i in range(12):
            current_cusp = house_cusps[i]
            next_cusp = house_cusps[(i + 1) % 12]

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
        north_node_speed = None

        for planet_enum in Planet:
            try:
                if planet_enum == Planet.SOUTH_NODE:
                    continue

                result, ret_flag = swe.calc_ut(julian_day, planet_enum.value)
                longitude = result[0]
                latitude = result[1]
                distance = result[2]
                speed = result[3]

                if planet_enum == Planet.NORTH_NODE:
                    north_node_longitude = longitude
                    north_node_speed = speed

                sign_enum = get_zodiac_sign(longitude)
                degree_in_sign = get_degree_in_sign(longitude)
                is_retrograde = speed < 0
                dignity = get_planet_dignity(planet_enum, sign_enum)
                planet_house = self._get_planet_house(longitude, houses)

                planet_position = PlanetPosition(
                    name=PLANET_NAMES[planet_enum],
                    name_en=planet_enum.name.replace("_", " ").title(),
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

        if north_node_longitude is not None and north_node_speed is not None:
            try:
                south_node_longitude = (north_node_longitude + 180) % 360
                south_node_speed = north_node_speed
                sign_enum = get_zodiac_sign(south_node_longitude)
                degree_in_sign = get_degree_in_sign(south_node_longitude)
                planet_house = self._get_planet_house(south_node_longitude, houses)
                is_retrograde = south_node_speed < 0

                south_node = PlanetPosition(
                    name=PLANET_NAMES[Planet.SOUTH_NODE],
                    name_en=Planet.SOUTH_NODE.name.title().replace("_", " "),
                    symbol=PLANET_SYMBOLS[Planet.SOUTH_NODE],
                    longitude=round(south_node_longitude, 4),
                    latitude=0.0, distance=0.0,
                    speed=round(south_node_speed, 4),
                    speed_display=self._format_speed(south_node_speed),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 2),
                    degree_display=self._format_degree(degree_in_sign),
                    house=planet_house,
                    retrograde=is_retrograde,
                    dignity="neutral"
                )
                planet_positions.append(south_node)
            except Exception as e:
                logger.error(f"Error calculating South Node: {str(e)}")

        return planet_positions

    def _calculate_aspects(self, planets: List[PlanetPosition]) -> List[AspectInfo]:
        aspects = []
        major_aspects = {
            AspectType.CONJUNCTION, AspectType.OPPOSITION,
            AspectType.TRINE, AspectType.SQUARE, AspectType.SEXTILE
        }
        MAX_ORB = 3.15

        planet_name_to_enum = {name: planet for planet, name in PLANET_NAMES.items()}
        planet_name_to_enum["Yükselen"] = None
        planet_name_to_enum["Orta Gök"] = None

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]

                planet1_enum = planet_name_to_enum.get(planet1.name)
                planet2_enum = planet_name_to_enum.get(planet2.name)

                aspect_type, orb = get_aspect(
                    planet1.longitude, planet2.longitude,
                    planet1_enum, planet2_enum
                )

                if aspect_type is not None and aspect_type in major_aspects and orb <= MAX_ORB:
                    orb_rounded = round(orb, 2)
                    aspect_info = AspectInfo(
                        planet1=planet1.name,
                        aspect=ASPECT_NAMES[aspect_type],
                        aspect_en=aspect_type.name.title().replace("_", " "),
                        aspect_symbol=ASPECT_SYMBOLS.get(aspect_type, ""),
                        planet2=planet2.name,
                        orb=orb_rounded,
                        angle=aspect_type.value,
                        nature=ASPECT_NATURE[aspect_type]
                    )
                    aspects.append(aspect_info)

        logger.info(f"Calculated {len(aspects)} major aspects (orb < {MAX_ORB})")
        return aspects

    def _calculate_element_balance(self, planets: List[PlanetPosition]) -> ElementBalance:
        element_counts = {"ates": 0, "toprak": 0, "hava": 0, "su": 0}

        for planet in planets:
            if planet.name == "Güney Düğüm":
                continue
            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    element = ZODIAC_ELEMENTS[sign_enum]
                    element_counts[element] += 1
                    break

        total = sum(element_counts.values()) or 1
        return ElementBalance(
            fire=round(element_counts["ates"] / total * 100, 1),
            earth=round(element_counts["toprak"] / total * 100, 1),
            air=round(element_counts["hava"] / total * 100, 1),
            water=round(element_counts["su"] / total * 100, 1)
        )

    def _calculate_quality_balance(self, planets: List[PlanetPosition]) -> QualityBalance:
        quality_counts = {"oncu": 0, "sabit": 0, "degisken": 0}

        for planet in planets:
            if planet.name == "Güney Düğüm":
                continue
            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    quality = ZODIAC_QUALITIES[sign_enum]
                    quality_counts[quality] += 1
                    break

        total = sum(quality_counts.values()) or 1
        return QualityBalance(
            cardinal=round(quality_counts["oncu"] / total * 100, 1),
            fixed=round(quality_counts["sabit"] / total * 100, 1),
            mutable=round(quality_counts["degisken"] / total * 100, 1)
        )

    def _calculate_essential_dignities(self, planets: List[PlanetPosition], sun_longitude: float) -> EssentialDignitiesTable:
        sun_data = next((p for p in planets if p.name == "Güneş"), None)
        is_day_chart = sun_data and sun_data.house in [7, 8, 9, 10, 11, 12]

        main_planets = [
            Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS, Planet.MARS,
            Planet.JUPITER, Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO
        ]

        rows = []
        total_score = 0

        for planet_enum in main_planets:
            planet_name_tr = PLANET_NAMES[planet_enum]
            planet_data = next((p for p in planets if p.name == planet_name_tr), None)
            if not planet_data:
                continue

            sign_enum = get_zodiac_sign(planet_data.longitude)
            degree_in_sign = get_degree_in_sign(planet_data.longitude)

            ruler_planets = []
            exaltation_planets = []
            triplicity_planets = []
            term_planets = []
            face_planets = []
            detriment_planets = []
            fall_planets = []
            score = 0

            ruler = PLANET_RULERSHIPS.get(sign_enum)
            if ruler:
                ruler_planets.append(PLANET_SYMBOLS[ruler])
                if ruler == planet_enum:
                    score += 5

            for p, dignities in PLANET_DIGNITIES.items():
                if dignities.get(sign_enum) == Dignity.EXALTED:
                    exaltation_planets.append(PLANET_SYMBOLS[p])
                    if p == planet_enum:
                        score += 4

            triplicity_lord = get_triplicity_lord(sign_enum, is_day_chart)
            if triplicity_lord:
                triplicity_planets.append(PLANET_SYMBOLS[triplicity_lord])
                if triplicity_lord == planet_enum:
                    score += 3

            term_lord = get_term_lord(sign_enum, degree_in_sign)
            if term_lord:
                term_planets.append(PLANET_SYMBOLS[term_lord])
                if term_lord == planet_enum:
                    score += 2

            face_lord = get_face_lord(sign_enum, degree_in_sign)
            if face_lord:
                face_planets.append(PLANET_SYMBOLS[face_lord])
                if face_lord == planet_enum:
                    score += 1

            for p, dignities in PLANET_DIGNITIES.items():
                if dignities.get(sign_enum) == Dignity.DETRIMENT:
                    detriment_planets.append(PLANET_SYMBOLS[p])
                    if p == planet_enum:
                        score -= 5

            for p, dignities in PLANET_DIGNITIES.items():
                if dignities.get(sign_enum) == Dignity.FALL:
                    fall_planets.append(PLANET_SYMBOLS[p])
                    if p == planet_enum:
                        score -= 4

            row = EssentialDignityRow(
                planet=planet_name_tr, planet_en=PLANET_SYMBOLS[planet_enum],
                ruler=ruler_planets, exaltation=exaltation_planets,
                triplicity=triplicity_planets, term=term_planets,
                face=face_planets, detriment=detriment_planets,
                fall=fall_planets, score=score
            )
            rows.append(row)
            total_score += score

        return EssentialDignitiesTable(rows=rows, total_score=total_score)


_calculator: Optional[BirthChartCalculator] = None


def get_calculator() -> BirthChartCalculator:
    global _calculator
    if _calculator is None:
        _calculator = BirthChartCalculator()
    return _calculator


# Transit planets: 10 main planets + True Node
TRANSIT_PLANETS = [
    Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS, Planet.MARS,
    Planet.JUPITER, Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO,
    Planet.NORTH_NODE,
]

# One-hour delta in Julian days for applying/separating detection
_ONE_HOUR_JD = 1.0 / 24.0


class TransitCalculator:
    def __init__(self):
        self._birth_chart_calculator = BirthChartCalculator.__new__(BirthChartCalculator)
        logger.info("TransitCalculator initialized")

    def calculate_transits(
        self,
        natal_chart_data: dict,
        transit_date: str,
        transit_time: Optional[str] = None,
    ) -> dict:
        """
        Calculate transit planet positions and their aspects to natal planets.

        natal_chart_data: serialized BirthChartData dict (from chart_cache)
        transit_date: ISO date string, e.g. "2026-03-24"
        transit_time: local time string HH:MM (optional, defaults to 12:00 UT)
        Returns a dict with transit_planets and transit_aspects.
        """
        dt = datetime.strptime(transit_date, "%Y-%m-%d")

        if transit_time:
            hour, minute = map(int, transit_time.split(":"))
            tz_name = (
                natal_chart_data.get("chart_info", {})
                .get("location", {})
                .get("timezone", "UTC")
            )
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(tz_name)
                local_dt = datetime(dt.year, dt.month, dt.day, hour, minute, tzinfo=tz)
                utc_tt = local_dt.utctimetuple()
                ut_hour = utc_tt.tm_hour + utc_tt.tm_min / 60.0
            except Exception:
                ut_hour = hour + minute / 60.0
        else:
            ut_hour = 12.0

        jd = swe.julday(dt.year, dt.month, dt.day, ut_hour)

        natal_houses = natal_chart_data.get("houses", [])
        natal_planets_raw = natal_chart_data.get("planets", [])

        # Birth location for transit ASC/MC calculation
        location = natal_chart_data.get("chart_info", {}).get("location", {})
        birth_lat = location.get("latitude", 0.0)
        birth_lon = location.get("longitude", 0.0)
        house_system = natal_chart_data.get("chart_info", {}).get("house_system", "Placidus")

        transit_planets = self._calculate_transit_planets(
            jd, natal_houses, birth_lat, birth_lon, house_system
        )
        transit_aspects = self._calculate_transit_aspects(jd, transit_planets, natal_planets_raw)

        logger.info(
            f"Transit calculation for {transit_date} {transit_time or '12:00 UT'}: "
            f"{len(transit_planets)} planets, {len(transit_aspects)} aspects"
        )

        return {
            "transit_planets": transit_planets,
            "transit_aspects": transit_aspects,
        }

    # Map house system display name back to swe byte code
    _HOUSE_SYSTEM_BYTES = {
        "Placidus": b"P", "Koch": b"K", "Equal": b"E",
        "Whole Sign": b"W", "Campanus": b"C", "Regiomontanus": b"R",
    }

    def _calculate_transit_planets(
        self,
        jd: float,
        natal_houses: list,
        birth_lat: float,
        birth_lon: float,
        house_system: str,
    ) -> List[dict]:
        planets = []
        north_node_longitude = None
        north_node_speed = None

        for planet_enum in TRANSIT_PLANETS:
            try:
                result, _ = swe.calc_ut(jd, planet_enum.value)
                longitude = result[0]
                speed = result[3]

                if planet_enum == Planet.NORTH_NODE:
                    north_node_longitude = longitude
                    north_node_speed = speed

                sign_enum = get_zodiac_sign(longitude)
                degree_in_sign = get_degree_in_sign(longitude)
                is_retrograde = speed < 0
                house = self._get_natal_house(longitude, natal_houses)

                planets.append({
                    "name_tr": PLANET_NAMES[planet_enum],
                    "name_en": planet_enum.name.replace("_", " ").title(),
                    "symbol": PLANET_SYMBOLS[planet_enum],
                    "longitude": round(longitude, 4),
                    "speed": round(speed, 4),
                    "speed_display": self._format_speed(speed),
                    "sign_tr": ZODIAC_NAMES[sign_enum],
                    "sign_en": sign_enum.name.title(),
                    "degree_in_sign": round(degree_in_sign, 2),
                    "degree_display": self._format_degree(degree_in_sign),
                    "retrograde": is_retrograde,
                    "house": house,
                    "planet_enum": planet_enum,
                })
            except Exception as e:
                logger.error(f"Error calculating transit {planet_enum.name}: {e}")

        # South Node = North Node + 180°
        if north_node_longitude is not None:
            sn_lon = (north_node_longitude + 180) % 360
            sn_speed = north_node_speed or 0.0
            sign_enum = get_zodiac_sign(sn_lon)
            degree_in_sign = get_degree_in_sign(sn_lon)
            planets.append({
                "name_tr": PLANET_NAMES[Planet.SOUTH_NODE],
                "name_en": "South Node",
                "symbol": PLANET_SYMBOLS[Planet.SOUTH_NODE],
                "longitude": round(sn_lon, 4),
                "speed": round(sn_speed, 4),
                "speed_display": self._format_speed(sn_speed),
                "sign_tr": ZODIAC_NAMES[sign_enum],
                "sign_en": sign_enum.name.title(),
                "degree_in_sign": round(degree_in_sign, 2),
                "degree_display": self._format_degree(degree_in_sign),
                "retrograde": sn_speed < 0,
                "house": self._get_natal_house(sn_lon, natal_houses),
                "planet_enum": Planet.SOUTH_NODE,
            })

        # Transit ASC and MC (calculated for birth location at transit time)
        try:
            hs_byte = self._HOUSE_SYSTEM_BYTES.get(house_system, b"P")
            transit_houses = swe.houses_ex(jd, birth_lat, birth_lon, hs_byte)
            transit_ascmc = transit_houses[1]
            asc_lon = transit_ascmc[0]
            mc_lon = transit_ascmc[1]

            for name_tr, name_en, symbol, lon in [
                ("Yükselen", "Ascendant", "ASC", asc_lon),
                ("Orta Gök", "Midheaven", "MC", mc_lon),
            ]:
                sign_enum = get_zodiac_sign(lon)
                degree_in_sign = get_degree_in_sign(lon)
                planets.append({
                    "name_tr": name_tr,
                    "name_en": name_en,
                    "symbol": symbol,
                    "longitude": round(lon, 4),
                    "speed": 0.0,
                    "speed_display": self._format_speed(0.0),
                    "sign_tr": ZODIAC_NAMES[sign_enum],
                    "sign_en": sign_enum.name.title(),
                    "degree_in_sign": round(degree_in_sign, 2),
                    "degree_display": self._format_degree(degree_in_sign),
                    "retrograde": False,
                    "house": self._get_natal_house(lon, natal_houses),
                    "planet_enum": None,  # No swe planet ID for angles
                })
        except Exception as e:
            logger.error(f"Error calculating transit ASC/MC: {e}")

        return planets

    def _calculate_transit_aspects(
        self,
        jd: float,
        transit_planets: List[dict],
        natal_planets_raw: list,
    ) -> List[dict]:
        """Calculate aspects between transit planets and ALL natal points (planets + ASC/MC)."""
        aspects = []
        major_aspects = list(TRANSIT_ORBS.keys())

        for t_planet in transit_planets:
            for n_planet in natal_planets_raw:
                n_name = n_planet.get("name") if isinstance(n_planet, dict) else getattr(n_planet, "name", "")
                n_name_en = n_planet.get("name_en") if isinstance(n_planet, dict) else getattr(n_planet, "name_en", "")
                n_lon = n_planet.get("longitude") if isinstance(n_planet, dict) else getattr(n_planet, "longitude", 0.0)

                # Skip DSC and IC (redundant with ASC/MC opposition)
                if n_name in ("İnen", "Gök Altı"):
                    continue

                t_lon = t_planet["longitude"]

                for aspect_type in major_aspects:
                    angle = aspect_type.value
                    diff = self._calc_angle(t_lon, n_lon)
                    orb = abs(diff - angle)

                    if orb <= TRANSIT_ORBS[aspect_type]:
                        applying = self._is_applying(
                            jd, t_planet, t_lon, n_lon, angle
                        )

                        aspects.append({
                            "transit_planet_tr": t_planet["name_tr"],
                            "transit_planet_en": t_planet["name_en"],
                            "natal_planet_tr": n_name,
                            "natal_planet_en": n_name_en,
                            "aspect_tr": ASPECT_NAMES[aspect_type],
                            "aspect_en": aspect_type.name.replace("_", " ").title(),
                            "aspect_symbol": ASPECT_SYMBOLS.get(aspect_type, ""),
                            "angle": angle,
                            "orb": round(orb, 2),
                            "applying": applying,
                            "nature": ASPECT_NATURE[aspect_type],
                        })

        # Sort: natal planet order first, then transit planet order, then orb
        _PLANET_ORDER = [
            "Güneş", "Ay", "Merkür", "Venüs", "Mars",
            "Jüpiter", "Satürn", "Uranüs", "Neptün", "Plüton",
            "Kuzey Düğüm", "Güney Düğüm", "Yükselen", "Orta Gök",
        ]
        aspects.sort(key=lambda a: (
            _PLANET_ORDER.index(a["natal_planet_tr"]) if a["natal_planet_tr"] in _PLANET_ORDER else 99,
            _PLANET_ORDER.index(a["transit_planet_tr"]) if a["transit_planet_tr"] in _PLANET_ORDER else 99,
            a["orb"],
        ))
        return aspects

    def _is_applying(
        self,
        jd: float,
        t_planet: dict,
        transit_lon: float,
        natal_lon: float,
        aspect_angle: float,
    ) -> bool:
        """Return True if the transit planet is moving toward exact aspect (applying)."""
        planet_enum = t_planet.get("planet_enum")
        if planet_enum is None or planet_enum == Planet.SOUTH_NODE:
            # For South Node, use speed sign: if orb is decreasing
            speed = t_planet.get("speed", 0.0)
            if speed == 0.0:
                return False
            # Approximate: compute next lon from speed
            next_lon = (transit_lon + speed / 24.0) % 360
            current_orb = abs(self._calc_angle(transit_lon, natal_lon) - aspect_angle)
            next_orb = abs(self._calc_angle(next_lon, natal_lon) - aspect_angle)
            return next_orb < current_orb

        try:
            result_next, _ = swe.calc_ut(jd + _ONE_HOUR_JD, planet_enum.value)
            lon_next = result_next[0]

            current_orb = abs(self._calc_angle(transit_lon, natal_lon) - aspect_angle)
            next_orb = abs(self._calc_angle(lon_next, natal_lon) - aspect_angle)

            return next_orb < current_orb
        except Exception:
            return False

    def _get_natal_house(self, longitude: float, natal_houses: list) -> int:
        if not natal_houses:
            return 0
        house_cusps = []
        for h in natal_houses:
            cusp = h.get("cusp_longitude") if isinstance(h, dict) else getattr(h, "cusp_longitude", 0.0)
            house_cusps.append(cusp)

        lon = longitude % 360
        for i in range(12):
            current = house_cusps[i]
            nxt = house_cusps[(i + 1) % 12]
            if current < nxt:
                if current <= lon < nxt:
                    return i + 1
            else:
                if lon >= current or lon < nxt:
                    return i + 1
        return 1

    def _calc_angle(self, lon1: float, lon2: float) -> float:
        diff = abs(lon1 - lon2) % 360
        if diff > 180:
            diff = 360 - diff
        return diff

    def _format_degree(self, decimal_degree: float) -> str:
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        return f"{degrees}°{minutes:02d}'"

    def _format_speed(self, decimal_speed: float) -> str:
        is_negative = decimal_speed < 0
        abs_speed = abs(decimal_speed)
        degrees = int(abs_speed)
        remainder = (abs_speed - degrees) * 60
        minutes = int(remainder)
        seconds = int((remainder - minutes) * 60)
        sign = "-" if is_negative else ""
        return f"{sign}{degrees:02d}°{minutes:02d}'{seconds:02d}\""

_transit_calculator: Optional[TransitCalculator] = None


def get_transit_calculator() -> TransitCalculator:
    global _transit_calculator
    if _transit_calculator is None:
        _transit_calculator = TransitCalculator()
    return _transit_calculator
