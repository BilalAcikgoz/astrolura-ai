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
    # CHIRON = swe.CHIRON  # Requires seas_18.se1 file

# Planet symbols and names
PLANET_SYMBOLS = {
    Planet.SUN: "Sun",
    Planet.MOON: "Moon",
    Planet.MERCURY: "Mercury",
    Planet.VENUS: "Venus",
    Planet.MARS: "Mars",
    Planet.JUPITER: "Jupiter",
    Planet.SATURN: "Saturn",
    Planet.URANUS: "Uranus",
    Planet.NEPTUNE: "Neptune",
    Planet.PLUTO: "Pluto",
    Planet.NORTH_NODE: "North Node",
    # Planet.CHIRON: "Chiron",
}

PLANET_NAMES = {
    Planet.SUN: "Gunes",
    Planet.MOON: "Ay",
    Planet.MERCURY: "Merkur",
    Planet.VENUS: "Venus",
    Planet.MARS: "Mars",
    Planet.JUPITER: "Jupiter",
    Planet.SATURN: "Saturn",
    Planet.URANUS: "Uranus",
    Planet.NEPTUNE: "Neptun",
    Planet.PLUTO: "Pluto",
    Planet.NORTH_NODE: "Kuzey Node",
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
    ZodiacSign.ARIES: "Koc",
    ZodiacSign.TAURUS: "Boga",
    ZodiacSign.GEMINI: "Ikizler",
    ZodiacSign.CANCER: "Yengec",
    ZodiacSign.LEO: "Aslan",
    ZodiacSign.VIRGO: "Basak",
    ZodiacSign.LIBRA: "Terazi",
    ZodiacSign.SCORPIO: "Akrep",
    ZodiacSign.SAGITTARIUS: "Yay",
    ZodiacSign.CAPRICORN: "Oglak",
    ZodiacSign.AQUARIUS: "Kova",
    ZodiacSign.PISCES: "Balik",
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

# Planet Rulerships
PLANET_RULERSHIPS = {
    ZodiacSign.ARIES: Planet.MARS,
    ZodiacSign.TAURUS: Planet.VENUS,
    ZodiacSign.GEMINI: Planet.MERCURY,
    ZodiacSign.CANCER: Planet.MOON,
    ZodiacSign.LEO: Planet.SUN,
    ZodiacSign.VIRGO: Planet.MERCURY,
    ZodiacSign.LIBRA: Planet.VENUS,
    ZodiacSign.SCORPIO: Planet.PLUTO,
    ZodiacSign.SAGITTARIUS: Planet.JUPITER,
    ZodiacSign.CAPRICORN: Planet.SATURN,
    ZodiacSign.AQUARIUS: Planet.URANUS,
    ZodiacSign.PISCES: Planet.NEPTUNE,
}

# Aspects
class AspectType(Enum):
    # Aspect types and their angles
    CONJUNCTION = 0
    OPPOSITION = 180
    TRINE = 120
    SQUARE = 90
    SEXTILE = 60
    QUINCUNX = 150
    SEMI_SEXTILE = 30
    SEMI_SQUARE = 45
    SESQUIQUADRATE = 135

ASPECT_NAMES = {
    AspectType.CONJUNCTION: "Kavusum",
    AspectType.OPPOSITION: "Karsitlik",
    AspectType.TRINE: "Ucgen",
    AspectType.SQUARE: "Kare",
    AspectType.SEXTILE: "Altigen",
    AspectType.QUINCUNX: "Quincunx",
    AspectType.SEMI_SEXTILE: "Yari Altigen",
    AspectType.SEMI_SQUARE: "Yari Kare",
    AspectType.SESQUIQUADRATE: "Sesquiquadrate",
}

ASPECT_SYMBOLS = {
    AspectType.CONJUNCTION: "Conjunction",
    AspectType.OPPOSITION: "Opposition",
    AspectType.TRINE: "Trine",
    AspectType.SQUARE: "Square",
    AspectType.SEXTILE: "Sextile",
    AspectType.QUINCUNX: "Quincunx",
}

# Aspect orbs (in degrees)
ASPECT_ORBS = {
    AspectType.CONJUNCTION: 8.0,
    AspectType.OPPOSITION: 8.0,
    AspectType.TRINE: 8.0,
    AspectType.SQUARE: 7.0,
    AspectType.SEXTILE: 6.0,
    AspectType.QUINCUNX: 3.0,
    AspectType.SEMI_SEXTILE: 2.0,
    AspectType.SEMI_SQUARE: 2.0,
    AspectType.SESQUIQUADRATE: 2.0,
}

# Aspect nature (harmonious or challenging)
ASPECT_NATURE = {
    AspectType.CONJUNCTION: "notr",
    AspectType.OPPOSITION: "zorlayici",
    AspectType.TRINE: "uyumlu",
    AspectType.SQUARE: "zorlayici",
    AspectType.SEXTILE: "uyumlu",
    AspectType.QUINCUNX: "karmasik",
    AspectType.SEMI_SEXTILE: "hafif",
    AspectType.SEMI_SQUARE: "hafif zorlayici",
    AspectType.SESQUIQUADRATE: "hafif zorlayici",
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
        ZodiacSign.AQUARIUS: Dignity.EXALTED,
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
    Planet.URANUS: {
        ZodiacSign.AQUARIUS: Dignity.RULER,
        ZodiacSign.SCORPIO: Dignity.EXALTED,
        ZodiacSign.LEO: Dignity.DETRIMENT,
        ZodiacSign.TAURUS: Dignity.FALL,
    },
    Planet.NEPTUNE: {
        ZodiacSign.PISCES: Dignity.RULER,
        ZodiacSign.LEO: Dignity.EXALTED,
        ZodiacSign.VIRGO: Dignity.DETRIMENT,
        ZodiacSign.AQUARIUS: Dignity.FALL,
    },
    Planet.PLUTO: {
        ZodiacSign.SCORPIO: Dignity.RULER,
        ZodiacSign.LEO: Dignity.EXALTED,
        ZodiacSign.TAURUS: Dignity.DETRIMENT,
        ZodiacSign.AQUARIUS: Dignity.FALL,
    },
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

def calculate_aspect_angle(long1: float, long2: float) -> float:
    # Calculate the angle between two celestial bodies
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect(long1: float, long2: float) -> Tuple[AspectType | None, float]:
    """
    Determine if two planets form an aspect
    Returns: (AspectType, orb) or (None, angle) if no aspect
    """
    angle = calculate_aspect_angle(long1, long2)

    for aspect_type, aspect_angle in AspectType.__members__.items():
        aspect = AspectType[aspect_type]
        ideal_angle = aspect.value
        orb = ASPECT_ORBS[aspect]

        if abs(angle - ideal_angle) <= orb:
            actual_orb = abs(angle - ideal_angle)
            return aspect, actual_orb

    return None, angle
