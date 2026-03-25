# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, List, Tuple
import swisseph as swe

# Swiss Ephemeris Planet IDs
class Planet(Enum):
    # Planet enumeration with Swiss Ephemeris IDs
    SUN = swe.SUN
    MOON = swe.MOON
    MERCURY = swe.MERCURY
    VENUS = swe.VENUS
    MARS = swe.MARS
    JUPITER = swe.JUPITER
    SATURN = swe.SATURN
    URANUS = swe.URANUS
    NEPTUNE = swe.NEPTUNE
    PLUTO = swe.PLUTO
    NORTH_NODE = swe.TRUE_NODE
    SOUTH_NODE = -1  # Calculated as North Node + 180°
    # CHIRON = swe.CHIRON  # Requires seas_18.se1 file

# Planet symbols and names
PLANET_SYMBOLS = {
    Planet.SUN: "☉",
    Planet.MOON: "☽",
    Planet.MERCURY: "☿",
    Planet.VENUS: "♀",
    Planet.MARS: "♂",
    Planet.JUPITER: "♃",
    Planet.SATURN: "♄",
    Planet.URANUS: "♅",
    Planet.NEPTUNE: "♆",
    Planet.PLUTO: "♇",
    Planet.NORTH_NODE: "☊",
    Planet.SOUTH_NODE: "☋",
    # Planet.CHIRON: "⚷",
}

PLANET_NAMES = {
    Planet.SUN: "Güneş",
    Planet.MOON: "Ay",
    Planet.MERCURY: "Merkür",
    Planet.VENUS: "Venüs",
    Planet.MARS: "Mars",
    Planet.JUPITER: "Jüpiter",
    Planet.SATURN: "Satürn",
    Planet.URANUS: "Uranüs",
    Planet.NEPTUNE: "Neptün",
    Planet.PLUTO: "Plüton",
    Planet.NORTH_NODE: "Kuzey Düğüm",
    Planet.SOUTH_NODE: "Güney Düğüm",
    # Planet.CHIRON: "Chiron",
}

# Zodiac Signs
class ZodiacSign(Enum):
    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11

ZODIAC_NAMES = {
    ZodiacSign.ARIES: "Koç",
    ZodiacSign.TAURUS: "Boğa",
    ZodiacSign.GEMINI: "İkizler",
    ZodiacSign.CANCER: "Yengeç",
    ZodiacSign.LEO: "Aslan",
    ZodiacSign.VIRGO: "Başak",
    ZodiacSign.LIBRA: "Terazi",
    ZodiacSign.SCORPIO: "Akrep",
    ZodiacSign.SAGITTARIUS: "Yay",
    ZodiacSign.CAPRICORN: "Oğlak",
    ZodiacSign.AQUARIUS: "Kova",
    ZodiacSign.PISCES: "Balık",
}

ZODIAC_SYMBOLS = {
    ZodiacSign.ARIES: "Aries",
    ZodiacSign.TAURUS: "Taurus",
    ZodiacSign.GEMINI: "Gemini",
    ZodiacSign.CANCER: "Cancer",
    ZodiacSign.LEO: "Leo",
    ZodiacSign.VIRGO: "Virgo",
    ZodiacSign.LIBRA: "Libra",
    ZodiacSign.SCORPIO: "Scorpio",
    ZodiacSign.SAGITTARIUS: "Sagittarius",
    ZodiacSign.CAPRICORN: "Capricorn",
    ZodiacSign.AQUARIUS: "Aquarius",
    ZodiacSign.PISCES: "Pisces",
}

# Zodiac Elements
ZODIAC_ELEMENTS = {
    ZodiacSign.ARIES: "ates",
    ZodiacSign.TAURUS: "toprak",
    ZodiacSign.GEMINI: "hava",
    ZodiacSign.CANCER: "su",
    ZodiacSign.LEO: "ates",
    ZodiacSign.VIRGO: "toprak",
    ZodiacSign.LIBRA: "hava",
    ZodiacSign.SCORPIO: "su",
    ZodiacSign.SAGITTARIUS: "ates",
    ZodiacSign.CAPRICORN: "toprak",
    ZodiacSign.AQUARIUS: "hava",
    ZodiacSign.PISCES: "su",
}

# Zodiac Qualities (Modalities)
ZODIAC_QUALITIES = {
    ZodiacSign.ARIES: "oncu",
    ZodiacSign.TAURUS: "sabit",
    ZodiacSign.GEMINI: "degisken",
    ZodiacSign.CANCER: "oncu",
    ZodiacSign.LEO: "sabit",
    ZodiacSign.VIRGO: "degisken",
    ZodiacSign.LIBRA: "oncu",
    ZodiacSign.SCORPIO: "sabit",
    ZodiacSign.SAGITTARIUS: "degisken",
    ZodiacSign.CAPRICORN: "oncu",
    ZodiacSign.AQUARIUS: "sabit",
    ZodiacSign.PISCES: "degisken",
}

# Planet Rulerships - Classical system (7 planets)
PLANET_RULERSHIPS = {
    ZodiacSign.ARIES: Planet.MARS,
    ZodiacSign.TAURUS: Planet.VENUS,
    ZodiacSign.GEMINI: Planet.MERCURY,
    ZodiacSign.CANCER: Planet.MOON,
    ZodiacSign.LEO: Planet.SUN,
    ZodiacSign.VIRGO: Planet.MERCURY,
    ZodiacSign.LIBRA: Planet.VENUS,
    ZodiacSign.SCORPIO: Planet.MARS,  # Classical ruler (not Pluto)
    ZodiacSign.SAGITTARIUS: Planet.JUPITER,
    ZodiacSign.CAPRICORN: Planet.SATURN,
    ZodiacSign.AQUARIUS: Planet.SATURN,  # Classical ruler (not Uranus)
    ZodiacSign.PISCES: Planet.JUPITER,  # Classical ruler (not Neptune)
}

# Aspects
class AspectType(Enum):
    # Aspect types and their angles
    CONJUNCTION = 0
    SEMI_SEXTILE = 30
    SEMI_SQUARE = 45
    SEXTILE = 60
    QUINTILE = 72
    SQUARE = 90
    TRINE = 120
    SESQUIQUADRATE = 135
    BIQUINTILE = 144
    QUINCUNX = 150
    OPPOSITION = 180

ASPECT_NAMES = {
    AspectType.CONJUNCTION: "Kavuşum",
    AspectType.SEMI_SEXTILE: "Yarı Sekstil",
    AspectType.SEMI_SQUARE: "Yarım Kare",
    AspectType.SEXTILE: "Sekstil",
    AspectType.QUINTILE: "Beşlik",
    AspectType.SQUARE: "Kare",
    AspectType.TRINE: "Üçgen",
    AspectType.SESQUIQUADRATE: "Sesquikare",
    AspectType.BIQUINTILE: "Çift Beşlik",
    AspectType.QUINCUNX: "Birleşmeyen Açı",
    AspectType.OPPOSITION: "Karşıt",
}

ASPECT_SYMBOLS = {
    AspectType.CONJUNCTION: "☌",
    AspectType.SEMI_SEXTILE: "⚺",
    AspectType.SEMI_SQUARE: "∠",
    AspectType.SEXTILE: "⚹",
    AspectType.QUINTILE: "Q",
    AspectType.SQUARE: "□",
    AspectType.TRINE: "△",
    AspectType.SESQUIQUADRATE: "⚼",
    AspectType.BIQUINTILE: "bQ",
    AspectType.QUINCUNX: "⚻",
    AspectType.OPPOSITION: "☍",
}

# Aspect orbs (in degrees) - Default maximum orbs for each aspect type
ASPECT_ORBS = {
    AspectType.CONJUNCTION: 10.0,
    AspectType.SEMI_SEXTILE: 3.0,
    AspectType.SEMI_SQUARE: 3.0,
    AspectType.SEXTILE: 6.0,
    AspectType.QUINTILE: 2.0,
    AspectType.SQUARE: 10.0,
    AspectType.TRINE: 10.0,
    AspectType.SESQUIQUADRATE: 3.0,
    AspectType.BIQUINTILE: 2.0,
    AspectType.QUINCUNX: 3.0,
    AspectType.OPPOSITION: 10.0,
}

# Planet orbs (in degrees) - Each planet has its own orb value
# These are used to calculate the actual orb for an aspect between two planets
PLANET_ORBS = {
    Planet.SUN: 15.0,
    Planet.MOON: 12.0,
    Planet.MERCURY: 7.0,
    Planet.VENUS: 7.0,
    Planet.MARS: 8.0,
    Planet.JUPITER: 9.0,
    Planet.SATURN: 9.0,
    Planet.URANUS: 5.0,
    Planet.NEPTUNE: 5.0,
    Planet.PLUTO: 5.0,
    Planet.NORTH_NODE: 5.0,
    Planet.SOUTH_NODE: 5.0,
}

# Aspect nature (harmonious or challenging)
ASPECT_NATURE = {
    AspectType.CONJUNCTION: "notr",
    AspectType.SEMI_SEXTILE: "hafif",
    AspectType.SEMI_SQUARE: "hafif zorlayici",
    AspectType.SEXTILE: "uyumlu",
    AspectType.QUINTILE: "yaratici",
    AspectType.SQUARE: "zorlayici",
    AspectType.TRINE: "uyumlu",
    AspectType.SESQUIQUADRATE: "hafif zorlayici",
    AspectType.BIQUINTILE: "yaratici",
    AspectType.QUINCUNX: "karmasik",
    AspectType.OPPOSITION: "zorlayici",
}

# Transit-specific orbs (tighter than natal chart orbs)
TRANSIT_ORBS = {
    AspectType.CONJUNCTION: 3.0,
    AspectType.OPPOSITION:  3.0,
    AspectType.TRINE:       3.0,
    AspectType.SQUARE:      3.0,
    AspectType.SEXTILE:     3.0,
}

# House Systems
class HouseSystem(Enum):
    PLACIDUS = "P"
    KOCH = "K"
    EQUAL = "E"
    WHOLE_SIGN = "W"
    CAMPANUS = "C"
    REGIOMONTANUS = "R"

HOUSE_SYSTEM_NAMES = {
    HouseSystem.PLACIDUS: "Placidus",
    HouseSystem.KOCH: "Koch",
    HouseSystem.EQUAL: "Equal",
    HouseSystem.WHOLE_SIGN: "Whole Sign",
    HouseSystem.CAMPANUS: "Campanus",
    HouseSystem.REGIOMONTANUS: "Regiomontanus",
}

# House meanings
HOUSE_NAMES = {
    1: "1. Ev - Benlik ve Kisilik",
    2: "2. Ev - Degerler ve Maddi Durum",
    3: "3. Ev - Iletisim ve Ogrenim",
    4: "4. Ev - Ev ve Aile",
    5: "5. Ev - Yaraticilik ve Ask",
    6: "6. Ev - Saglik ve Calisma",
    7: "7. Ev - Iliskiler ve Ortakliklar",
    8: "8. Ev - Donusum ve Ortak Kaynaklar",
    9: "9. Ev - Felsefe ve Uzak Yolculuklar",
    10: "10. Ev - Kariyer ve Toplumsal Statu",
    11: "11. Ev - Arkadasliklar ve Hedefler",
    12: "12. Ev - Bilincalti ve Gizli Dusmanlar",
}

# Angles (Critical points in the chart)
class Angle(Enum):
    ASCENDANT = "ASC"
    MIDHEAVEN = "MC"
    DESCENDANT = "DSC"
    IMUM_COELI = "IC"

ANGLE_NAMES = {
    Angle.ASCENDANT: "Yukselen (ASC)",
    Angle.MIDHEAVEN: "Orta Gogu (MC)",
    Angle.DESCENDANT: "Inen (DSC)",
    Angle.IMUM_COELI: "Gok Alti (IC)",
}

# Dignity types
class Dignity(Enum):
    RULER = "ruler"
    EXALTED = "exalted"
    DETRIMENT = "detriment"
    FALL = "fall"
    NEUTRAL = "neutral"

# Planet dignities by sign
PLANET_DIGNITIES = {
    Planet.SUN: {
        ZodiacSign.LEO: Dignity.RULER,
        ZodiacSign.ARIES: Dignity.EXALTED,
        ZodiacSign.AQUARIUS: Dignity.DETRIMENT,
        ZodiacSign.LIBRA: Dignity.FALL,
    },
    Planet.MOON: {
        ZodiacSign.CANCER: Dignity.RULER,
        ZodiacSign.TAURUS: Dignity.EXALTED,
        ZodiacSign.CAPRICORN: Dignity.DETRIMENT,
        ZodiacSign.SCORPIO: Dignity.FALL,
    },
    Planet.MERCURY: {
        ZodiacSign.GEMINI: Dignity.RULER,
        ZodiacSign.VIRGO: Dignity.RULER,
        ZodiacSign.SAGITTARIUS: Dignity.DETRIMENT,
        ZodiacSign.PISCES: Dignity.DETRIMENT,
    },
    Planet.VENUS: {
        ZodiacSign.TAURUS: Dignity.RULER,
        ZodiacSign.LIBRA: Dignity.RULER,
        ZodiacSign.PISCES: Dignity.EXALTED,
        ZodiacSign.ARIES: Dignity.DETRIMENT,
        ZodiacSign.SCORPIO: Dignity.DETRIMENT,
        ZodiacSign.VIRGO: Dignity.FALL,
    },
    Planet.MARS: {
        ZodiacSign.ARIES: Dignity.RULER,
        ZodiacSign.SCORPIO: Dignity.RULER,
        ZodiacSign.CAPRICORN: Dignity.EXALTED,
        ZodiacSign.LIBRA: Dignity.DETRIMENT,
        ZodiacSign.TAURUS: Dignity.DETRIMENT,
        ZodiacSign.CANCER: Dignity.FALL,
    },
    Planet.JUPITER: {
        ZodiacSign.SAGITTARIUS: Dignity.RULER,
        ZodiacSign.PISCES: Dignity.RULER,
        ZodiacSign.CANCER: Dignity.EXALTED,
        ZodiacSign.GEMINI: Dignity.DETRIMENT,
        ZodiacSign.VIRGO: Dignity.DETRIMENT,
        ZodiacSign.CAPRICORN: Dignity.FALL,
    },
    Planet.SATURN: {
        ZodiacSign.CAPRICORN: Dignity.RULER,
        ZodiacSign.AQUARIUS: Dignity.RULER,
        ZodiacSign.LIBRA: Dignity.EXALTED,
        ZodiacSign.CANCER: Dignity.DETRIMENT,
        ZodiacSign.LEO: Dignity.DETRIMENT,
        ZodiacSign.ARIES: Dignity.FALL,
    },
    # Modern planets (Uranus, Neptune, Pluto) are not used in classical essential dignities
    # Keeping them neutral for compatibility but they won't appear in the essential dignities table
}

# Triplicities (Daytime and Nighttime rulers by element)
# Used for essential dignities calculation
TRIPLICITIES = {
    # Fire signs (Aries, Leo, Sagittarius)
    ZodiacSign.ARIES: {"day": Planet.SUN, "night": Planet.JUPITER},
    ZodiacSign.LEO: {"day": Planet.SUN, "night": Planet.JUPITER},
    ZodiacSign.SAGITTARIUS: {"day": Planet.SUN, "night": Planet.JUPITER},

    # Earth signs (Taurus, Virgo, Capricorn)
    ZodiacSign.TAURUS: {"day": Planet.VENUS, "night": Planet.MOON},
    ZodiacSign.VIRGO: {"day": Planet.VENUS, "night": Planet.MOON},
    ZodiacSign.CAPRICORN: {"day": Planet.VENUS, "night": Planet.MOON},

    # Air signs (Gemini, Libra, Aquarius)
    ZodiacSign.GEMINI: {"day": Planet.SATURN, "night": Planet.MERCURY},
    ZodiacSign.LIBRA: {"day": Planet.SATURN, "night": Planet.MERCURY},
    ZodiacSign.AQUARIUS: {"day": Planet.SATURN, "night": Planet.MERCURY},

    # Water signs (Cancer, Scorpio, Pisces)
    ZodiacSign.CANCER: {"day": Planet.VENUS, "night": Planet.MARS},
    ZodiacSign.SCORPIO: {"day": Planet.VENUS, "night": Planet.MARS},
    ZodiacSign.PISCES: {"day": Planet.VENUS, "night": Planet.MARS},
}

# Ptolemaic Terms (Bounds) - Classical essential dignities system
# Each sign divided into 5 unequal parts by planet
# Format: {sign: [(end_degree, planet), ...]}
PTOLEMAIC_TERMS = {
    ZodiacSign.ARIES: [(6, Planet.JUPITER), (12, Planet.VENUS), (20, Planet.MERCURY), (25, Planet.MARS), (30, Planet.SATURN)],
    ZodiacSign.TAURUS: [(8, Planet.VENUS), (14, Planet.MERCURY), (22, Planet.JUPITER), (27, Planet.SATURN), (30, Planet.MARS)],
    ZodiacSign.GEMINI: [(6, Planet.MERCURY), (12, Planet.JUPITER), (17, Planet.VENUS), (24, Planet.MARS), (30, Planet.SATURN)],
    ZodiacSign.CANCER: [(7, Planet.MARS), (13, Planet.VENUS), (19, Planet.MERCURY), (26, Planet.JUPITER), (30, Planet.SATURN)],
    ZodiacSign.LEO: [(6, Planet.JUPITER), (11, Planet.VENUS), (18, Planet.SATURN), (24, Planet.MERCURY), (30, Planet.MARS)],
    ZodiacSign.VIRGO: [(7, Planet.MERCURY), (17, Planet.VENUS), (21, Planet.JUPITER), (28, Planet.MARS), (30, Planet.SATURN)],
    ZodiacSign.LIBRA: [(6, Planet.SATURN), (14, Planet.MERCURY), (21, Planet.JUPITER), (28, Planet.VENUS), (30, Planet.MARS)],
    ZodiacSign.SCORPIO: [(7, Planet.MARS), (11, Planet.VENUS), (19, Planet.MERCURY), (24, Planet.JUPITER), (30, Planet.SATURN)],
    ZodiacSign.SAGITTARIUS: [(12, Planet.JUPITER), (17, Planet.VENUS), (21, Planet.MERCURY), (26, Planet.SATURN), (30, Planet.MARS)],
    ZodiacSign.CAPRICORN: [(7, Planet.MERCURY), (14, Planet.JUPITER), (22, Planet.VENUS), (26, Planet.SATURN), (30, Planet.MARS)],
    ZodiacSign.AQUARIUS: [(7, Planet.MERCURY), (13, Planet.VENUS), (20, Planet.JUPITER), (25, Planet.MARS), (30, Planet.SATURN)],
    ZodiacSign.PISCES: [(12, Planet.VENUS), (16, Planet.JUPITER), (19, Planet.MERCURY), (28, Planet.MARS), (30, Planet.SATURN)],
}

# Faces/Decans - Each sign divided into 3 equal parts (10° each)
# Format: {sign: [planet for 0-10°, planet for 10-20°, planet for 20-30°]}
FACES = {
    ZodiacSign.ARIES: [Planet.MARS, Planet.SUN, Planet.VENUS],
    ZodiacSign.TAURUS: [Planet.MERCURY, Planet.MOON, Planet.SATURN],
    ZodiacSign.GEMINI: [Planet.JUPITER, Planet.MARS, Planet.SUN],
    ZodiacSign.CANCER: [Planet.VENUS, Planet.MERCURY, Planet.MOON],
    ZodiacSign.LEO: [Planet.SATURN, Planet.JUPITER, Planet.MARS],
    ZodiacSign.VIRGO: [Planet.SUN, Planet.VENUS, Planet.MERCURY],
    ZodiacSign.LIBRA: [Planet.MOON, Planet.SATURN, Planet.JUPITER],
    ZodiacSign.SCORPIO: [Planet.MARS, Planet.SUN, Planet.VENUS],
    ZodiacSign.SAGITTARIUS: [Planet.MERCURY, Planet.MOON, Planet.SATURN],
    ZodiacSign.CAPRICORN: [Planet.JUPITER, Planet.MARS, Planet.SUN],
    ZodiacSign.AQUARIUS: [Planet.VENUS, Planet.MERCURY, Planet.MOON],
    ZodiacSign.PISCES: [Planet.SATURN, Planet.JUPITER, Planet.MARS],
}

def get_zodiac_sign(longitude: float) -> ZodiacSign:
    # Get zodiac sign from longitude
    sign_index = int(longitude / 30)
    return ZodiacSign(sign_index)

def get_degree_in_sign(longitude: float) -> float:
    # Get degree within the zodiac sign
    return longitude % 30

def get_planet_dignity(planet: Planet, sign: ZodiacSign) -> Dignity:
    # Get planet's dignity in a given sign
    if planet in PLANET_DIGNITIES:
        return PLANET_DIGNITIES[planet].get(sign, Dignity.NEUTRAL)
    return Dignity.NEUTRAL

def get_triplicity_lord(sign: ZodiacSign, is_day_chart: bool) -> Planet | None:
    """Get the triplicity lord for a sign based on day/night"""
    if sign in TRIPLICITIES:
        return TRIPLICITIES[sign]["day" if is_day_chart else "night"]
    return None

def get_term_lord(sign: ZodiacSign, degree: float) -> Planet | None:
    """Get the term (bound) lord for a specific degree in a sign (Ptolemaic system)"""
    if sign in PTOLEMAIC_TERMS:
        for end_degree, planet in PTOLEMAIC_TERMS[sign]:
            if degree < end_degree:
                return planet
    return None

def get_face_lord(sign: ZodiacSign, degree: float) -> Planet | None:
    """Get the face/decan lord for a specific degree in a sign"""
    if sign in FACES:
        face_index = int(degree / 10)  # 0-10° = index 0, 10-20° = index 1, 20-30° = index 2
        if 0 <= face_index < 3:
            return FACES[sign][face_index]
    return None

def calculate_aspect_angle(long1: float, long2: float) -> float:
    # Calculate the angle between two celestial bodies
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect(long1: float, long2: float, planet1: Planet = None, planet2: Planet = None) -> Tuple[AspectType | None, float]:
    """
    Determine if two planets form an aspect
    Returns: (AspectType, orb) or (None, angle) if no aspect

    If planet1 and planet2 are provided, uses their individual orbs.
    Otherwise uses default aspect orbs.
    """
    angle = calculate_aspect_angle(long1, long2)

    for aspect_type, aspect_angle in AspectType.__members__.items():
        aspect = AspectType[aspect_type]
        ideal_angle = aspect.value

        # Calculate maximum allowed orb
        if planet1 and planet2 and planet1 in PLANET_ORBS and planet2 in PLANET_ORBS:
            # Use planet-specific orbs: smaller of (planet1_orb + planet2_orb) or default aspect orb
            max_orb = min(
                (PLANET_ORBS[planet1] + PLANET_ORBS[planet2]) / 2,
                ASPECT_ORBS[aspect]
            )
        else:
            max_orb = ASPECT_ORBS[aspect]

        if abs(angle - ideal_angle) <= max_orb:
            actual_orb = abs(angle - ideal_angle)
            return aspect, actual_orb

    return None, angle
