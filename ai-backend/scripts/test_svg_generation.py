"""
Test SVG Birth Chart Generation

Tests the SVG chart generator with real birth chart data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.astrology.calculator import get_calculator
from app.core.visualization import generate_birth_chart_svg

def test_svg_generation():
    """Test SVG generation with sample birth data"""

    print("="*70)
    print("SVG BIRTH CHART GENERATION TEST")
    print("="*70)

    # Sample birth data
    name = "Bilal Acikgoz"
    birth_date = "1997-06-30"
    birth_time = "20:30"
    birth_place = "Ankara, Turkey"

    print(f"\nBirth Data:")
    print(f"  Name: {name}")
    print(f"  Date: {birth_date}")
    print(f"  Time: {birth_time}")
    print(f"  Place: {birth_place}")
    print("="*70)

    # Calculate birth chart
    print("\n[1/3] Calculating birth chart...")
    calculator = get_calculator()
    chart_id, chart_data = calculator.calculate_birth_chart(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        house_system="placidus"
    )
    print(f"  ✓ Chart calculated successfully (ID: {chart_id})")

    # Generate SVG
    print("\n[2/3] Generating SVG chart...")
    try:
        svg_content = generate_birth_chart_svg(chart_data, language="en")
        print(f"  ✓ SVG generated successfully")
        print(f"  ✓ SVG size: {len(svg_content):,} bytes")

        # Check SVG content
        if "<svg" in svg_content and "</svg>" in svg_content:
            print(f"  ✓ Valid SVG structure")
        else:
            print(f"  ✗ Invalid SVG structure")
            return False

    except Exception as e:
        print(f"  ✗ Error generating SVG: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Save SVG to file
    print("\n[3/3] Saving SVG to file...")
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"birth_chart_{chart_id}.svg"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"  ✓ SVG saved to: {output_file}")

    # Summary
    print("\n" + "="*70)
    print("✅ TEST PASSED!")
    print("="*70)
    print(f"\nChart Elements:")
    print(f"  • Planets: {len(chart_data.planets)}")
    print(f"  • Houses: {len(chart_data.houses)}")
    print(f"  • Aspects: {len(chart_data.aspects)}")
    print(f"  • Ascendant: {chart_data.ascendant.sign} {chart_data.ascendant.degree_in_sign:.2f}°")
    print(f"  • Midheaven: {chart_data.midheaven.sign} {chart_data.midheaven.degree_in_sign:.2f}°")
    print(f"\nYou can open the SVG file in a web browser to view the chart:")
    print(f"  file://{output_file.absolute()}")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    success = test_svg_generation()
    sys.exit(0 if success else 1)
