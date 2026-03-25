from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class LocationInfo(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    timezone: str


class PlanetPosition(BaseModel):
    name: str = Field(..., description="Planet name in Turkish")
    name_en: str = Field(..., description="Planet name in English")
    symbol: str = Field(..., description="Planet symbol")
    longitude: float = Field(..., description="Ecliptic longitude in degrees")
    latitude: float = Field(..., description="Ecliptic latitude in degrees")
    distance: float = Field(..., description="Distance from Earth in AU")
    speed: float = Field(..., description="Daily motion in degrees")
    speed_display: str = Field(..., description="Formatted speed display (e.g., 00°57'13\")")
    sign: str = Field(..., description="Zodiac sign in Turkish")
    sign_en: str = Field(..., description="Zodiac sign in English")
    sign_symbol: str = Field(..., description="Zodiac sign symbol")
    degree_in_sign: float = Field(..., description="Degree within the sign (0-30)")
    degree_display: str = Field(..., description="Formatted degree display (e.g., 8°57')")
    house: int = Field(..., description="House number (1-12)")
    retrograde: bool = Field(..., description="Is planet retrograde?")
    dignity: str = Field(..., description="Planet dignity (ruler, exalted, detriment, fall, neutral)")


class HouseInfo(BaseModel):
    number: int = Field(..., description="House number (1-12)")
    name: str = Field(..., description="House name and meaning in Turkish")
    cusp_longitude: float = Field(..., description="House cusp longitude in degrees")
    sign: str = Field(..., description="Sign on the house cusp in Turkish")
    sign_en: str = Field(..., description="Sign on the house cusp in English")
    sign_symbol: str = Field(..., description="Sign symbol")
    degree_in_sign: float = Field(..., description="Degree of cusp within the sign")
    degree_display: str = Field(..., description="Formatted degree display (e.g., 8°57')")


class AspectInfo(BaseModel):
    planet1: str = Field(..., description="First planet name")
    aspect: str = Field(..., description="Aspect type in Turkish")
    aspect_en: str = Field(..., description="Aspect type in English")
    aspect_symbol: str = Field(..., description="Aspect symbol")
    planet2: str = Field(..., description="Second planet name")
    orb: float = Field(..., description="Orb (difference from exact aspect)")
    angle: float = Field(..., description="Exact aspect angle (e.g., 180 for opposition)")
    nature: str = Field(..., description="Aspect nature (harmonious, challenging, neutral)")


class ElementBalance(BaseModel):
    fire: float = Field(..., description="Fire element percentage")
    earth: float = Field(..., description="Earth element percentage")
    air: float = Field(..., description="Air element percentage")
    water: float = Field(..., description="Water element percentage")


class QualityBalance(BaseModel):
    cardinal: float = Field(..., description="Cardinal quality percentage")
    fixed: float = Field(..., description="Fixed quality percentage")
    mutable: float = Field(..., description="Mutable quality percentage")


class EssentialDignityRow(BaseModel):
    planet: str = Field(..., description="Planet name")
    planet_en: str = Field(..., description="Planet name in English")
    ruler: List[str] = Field(default_factory=list, description="Planets this planet rules")
    exaltation: List[str] = Field(default_factory=list, description="Planets this planet exalts")
    triplicity: List[str] = Field(default_factory=list, description="Planets in this planet's triplicity")
    term: List[str] = Field(default_factory=list, description="Planets in this planet's term")
    face: List[str] = Field(default_factory=list, description="Planets in this planet's face/decan")
    detriment: List[str] = Field(default_factory=list, description="Planets this planet is detriment to")
    fall: List[str] = Field(default_factory=list, description="Planets this planet is fall to")
    score: int = Field(..., description="Total essential dignity score")


class EssentialDignitiesTable(BaseModel):
    rows: List[EssentialDignityRow] = Field(..., description="Rows for each planet")
    total_score: int = Field(..., description="Sum of all planet scores")


class ChartInfo(BaseModel):
    name: str
    birth_date: str
    birth_time: str
    birth_datetime_local: str
    birth_datetime_utc: str
    location: LocationInfo
    house_system: str
    julian_day: float


class BirthChartData(BaseModel):
    chart_info: ChartInfo
    planets: List[PlanetPosition]
    houses: List[HouseInfo]
    aspects: List[AspectInfo]
    elements: ElementBalance
    qualities: QualityBalance
    dignities: EssentialDignitiesTable


class BirthChartResponse(BaseModel):
    success: bool = True
    chart_id: str = Field(..., description="Unique identifier for this chart")
    chart_data: BirthChartData
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterpretationResponse(BaseModel):
    success: bool = True
    chart_id: str
    interpretation: str = Field(..., description="Full interpretation in Markdown format")
    interpretation_style: str
    language: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransitPlanet(BaseModel):
    name_tr: str
    name_en: str
    symbol: str
    sign_tr: str
    sign_en: str
    degree_display: str
    speed: float
    speed_display: str
    retrograde: bool
    house: int


class TransitAspect(BaseModel):
    transit_planet_tr: str
    transit_planet_en: str
    natal_planet_tr: str
    natal_planet_en: str
    aspect_tr: str
    aspect_en: str
    aspect_symbol: str
    angle: float
    orb: float
    applying: bool
    nature: str


class TransitChartResponse(BaseModel):
    success: bool = True
    transit_id: str
    natal_chart_id: str
    transit_date: str
    transit_time: Optional[str] = None
    transit_planets: List[TransitPlanet]
    transit_aspects: List[TransitAspect]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransitInterpretationResponse(BaseModel):
    success: bool = True
    transit_id: str
    natal_chart_id: str
    transit_date: str
    interpretation: str
    language: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorResponse(BaseModel):
    success: bool = False
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    rag_status: Optional[str] = Field(default=None, description="RAG pipeline connection status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
