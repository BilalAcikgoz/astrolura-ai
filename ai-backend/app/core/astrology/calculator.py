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
    ASPECT_NATURE, HOUSE_NAMES, HOUSE_SYSTEM_NAMES, PLANET_DIGNITIES,
    get_zodiac_sign, get_degree_in_sign, get_planet_dignity, get_aspect,
)
from app.core.astrology.dignity_tables import get_traditional_dignities
from app.core.geocoding import get_geocoding_service
from app.api.models import (
    BirthChartData, ChartInfo, LocationInfo, PlanetPosition,
    HouseInfo, AspectInfo, ElementBalance, QualityBalance, TraditionalDignityInfo
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
        Convert decimal degree to degrees and minutes format with high precision
        Example: 8.95 -> "8°57'"
        """
        degrees = int(decimal_degree)
        minutes = round((decimal_degree - degrees) * 60)
        return f"{degrees}°{minutes:02d}'"

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

            # Step 4: Calculate Julian Day with high precision
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

            # Step 6.5: Add only Ascendant and Midheaven to planets list (NOT Descendant and IC)
            planets.append(angles["ascendant"])
            planets.append(angles["midheaven"])

            # Step 7: Calculate aspects (filtered)
            aspects = self._calculate_aspects(planets)

            # Step 8: Calculate element and quality balance - FIXED
            elements = self._calculate_element_balance(planets)
            qualities = self._calculate_quality_balance(planets)

            # Step 9: Calculate traditional dignities (asaletler) with scoring
            is_day_chart = False
            try:
                # Güneş pozisyonunu 'planets' listesinden bul
                sun_position = next((p for p in planets if p.name == "Gunes"), None)
                
                if sun_position is not None:
                    # Geleneksel kural: Güneş 7-12. evler arasındaysa (ufkun üstünde) gündüz haritasıdır.
                    if 7 <= sun_position.house <= 12:
                        is_day_chart = True
                    # Aksi halde 'is_day_chart' False (Gece) olarak kalır
                    logger.info(f"Chart determined as {'DAY' if is_day_chart else 'NIGHT'} chart (Sun in house {sun_position.house}).")
                else:
                    # Bu durumun olmaması gerekir, ancak olursa logla
                    logger.error("CRITICAL: 'Gunes' not found in planet list. Cannot determine day/night chart. Defaulting to NIGHT.")
                    is_day_chart = False # Hata durumunda Gece'ye ayarla
            
            except Exception as e:
                # Beklenmedik bir hata olursa logla ve Gece'ye ayarla
                logger.error(f"Error determining day/night chart: {str(e)}. Defaulting to NIGHT.")
                is_day_chart = False # Hata durumundaki "güvenli varsayım" 'Gece' olmalı

            dignities = self._calculate_traditional_dignities(planets, is_day_chart=is_day_chart)

            # Step 10: Generate chart ID
            chart_id = str(uuid.uuid4())

            # Step 11: Assemble chart data
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
        """Calculate Julian Day with high precision"""
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
        Calculate houses with high precision
        """
        house_system_enum = self._get_house_system_enum(house_system)

        result = swe.houses_ex(
            julian_day,
            latitude,
            longitude,
            house_system_enum.value.encode('ascii')
        )

        cusps = result[0]  # 0-indexed array
        ascmc = result[1]

        # Build houses list with corrected precision
        houses = []
        for i in range(1, 13):
            cusp_longitude = cusps[i - 1]
            sign_enum = get_zodiac_sign(cusp_longitude)
            degree_in_sign = get_degree_in_sign(cusp_longitude)

            house_info = HouseInfo(
                number=i,
                name=HOUSE_NAMES[i],
                cusp_longitude=round(cusp_longitude, 6),
                sign=ZODIAC_NAMES[sign_enum],
                sign_en=sign_enum.name.title(),
                sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                degree_in_sign=round(degree_in_sign, 4),
                degree_display=self._format_degree(degree_in_sign)
            )
            houses.append(house_info)

        # Ascendant and Midheaven with corrected precision
        asc_longitude = ascmc[0]
        mc_longitude = ascmc[1]

        asc_sign = get_zodiac_sign(asc_longitude)
        mc_sign = get_zodiac_sign(mc_longitude)

        asc_degree_in_sign = get_degree_in_sign(asc_longitude)
        mc_degree_in_sign = get_degree_in_sign(mc_longitude)

        angles = {
            "ascendant": PlanetPosition(
                name="Yukselen",
                name_en="Ascendant",
                symbol="ASC",
                longitude=round(asc_longitude, 6),
                latitude=0.0,
                distance=0.0,
                speed=0.0,
                speed_display="00°00'00\"",
                sign=ZODIAC_NAMES[asc_sign],
                sign_en=asc_sign.name.title(),
                sign_symbol=ZODIAC_SYMBOLS[asc_sign],
                degree_in_sign=round(asc_degree_in_sign, 4),
                degree_display=self._format_degree(asc_degree_in_sign),
                house=1,
                retrograde=False,
                dignity="neutral"
            ),
            "midheaven": PlanetPosition(
                name="Orta Gogu",
                name_en="Midheaven",
                symbol="MC",
                longitude=round(mc_longitude, 6),
                latitude=0.0,
                distance=0.0,
                speed=0.0,
                speed_display="00°00'00\"",
                sign=ZODIAC_NAMES[mc_sign],
                sign_en=mc_sign.name.title(),
                sign_symbol=ZODIAC_SYMBOLS[mc_sign],
                degree_in_sign=round(mc_degree_in_sign, 4),
                degree_display=self._format_degree(mc_degree_in_sign),
                house=10,
                retrograde=False,
                dignity="neutral"
            )
        }

        return houses, angles

    def _get_planet_house(self, planet_longitude: float, houses: List[HouseInfo]) -> int:
        """
        Determine which house a planet is in based on its longitude
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
        north_node_data = None

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

                # Store North Node data for South Node calculation
                if planet_enum == Planet.NORTH_NODE:
                    north_node_data = {
                        'longitude': longitude,
                        'latitude': latitude,
                        'distance': distance,
                        'speed': speed
                    }

                sign_enum = get_zodiac_sign(longitude)
                degree_in_sign = get_degree_in_sign(longitude)
                is_retrograde = speed < 0
                dignity = get_planet_dignity(planet_enum, sign_enum)

                planet_house = self._get_planet_house(longitude, houses)

                planet_position = PlanetPosition(
                    name=PLANET_NAMES[planet_enum],
                    name_en=planet_enum.name.title().replace("_", " "),
                    symbol=PLANET_SYMBOLS[planet_enum],
                    longitude=round(longitude, 6),
                    latitude=round(latitude, 6),
                    distance=round(distance, 6),
                    speed=round(speed, 6),
                    speed_display=self._format_speed(speed),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 4),
                    degree_display=self._format_degree(degree_in_sign),
                    house=planet_house,
                    retrograde=is_retrograde,
                    dignity=dignity.value
                )

                planet_positions.append(planet_position)

            except Exception as e:
                logger.error(f"Error calculating {planet_enum.name}: {str(e)}")
                continue

        # Now calculate South Node (North Node + 180°) with same speed as North Node
        if north_node_data is not None:
            try:
                south_node_longitude = (north_node_data['longitude'] + 180) % 360
                sign_enum = get_zodiac_sign(south_node_longitude)
                degree_in_sign = get_degree_in_sign(south_node_longitude)
                planet_house = self._get_planet_house(south_node_longitude, houses)
                is_retrograde = south_node_speed < 0

                # South Node has the same speed as North Node (it moves with it)
                south_node = PlanetPosition(
                    name=PLANET_NAMES[Planet.SOUTH_NODE],
                    name_en="South Node",
                    symbol=PLANET_SYMBOLS[Planet.SOUTH_NODE],
                    longitude=round(south_node_longitude, 6),
                    latitude=-north_node_data['latitude'],  # Opposite latitude
                    distance=north_node_data['distance'],
                    speed=north_node_data['speed'],  # Same speed as North Node!
                    speed_display=self._format_speed(north_node_data['speed']),
                    sign=ZODIAC_NAMES[sign_enum],
                    sign_en=sign_enum.name.title(),
                    sign_symbol=ZODIAC_SYMBOLS[sign_enum],
                    degree_in_sign=round(degree_in_sign, 4),
                    degree_display=self._format_degree(degree_in_sign),
                    house=planet_house,
                    retrograde=north_node_data['speed'] < 0,
                    dignity="neutral"
                )
                planet_positions.append(south_node)
            except Exception as e:
                logger.error(f"Error calculating South Node: {str(e)}")

        return planet_positions

    def _calculate_aspects(self, planets: List[PlanetPosition]) -> List[AspectInfo]:
        """
        Calculate aspects with filtering for major aspects only
        """
        aspects = []
        
        # Only consider major aspects (similar to real astrology apps)
        MAJOR_ASPECTS = {
            AspectType.CONJUNCTION,
            AspectType.SEXTILE,
            AspectType.SQUARE,
            AspectType.TRINE,
            AspectType.OPPOSITION,
        }
        
        # Only calculate aspects between main celestial bodies
        # Exclude angles from aspect calculations or be very selective
        ASPECT_BODIES = {
            "Gunes", "Ay", "Merkur", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto",
            "Kuzey Node", "Guney Node"
        }
        
        # Special handling for angles
        ANGLE_NAMES = {"Yukselen", "Orta Gogu"}

        # Major aspects only
        major_aspects = {
            AspectType.CONJUNCTION,
            AspectType.OPPOSITION,
            AspectType.TRINE,
            AspectType.SQUARE,
            AspectType.SEXTILE
        }

        # Maximum orb for filtering
        MAX_ORB = 3.0

        # Create a reverse mapping from Turkish planet name to Planet enum
        planet_name_to_enum = {name: planet for planet, name in PLANET_NAMES.items()}

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]

                # Skip if both are angles
                if planet1.name in ANGLE_NAMES and planet2.name in ANGLE_NAMES:
                    continue

                # Get planet enums for orb calculation
                planet1_enum = planet_name_to_enum.get(planet1.name)
                planet2_enum = planet_name_to_enum.get(planet2.name)

                aspect_type, orb = get_aspect(
                    planet1.longitude,
                    planet2.longitude,
                    planet1_enum,
                    planet2_enum
                )

                # Only include major aspects with orb <= 3.0 degrees
                if aspect_type is not None and aspect_type in MAJOR_ASPECTS:
                    # Maximum orb is 3.0 degrees for all aspects
                    max_orb = 3.0

                    if orb <= max_orb:
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

        logger.info(f"Calculated {len(aspects)} major aspects")
        return aspects

    def _calculate_element_balance(self, planets: List[PlanetPosition]) -> ElementBalance:
        """
        Calculate element balance using main 10 planets + Ascendant
        Each gets 1 point for their sign's element
        """
        element_counts = {"ates": 0, "toprak": 0, "hava": 0, "su": 0}
        
        # Count these: Sun through Pluto + Ascendant 
        COUNTABLE_PLANETS = {
            "Gunes", "Ay", "Merkur", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto",
            "Yukselen"  # Include Ascendant
        }
        
        for planet in planets:
            if planet.name not in COUNTABLE_PLANETS:
                continue

            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    element = ZODIAC_ELEMENTS[sign_enum]
                    element_counts[element] += 1
                    break

        total = sum(element_counts.values())
        if total == 0:
            total = 1  # Prevent division by zero

        # Round to 1 decimal but ensure they sum to 100%
        percentages = {}
        raw_percentages = {k: (v / total * 100) for k, v in element_counts.items()}
        
        # Round all but last
        running_total = 0
        for i, (k, v) in enumerate(raw_percentages.items()):
            if i < len(raw_percentages) - 1:
                percentages[k] = round(v, 1)
                running_total += percentages[k]
            else:
                # Last one gets the remainder to ensure sum = 100
                percentages[k] = round(100 - running_total, 1)

        return ElementBalance(
            fire=percentages["ates"],
            earth=percentages["toprak"],
            air=percentages["hava"],
            water=percentages["su"]
        )

    def _calculate_quality_balance(self, planets: List[PlanetPosition]) -> QualityBalance:
        """
        Calculate quality balance using main 10 planets + Ascendant
        """
        quality_counts = {"oncu": 0, "sabit": 0, "degisken": 0}
        
        # Count these: Sun through Pluto + Ascendant
        COUNTABLE_PLANETS = {
            "Gunes", "Ay", "Merkur", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto",
            "Yukselen"  # Include Ascendant
        }
        
        for planet in planets:
            if planet.name not in COUNTABLE_PLANETS:
                continue

            for sign_enum, sign_name in ZODIAC_NAMES.items():
                if sign_name == planet.sign:
                    quality = ZODIAC_QUALITIES[sign_enum]
                    quality_counts[quality] += 1
                    break

        total = sum(quality_counts.values())
        if total == 0:
            total = 1  # Prevent division by zero

        # Round to 1 decimal but ensure they sum to 100%
        percentages = {}
        raw_percentages = {k: (v / total * 100) for k, v in quality_counts.items()}
        
        # Round all but last
        running_total = 0
        for i, (k, v) in enumerate(raw_percentages.items()):
            if i < len(raw_percentages) - 1:
                percentages[k] = round(v, 1)
                running_total += percentages[k]
            else:
                # Last one gets the remainder to ensure sum = 100
                percentages[k] = round(100 - running_total, 1)

        return QualityBalance(
            cardinal=percentages["oncu"],
            fixed=percentages["sabit"],
            mutable=percentages["degisken"]
        )

    def _calculate_traditional_dignities(
        self, 
        planets: List[PlanetPosition], 
        is_day_chart: bool
    ) -> List[TraditionalDignityInfo]:
        """
        Geleneksel asaletleri (asaletler) uygun puanlama sistemi ve 
        gündüz/gece üçlü yöneticileri ile doğru bir şekilde hesaplar.
        
        Hata Düzeltmesi: Bu versiyon, dignity_tables'daki modern gezegen 
        girdilerini (Uranus, Neptun, Pluto) yok sayarak, 
        "Zarar", "Düşüş" ve "Yücelme" için SADECE geleneksel yöneticileri 
        getiren manuel haritalar kullanır.
        """
        dignities_list = []
        dignity_tables = get_traditional_dignities()

        # Gezegen isimlerini ("Gunes") sembollere ("Sun" veya "☉" - constants dosyanızda ne varsa)
        # dönüştürmek için harita
        name_to_symbol = {
            PLANET_NAMES[p_enum]: PLANET_SYMBOLS[p_enum]
            for p_enum in PLANET_NAMES
            if p_enum in PLANET_SYMBOLS
        }

        # --- YENİ (DÜZELTİLMİŞ) BÖLÜM: Geleneksel Haritalar ---
        # Otomatik haritalama modern gezegenler yüzünden (örn: Aslan Zarar -> Uranüs) 
        # hatalı sonuç veriyordu. Bu haritalar SADECE geleneksel yöneticileri kullanır.
        
        # Geleneksel Yücelme (Exaltation) Haritası
        sign_to_exaltation_traditional = {
            "Koc": "Gunes",
            "Boga": "Ay",
            "Basak": "Merkur",
            "Balik": "Venus",
            "Oglak": "Mars",
            "Yengec": "Jupiter",
            "Terazi": "Saturn"
        }
        
        # Geleneksel Zarar (Detriment) Haritası
        sign_to_detriment_traditional = {
            "Kova": "Gunes",
            "Oglak": "Ay",
            "Yay": "Merkur",
            "Balik": "Merkur",
            "Koc": "Venus",
            "Akrep": "Venus",
            "Terazi": "Mars",
            "Boga": "Mars",
            "Ikizler": "Jupiter",
            "Basak": "Jupiter",
            "Yengec": "Saturn",
            "Aslan": "Saturn"
        }
        
        # Geleneksel Düşüş (Fall) Haritası
        sign_to_fall_traditional = {
            "Terazi": "Gunes",
            "Akrep": "Ay",
            "Balik": "Merkur",
            "Basak": "Venus",
            "Yengec": "Mars",
            "Oglak": "Jupiter",
            "Koc": "Saturn"
        }
        # --- YENİ BÖLÜM SONU ---

        # Geleneksel astrolojide sadece 7 gezegen puan alır.
        TRADITIONAL_PLANETS_FOR_SCORING = {
            "Gunes", "Ay", "Merkur", "Venus", "Mars", "Jupiter", "Saturn"
        }
        
        # Modern gezegenler dahil olmak üzere bu gezegenler için tabloyu oluştururuz
        PLANETS_TO_DISPLAY = {
            "Gunes", "Ay", "Merkur", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto"
        }
        
        for planet in planets:
            if planet.name not in PLANETS_TO_DISPLAY:
                continue
            
            planet_name = planet.name
            planet_sign = planet.sign
            planet_degree = planet.degree_in_sign
            
            score = 0
            dignity_details = {
                "ruler": None,
                "exaltation": None, 
                "triplicity": None,
                "term": None,
                "face": None,
                "detriment": None,
                "fall": None
            }
            
            # 1. Yönetici (Ruler) (+5) - Bu zaten geleneksel listeyi kullanıyordu
            ruler_name = dignity_tables.rulerships.get(planet_sign)
            dignity_details["ruler"] = name_to_symbol.get(ruler_name)
            if ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score += 5
            
            # 2. Yücelme (Exaltation) (+4) - DÜZELTİLDİ
            exaltation_ruler_name = sign_to_exaltation_traditional.get(planet_sign) # <-- Düzeltilmiş haritayı kullan
            dignity_details["exaltation"] = name_to_symbol.get(exaltation_ruler_name)
            if exaltation_ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score += 4
            
            # 3. Üçlü (Triplicity) (+3)
            triplicity_ruler_name = dignity_tables.get_triplicity_ruler(planet_sign, is_day_chart)
            dignity_details["triplicity"] = name_to_symbol.get(triplicity_ruler_name)
            if triplicity_ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score += 3
            
            # 4. Terim (Term) (+2)
            term_ruler_name = dignity_tables.get_term_ruler(planet_sign, planet_degree)
            dignity_details["term"] = name_to_symbol.get(term_ruler_name)
            if term_ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score += 2
            
            # 5. Dekan (Face) (+1)
            face_ruler_name = dignity_tables.get_face_ruler(planet_sign, planet_degree)
            dignity_details["face"] = name_to_symbol.get(face_ruler_name)
            if face_ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score += 1
            
            # 6. Zarar (Detriment) (-5) - DÜZELTİLDİ
            detriment_ruler_name = sign_to_detriment_traditional.get(planet_sign) # <-- Düzeltilmiş haritayı kullan
            dignity_details["detriment"] = name_to_symbol.get(detriment_ruler_name)
            if detriment_ruler_name == planet_name and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                # Düzeltme: Puanlama sadece gezegenin kendisi zarardaysa yapılır.
                # Önceki kod bunu yanlışlıkla yöneticiye bakarak yapıyordu.
                if dignity_tables.is_in_detriment(planet_name, planet_sign):
                    score -= 5
            
            # 7. Düşüş (Fall) (-4) - DÜZELTİLDİ
            fall_ruler_name = sign_to_fall_traditional.get(planet_sign) # <-- Düzeltilmiş haritayı kullan
            dignity_details["fall"] = name_to_symbol.get(fall_ruler_name)
            if dignity_tables.is_in_fall(planet_name, planet_sign) and planet_name in TRADITIONAL_PLANETS_FOR_SCORING:
                score -= 4
            
            # Create dignity info
            dignity_info = TraditionalDignityInfo(
                planet=planet.name,
                planet_symbol=planet.symbol, # Bu, 'constants' dosyanızdan gelir (örn: "Sun" veya "☉")
                ruler=dignity_details["ruler"],
                exaltation=dignity_details["exaltation"],
                triplicity=dignity_details["triplicity"],
                term=dignity_details["term"],
                face=dignity_details["face"],
                detriment=dignity_details["detriment"],
                fall=dignity_details["fall"],
                score=score
            )
            dignities_list.append(dignity_info)
        
        return dignities_list

# Global calculator instance
_calculator: Optional[BirthChartCalculator] = None

def get_calculator() -> BirthChartCalculator:
    global _calculator
    if _calculator is None:
        _calculator = BirthChartCalculator()
    return _calculator