# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class BirthChartRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Bilal Acikgoz",
                "birth_date": "1997-06-30",
                "birth_time": "20:28",
                "birth_place": "Ankara, Turkey",
                "house_system": "placidus",
            }
        }
    )

    name: str = Field(..., min_length=2, max_length=100, description="Full name of the person")
    birth_date: str = Field(
        ..., description="Birth date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    birth_time: str = Field(
        ..., description="Birth time in HH:MM format (24-hour)", pattern=r"^\d{2}:\d{2}$"
    )
    birth_place: str = Field(
        ..., min_length=2, max_length=200, description="Birth place (city, country)"
    )
    house_system: Optional[str] = Field(
        default="placidus",
        description="House system to use (placidus, koch, equal, whole_sign)",
    )

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValueError("Birth date cannot be in the future")
            if parsed_date.year < 1800 or parsed_date.year > 2100:
                raise ValueError("Birth year must be between 1800 and 2100")
            return v
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Birth date must be in YYYY-MM-DD format")
            raise

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23):
                raise ValueError("Hour must be between 00 and 23")
            if not (0 <= minute <= 59):
                raise ValueError("Minute must be between 00 and 59")
            return v
        except ValueError as e:
            if "not enough values to unpack" in str(e) or "invalid literal" in str(e):
                raise ValueError("Birth time must be in HH:MM format")
            raise

    @field_validator("house_system")
    @classmethod
    def validate_house_system(cls, v: Optional[str]) -> str:
        if v is None:
            return "placidus"
        valid_systems = ["placidus", "koch", "equal", "whole_sign", "campanus", "regiomontanus"]
        v_lower = v.lower()
        if v_lower not in valid_systems:
            raise ValueError(
                f"Invalid house system. Must be one of: {', '.join(valid_systems)}"
            )
        return v_lower


class TransitRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chart_id": "550e8400-e29b-41d4-a716-446655440000",
                "transit_date": "2026-03-24",
                "transit_time": "15:31",
            }
        }
    )

    chart_id: str = Field(..., description="UUID of the natal birth chart")
    transit_date: Optional[str] = Field(
        default=None,
        description="Transit date in YYYY-MM-DD format (defaults to today)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    transit_time: Optional[str] = Field(
        default=None,
        description="Transit time in HH:MM format, local time (defaults to 12:00)",
        pattern=r"^\d{2}:\d{2}$",
    )

    @field_validator("transit_date", mode="before")
    @classmethod
    def default_transit_date(cls, v: Optional[str]) -> str:
        if v is None:
            return date.today().isoformat()
        return v

    @field_validator("transit_time")
    @classmethod
    def validate_transit_time(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23):
                raise ValueError("Hour must be between 00 and 23")
            if not (0 <= minute <= 59):
                raise ValueError("Minute must be between 00 and 59")
            return v
        except ValueError as e:
            if "not enough values to unpack" in str(e) or "invalid literal" in str(e):
                raise ValueError("Transit time must be in HH:MM format")
            raise


class TransitInterpretRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transit_id": "550e8400-e29b-41d4-a716-446655440001",
                "language": "tr",
            }
        }
    )

    transit_id: str = Field(..., description="UUID of the calculated transit chart")
    language: Optional[str] = Field(default="tr", description="Language code (tr, en)")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> str:
        if v is None:
            return "tr"
        v_lower = v.lower()
        if v_lower not in ["tr", "en"]:
            raise ValueError("Invalid language. Must be one of: tr, en")
        return v_lower


class BirthChartInterpretRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chart_id": "550e8400-e29b-41d4-a716-446655440000",
                "interpretation_style": "detailed",
                "language": "tr",
            }
        }
    )

    chart_id: str = Field(..., description="UUID of the calculated birth chart")
    interpretation_style: Optional[str] = Field(
        default="detailed",
        description="Style of interpretation (brief, detailed, comprehensive)",
    )
    language: Optional[str] = Field(
        default="tr", description="Language code for interpretation (tr, en)"
    )

    @field_validator("interpretation_style")
    @classmethod
    def validate_interpretation_style(cls, v: Optional[str]) -> str:
        if v is None:
            return "detailed"
        valid_styles = ["brief", "detailed", "comprehensive"]
        v_lower = v.lower()
        if v_lower not in valid_styles:
            raise ValueError(
                f"Invalid interpretation style. Must be one of: {', '.join(valid_styles)}"
            )
        return v_lower

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> str:
        if v is None:
            return "tr"
        valid_languages = ["tr", "en"]
        v_lower = v.lower()
        if v_lower not in valid_languages:
            raise ValueError(
                f"Invalid language. Must be one of: {', '.join(valid_languages)}"
            )
        return v_lower
