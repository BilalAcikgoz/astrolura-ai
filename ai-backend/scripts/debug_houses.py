"""
Debug script to inspect Swiss Ephemeris house calculation output
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import swisseph as swe
from datetime import datetime
from app.config import get_settings

settings = get_settings()
swe.set_ephe_path(settings.ephe_path)

# Birth data from the test case
birth_date = "1997-06-30"
birth_time = "20:30"
latitude = 39.716044
longitude = 32.705995

# Convert to UTC (Turkey = UTC+3 in summer)
utc_hour = 20.5 - 3.0  # 17.5 = 17:30 UTC

# Calculate Julian Day
jd = swe.julday(1997, 6, 30, utc_hour)

print("="*70)
print("SWISS EPHEMERIS HOUSE CALCULATION DEBUG")
print("="*70)
print(f"Birth Date: {birth_date} {birth_time} (local)")
print(f"UTC Time: 1997-06-30 17:30:00")
print(f"Location: Ankara ({latitude}°N, {longitude}°E)")
print(f"Julian Day: {jd}")
print(f"House System: Placidus (P)")
print("="*70)

# Calculate houses with Placidus system
result = swe.houses(jd, latitude, longitude, b'P')
cusps = result[0]
ascmc = result[1]

print(f"\n{'='*70}")
print("RAW OUTPUT FROM swe.houses()")
print(f"{'='*70}")
print(f"len(cusps): {len(cusps)}")
print(f"len(ascmc): {len(ascmc)}")

print(f"\n{'CUSPS ARRAY:':-^70}")
for i in range(len(cusps)):
    degree_in_sign = cusps[i] % 30
    sign_index = int(cusps[i] / 30)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sign_name = signs[sign_index] if 0 <= sign_index < 12 else "Unknown"
    print(f"cusps[{i:2d}] = {cusps[i]:9.4f}° = {sign_name:12s} {degree_in_sign:5.2f}°")

print(f"\n{'ASCMC ARRAY:':-^70}")
ascmc_labels = [
    "Ascendant (ASC)",
    "Midheaven (MC)",
    "ARMC",
    "Vertex",
    "Equatorial Ascendant",
    "Co-Ascendant (Koch)",
    "Co-Ascendant (Porphyry)",
    "Polar Ascendant"
]
for i in range(len(ascmc)):
    degree_in_sign = ascmc[i] % 30
    sign_index = int(ascmc[i] / 30)
    sign_name = signs[sign_index] if 0 <= sign_index < 12 else "Unknown"
    label = ascmc_labels[i] if i < len(ascmc_labels) else f"ascmc[{i}]"
    print(f"ascmc[{i}] = {ascmc[i]:9.4f}° = {sign_name:12s} {degree_in_sign:5.2f}° <- {label}")

print(f"\n{'VERIFICATION:':-^70}")
print(f"cusps[1] should equal ascmc[0]:")
print(f"  cusps[1]  = {cusps[1]:9.4f}°")
print(f"  ascmc[0]  = {ascmc[0]:9.4f}°")
print(f"  Match? {abs(cusps[1] - ascmc[0]) < 0.01}")

print(f"\ncusps[10] should equal ascmc[1]:")
print(f"  cusps[10] = {cusps[10]:9.4f}°")
print(f"  ascmc[1]  = {ascmc[1]:9.4f}°")
print(f"  Match? {abs(cusps[10] - ascmc[1]) < 0.01}")

# Calculate Sun position for reference
sun_result = swe.calc_ut(jd, 0)
sun_long = sun_result[0][0]
print(f"\n{'SUN POSITION (for reference):':-^70}")
print(f"Sun longitude: {sun_long:.4f}° = Cancer {sun_long % 30:.2f}°")

print(f"\n{'='*70}")
print("END DEBUG")
print(f"{'='*70}\n")
