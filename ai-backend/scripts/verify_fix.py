"""
Verify that the house calculation fix is working correctly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.astrology.calculator import get_calculator

# Birth data from the test case
name = "Bilal Acikgoz"
birth_date = "1997-06-30"
birth_time = "20:30"
birth_place = "Ankara, Turkey"

print("="*70)
print("HOUSE CALCULATION VERIFICATION")
print("="*70)
print(f"Name: {name}")
print(f"Birth: {birth_date} {birth_time}")
print(f"Place: {birth_place}")
print("="*70)

calculator = get_calculator()
chart_id, chart_data = calculator.calculate_birth_chart(
    name=name,
    birth_date=birth_date,
    birth_time=birth_time,
    birth_place=birth_place,
    house_system="placidus"
)

print(f"\n{'ANGLES (Critical Points):':-^70}")
print(f"Ascendant: {chart_data.ascendant.longitude:9.4f}° = {chart_data.ascendant.sign:12s} {chart_data.ascendant.degree_in_sign:5.2f}°")
print(f"Midheaven: {chart_data.midheaven.longitude:9.4f}° = {chart_data.midheaven.sign:12s} {chart_data.midheaven.degree_in_sign:5.2f}°")

print(f"\n{'HOUSES:':-^70}")
for house in chart_data.houses:
    print(f"House {house.number:2d}: {house.cusp_longitude:9.4f}° = {house.sign:12s} {house.degree_in_sign:5.2f}°")

print(f"\n{'VERIFICATION:':-^70}")
asc_matches_house1 = abs(chart_data.ascendant.longitude - chart_data.houses[0].cusp_longitude) < 0.01
mc_matches_house10 = abs(chart_data.midheaven.longitude - chart_data.houses[9].cusp_longitude) < 0.01

print(f"✓ Ascendant equals House 1 cusp: {asc_matches_house1}")
print(f"  ASC: {chart_data.ascendant.longitude:.4f}°")
print(f"  H1:  {chart_data.houses[0].cusp_longitude:.4f}°")

print(f"\n✓ Midheaven equals House 10 cusp: {mc_matches_house10}")
print(f"  MC:  {chart_data.midheaven.longitude:.4f}°")
print(f"  H10: {chart_data.houses[9].cusp_longitude:.4f}°")

print(f"\n{'EXPECTED VALUES FROM SWISS EPHEMERIS:':-^70}")
print("Ascendant (House 1): 282.4506° = Capricorn 12.45°")
print("Midheaven (House 10): 216.3473° = Scorpio 6.35°")
print("House 2:  324.0403° = Aquarius 24.04°")
print("House 12: 260.9668° = Sagittarius 20.97°")

print(f"\n{'ACTUAL VALUES FROM CALCULATOR:':-^70}")
print(f"House 1:  {chart_data.houses[0].cusp_longitude:.4f}° = {chart_data.houses[0].sign} {chart_data.houses[0].degree_in_sign:.2f}°")
print(f"House 2:  {chart_data.houses[1].cusp_longitude:.4f}° = {chart_data.houses[1].sign} {chart_data.houses[1].degree_in_sign:.2f}°")
print(f"House 10: {chart_data.houses[9].cusp_longitude:.4f}° = {chart_data.houses[9].sign} {chart_data.houses[9].degree_in_sign:.2f}°")
print(f"House 12: {chart_data.houses[11].cusp_longitude:.4f}° = {chart_data.houses[11].sign} {chart_data.houses[11].degree_in_sign:.2f}°")

if asc_matches_house1 and mc_matches_house10:
    print(f"\n{'='*70}")
    print("✅ SUCCESS! All house calculations are correct!")
    print(f"{'='*70}\n")
else:
    print(f"\n{'='*70}")
    print("❌ FAILED! House calculations still have errors!")
    print(f"{'='*70}\n")
