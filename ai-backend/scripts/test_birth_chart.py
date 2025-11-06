"""
Test Birth Chart Calculation

Simple script to test the birth chart calculator functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.astrology.calculator import get_calculator
from app.config import get_settings
import json
from datetime import datetime

def test_birth_chart():
    """Test birth chart calculation with sample data"""

    settings = get_settings()
    print(f"Astro-Fala Birth Chart Calculator Test")
    print(f"Environment: {settings.environment}")
    print("="*60)

    # Sample data
    test_cases = [
        {
            "name": "Test User 1",
            "birth_date": "1990-07-15",
            "birth_time": "14:30",
            "birth_place": "Istanbul, Turkey",
            "house_system": "placidus"
        },
        {
            "name": "Test User 2",
            "birth_date": "1995-03-21",
            "birth_time": "08:45",
            "birth_place": "Ankara, Turkey",
            "house_system": "placidus"
        }
    ]

    calculator = get_calculator()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")

        try:
            # Calculate chart
            chart_id, chart_data = calculator.calculate_birth_chart(**test_case)

            print(f"\n✓ Chart calculated successfully!")
            print(f"  Chart ID: {chart_id}")
            print(f"\n  Birth Info:")
            print(f"    Date: {chart_data.chart_info.birth_date}")
            print(f"    Time: {chart_data.chart_info.birth_time}")
            print(f"    Location: {chart_data.chart_info.location.city}, {chart_data.chart_info.location.country}")
            print(f"    Coordinates: {chart_data.chart_info.location.latitude}°N, {chart_data.chart_info.location.longitude}°E")
            print(f"    Timezone: {chart_data.chart_info.location.timezone}")

            print(f"\n  Angles:")
            print(f"    Ascendant: {chart_data.ascendant.sign} {chart_data.ascendant.degree_in_sign:.2f}°")
            print(f"    Midheaven: {chart_data.midheaven.sign} {chart_data.midheaven.degree_in_sign:.2f}°")

            print(f"\n  Planets:")
            for planet in chart_data.planets[:10]:  # Show main planets
                retro = " ℞" if planet.retrograde else ""
                print(f"    {planet.symbol} {planet.name:10s}: {planet.sign:10s} {planet.degree_in_sign:5.2f}° (House {planet.house}){retro}")

            print(f"\n  Elements:")
            print(f"    Fire:  {chart_data.elements.fire:5.1f}%")
            print(f"    Earth: {chart_data.elements.earth:5.1f}%")
            print(f"    Air:   {chart_data.elements.air:5.1f}%")
            print(f"    Water: {chart_data.elements.water:5.1f}%")

            print(f"\n  Qualities:")
            print(f"    Cardinal: {chart_data.qualities.cardinal:5.1f}%")
            print(f"    Fixed:    {chart_data.qualities.fixed:5.1f}%")
            print(f"    Mutable:  {chart_data.qualities.mutable:5.1f}%")

            print(f"\n  Aspects: {len(chart_data.aspects)} aspects found")
            # Show first 5 aspects
            for aspect in chart_data.aspects[:5]:
                print(f"    {aspect.planet1} {aspect.aspect_symbol} {aspect.planet2}: {aspect.aspect} (orb: {aspect.orb:.2f}°)")

            if len(chart_data.aspects) > 5:
                print(f"    ... and {len(chart_data.aspects) - 5} more")

        except Exception as e:
            print(f"\n✗ Error calculating chart: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("Test completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_birth_chart()
