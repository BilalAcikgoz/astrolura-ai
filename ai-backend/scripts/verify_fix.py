import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.astrology.calculator import get_calculator
import json

def test_specific_profile():    
    print("="*70)
    print("ASTRO-FALA BIRTH CHART - VERIFICATION TEST")
    print("="*70)
    
    # Test profile data
    name = "Beyza Seren Açıkgöz"
    birth_date = "1999-07-31"
    birth_time = "23:10"
    birth_place = "Düzce, Turkey"
    
    print(f"\nBirth Data:")
    print(f"  Name: {name}")
    print(f"  Date: {birth_date}")
    print(f"  Time: {birth_time}")
    print(f"  Place: {birth_place}")
    print("="*70)
    
    # Calculate birth chart
    print("\nCalculating birth chart...")
    calculator = get_calculator()
    
    try:
        chart_id, chart_data = calculator.calculate_birth_chart(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            house_system="placidus"
        )
        
        print(f"✓ Chart calculated successfully (ID: {chart_id})")
        
        # 1. Check planets and angles
        print(f"\n{'PLANETS & ANGLES:':-^70}")
        for planet in chart_data.planets:
            retro = " ℞" if planet.retrograde else ""
            print(f"{planet.symbol:8s} {planet.name:12s}: {planet.sign:10s} {planet.degree_display:8s} "
                  f"(House {planet.house:2d}) Speed: {planet.speed_display}{retro}")
        
        # Verify South Node speed
        south_node = next((p for p in chart_data.planets if p.name == "Guney Node"), None)
        if south_node:
            print(f"\n✓ South Node speed display: {south_node.speed_display}")
            if south_node.speed_display == "00°00'00\"":
                print("  ✗ ERROR: South Node speed should not be zero!")
        
        # 2. Check houses
        print(f"\n{'HOUSES:':-^70}")
        for house in chart_data.houses[:6]:  # Show first 6 houses
            print(f"House {house.number:2d}: {house.sign:10s} {house.degree_display:8s}")
        print("...")
        
        # 3. Check aspects count
        print(f"\n{'ASPECTS:':-^70}")
        print(f"Total aspects: {len(chart_data.aspects)}")
        
        # Group aspects by type
        aspect_counts = {}
        for aspect in chart_data.aspects:
            aspect_type = aspect.aspect_en
            aspect_counts[aspect_type] = aspect_counts.get(aspect_type, 0) + 1
        
        print("\nAspect distribution:")
        for aspect_type, count in sorted(aspect_counts.items()):
            print(f"  {aspect_type:15s}: {count}")
        
        # Show sample aspects
        print("\nSample aspects (first 5):")
        for aspect in chart_data.aspects[:5]:
            print(f"  {aspect.planet1:10s} {aspect.aspect_symbol:15s} {aspect.planet2:10s} "
                  f"(orb: {aspect.orb:.2f}°)")
        
        # 4. Check elements
        print(f"\n{'ELEMENTS:':-^70}")
        elements = chart_data.elements
        print(f"  Fire:  {elements.fire:5.1f}%")
        print(f"  Earth: {elements.earth:5.1f}%")
        print(f"  Air:   {elements.air:5.1f}%")
        print(f"  Water: {elements.water:5.1f}%")
        total = elements.fire + elements.earth + elements.air + elements.water
        print(f"  Total: {total:5.1f}%")
        
        # Verify expected values
        expected_elements = {"fire": 40.0, "earth": 26.7, "air": 0.0, "water": 33.3}
        matches = True
        for element, expected in expected_elements.items():
            actual = getattr(elements, element)
            if abs(actual - expected) > 1.0:
                print(f"  ✗ {element.title()} mismatch: expected {expected}%, got {actual}%")
                matches = False
        if matches:
            print("  ✓ Element distribution correct!")
        
        # 5. Check qualities
        print(f"\n{'QUALITIES:':-^70}")
        qualities = chart_data.qualities
        print(f"  Cardinal: {qualities.cardinal:5.1f}%")
        print(f"  Fixed:    {qualities.fixed:5.1f}%")
        print(f"  Mutable:  {qualities.mutable:5.1f}%")
        total = qualities.cardinal + qualities.fixed + qualities.mutable
        print(f"  Total:    {total:5.1f}%")
        
        expected_qualities = {"cardinal": 33.3, "fixed": 40.0, "mutable": 26.7}
        matches = True
        for quality, expected in expected_qualities.items():
            actual = getattr(qualities, quality)
            if abs(actual - expected) > 1.0:
                print(f"  ✗ {quality.title()} mismatch: expected {expected}%, got {actual}%")
                matches = False
        if matches:
            print("  ✓ Quality distribution correct!")
        
        # 6. Check dignities (asaletler)
        print(f"\n{'DIGNITIES (ASALETLER):':-^70}")
        if hasattr(chart_data, 'dignities') and chart_data.dignities:
            print(f"Total dignities: {len(chart_data.dignities)}")
            print("\nPlanetary dignities:")
            for dignity in chart_data.dignities:
                status = dignity.current_dignity if dignity.current_dignity != "-" else "Neutral"
                print(f"  {dignity.planet_symbol} {dignity.planet:10s} in {dignity.current_sign:10s}: {status}")
                if dignity.ruler:
                    print(f"    → Rules: {dignity.ruler}")
                if dignity.exalted:
                    print(f"    → Exalted in: {dignity.exalted}")
                if dignity.detriment:
                    print(f"    → Detriment in: {dignity.detriment}")
                if dignity.fall:
                    print(f"    → Fall in: {dignity.fall}")
            print("  ✓ Dignities table added successfully!")
        else:
            print("  ✗ ERROR: Dignities table not found!")
        
        # Summary
        print(f"\n{'='*70}")
        print("VERIFICATION SUMMARY:")
        print(f"{'='*70}")
        print(f"✓ Birth chart calculation: SUCCESS")
        print(f"✓ Planets count: {len([p for p in chart_data.planets if p.name not in ['Yukselen', 'Orta Gogu', 'Inen', 'Gok Alti']])} planets")
        print(f"✓ Houses count: {len(chart_data.houses)} houses")
        print(f"✓ Aspects count: {len(chart_data.aspects)} aspects (filtered)")
        print(f"✓ Dignities count: {len(chart_data.dignities) if hasattr(chart_data, 'dignities') else 0} planets")
        print(f"{'='*70}\n")
        
        # Export to JSON for inspection
        output_file = Path(__file__).parent / f"test_chart_{chart_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chart_data.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Chart data exported to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error calculating chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_profile()
    sys.exit(0 if success else 1)
